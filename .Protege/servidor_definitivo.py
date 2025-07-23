#!/usr/bin/env python3
"""
Servidor SISAGENT Definitivo
Solución completa para el sistema de operaciones bancarias
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pytz
import os
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sisagent-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_definitivo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar CORS para permitir peticiones desde el frontend
CORS(app, origins=['http://127.0.0.1:5000', 'http://localhost:5000', 'http://127.0.0.1:5002', 'http://localhost:5002'])

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuración de zona horaria
tz = pytz.timezone('America/Lima')

# Modelos de base de datos
class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(tz))
    usuarios = db.relationship('Usuario', backref='sucursal', lazy=True)

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre_completo = db.Column(db.String(200), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(tz))
    operaciones = db.relationship('Operacion', backref='usuario', lazy=True)

class Operacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=False)
    medio = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now(tz))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now(tz))

class ComisionDiaria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    total_comisiones = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now(tz))

class ComisionMensual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    total_comisiones = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.now(tz))

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas principales
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password) and user.activo:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales inválidas o usuario inactivo', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/operaciones')
@login_required
def operaciones():
    # Obtener operaciones según el rol del usuario
    if current_user.es_admin:
        operaciones_list = Operacion.query.filter_by(activo=True).order_by(Operacion.fecha.desc()).all()
    else:
        operaciones_list = Operacion.query.filter_by(usuario_id=current_user.id, activo=True).order_by(Operacion.fecha.desc()).all()
    
    return render_template('operaciones.html', operaciones=operaciones_list)

# API para actualizar operaciones
@app.route('/api/operaciones/<int:operacion_id>', methods=['PUT'])
@login_required
def actualizar_operacion(operacion_id):
    print(f"🔧 API: Actualizando operación {operacion_id}")
    
    try:
        # Obtener la operación
        operacion = Operacion.query.get_or_404(operacion_id)
        
        # Verificar permisos
        if not current_user.es_admin and operacion.usuario_id != current_user.id:
            return jsonify({'error': 'No tienes permisos para editar esta operación'}), 403
        
        # Obtener datos del request
        data = request.get_json()
        print(f"📊 Datos recibidos: {data}")
        
        # Validar datos
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Actualizar campos
        if 'monto' in data:
            operacion.monto = float(data['monto'])
        if 'comision' in data:
            operacion.comision = float(data['comision'])
        if 'medio' in data:
            operacion.medio = data['medio']
        
        # Guardar cambios
        db.session.commit()
        
        print(f"✅ Operación {operacion_id} actualizada exitosamente")
        
        # Actualizar comisiones relacionadas
        actualizar_comisiones(operacion)
        
        return jsonify({
            'success': True,
            'message': 'Operación actualizada exitosamente',
            'operacion': {
                'id': operacion.id,
                'monto': operacion.monto,
                'comision': operacion.comision,
                'medio': operacion.medio
            }
        })
        
    except Exception as e:
        print(f"❌ Error al actualizar operación: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar operación: {str(e)}'}), 500

def actualizar_comisiones(operacion):
    """Actualizar comisiones diarias y mensuales"""
    try:
        fecha = operacion.fecha.date()
        año = fecha.year
        mes = fecha.month
        
        # Actualizar comisión diaria
        comision_diaria = ComisionDiaria.query.filter_by(
            usuario_id=operacion.usuario_id,
            fecha=fecha
        ).first()
        
        if comision_diaria:
            # Recalcular total diario
            total_diario = db.session.query(db.func.sum(Operacion.comision)).filter(
                Operacion.usuario_id == operacion.usuario_id,
                db.func.date(Operacion.fecha) == fecha,
                Operacion.activo == True
            ).scalar() or 0.0
            
            comision_diaria.total_comisiones = total_diario
        
        # Actualizar comisión mensual
        comision_mensual = ComisionMensual.query.filter_by(
            usuario_id=operacion.usuario_id,
            año=año,
            mes=mes
        ).first()
        
        if comision_mensual:
            # Recalcular total mensual
            total_mensual = db.session.query(db.func.sum(Operacion.comision)).filter(
                Operacion.usuario_id == operacion.usuario_id,
                db.func.extract('year', Operacion.fecha) == año,
                db.func.extract('month', Operacion.fecha) == mes,
                Operacion.activo == True
            ).scalar() or 0.0
            
            comision_mensual.total_comisiones = total_mensual
        
        db.session.commit()
        
    except Exception as e:
        print(f"⚠️ Error al actualizar comisiones: {str(e)}")
        db.session.rollback()

# Inicialización de la base de datos
def inicializar_db():
    with app.app_context():
        db.create_all()
        
        # Crear sucursal por defecto si no existe
        sucursal_default = Sucursal.query.filter_by(nombre='Sucursal Principal').first()
        if not sucursal_default:
            sucursal_default = Sucursal(
                nombre='Sucursal Principal',
                direccion='Dirección Principal',
                telefono='01-123-4567'
            )
            db.session.add(sucursal_default)
            db.session.commit()
        
        # Crear usuario admin por defecto si no existe
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario()
            admin.username = 'admin'
            admin.email = 'admin@sisagent.com'
            admin.password_hash = generate_password_hash('admin123')
            admin.nombre_completo = 'Administrador SISAGENT'
            admin.es_admin = True
            admin.sucursal_id = sucursal_default.id
            db.session.add(admin)
        
        # Crear usuario normal por defecto si no existe
        usuario1 = Usuario.query.filter_by(username='usuario1').first()
        if not usuario1:
            usuario1 = Usuario()
            usuario1.username = 'usuario1'
            usuario1.email = 'usuario1@sisagent.com'
            usuario1.password_hash = generate_password_hash('password123')
            usuario1.nombre_completo = 'Usuario Normal'
            usuario1.es_admin = False
            usuario1.sucursal_id = sucursal_default.id
            db.session.add(usuario1)
        
        db.session.commit()
        print("✅ Base de datos inicializada correctamente")

if __name__ == '__main__':
    print("🚀 INICIANDO SERVIDOR SISAGENT DEFINITIVO")
    print("=" * 50)
    
    # Inicializar base de datos
    inicializar_db()
    
    print("🌐 Servidor ejecutándose en: http://127.0.0.1:5002")
    print("👤 Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("📝 Características:")
    print("   - API de actualización de operaciones funcional")
    print("   - CORS configurado correctamente")
    print("   - Base de datos SQLite limpia")
    print("   - Logging detallado para debugging")
    
    app.run(debug=True, use_reloader=False, port=5002) 