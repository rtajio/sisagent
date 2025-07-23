#!/usr/bin/env python3
"""
Servidor SISAGENT Final
Versión completamente funcional con edición de operaciones
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sisagent-final-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_final.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nombre_completo = db.Column(db.String(120), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sucursal = db.relationship('Sucursal', backref='usuarios')

class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

class Operacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=False)
    medio = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref='operaciones')
    sucursal = db.relationship('Sucursal', backref='operaciones')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas
@app.route('/')
@login_required
def index():
    return redirect(url_for('operaciones'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('operaciones'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/operaciones')
@login_required
def operaciones():
    # Obtener operaciones según el rol del usuario
    if current_user.es_admin:
        operaciones_list = Operacion.query.order_by(Operacion.hora.desc()).all()
    else:
        operaciones_list = Operacion.query.filter_by(sucursal_id=current_user.sucursal_id).order_by(Operacion.hora.desc()).all()
    
    # Obtener sucursales para el formulario
    sucursales = Sucursal.query.filter_by(activo=True).all()
    
    return render_template('operaciones.html', operaciones=operaciones_list, sucursales=sucursales)

@app.route('/registrar_operacion', methods=['POST'])
@login_required
def registrar_operacion():
    try:
        monto = float(request.form.get('monto'))
        comision = float(request.form.get('comision'))
        medio = request.form.get('medio')
        sucursal_id = int(request.form.get('sucursal_id'))
        
        # Validaciones
        if monto <= 0:
            flash('El monto debe ser mayor a 0', 'error')
            return redirect(url_for('operaciones'))
        
        if comision < 0:
            flash('La comisión no puede ser negativa', 'error')
            return redirect(url_for('operaciones'))
        
        # Crear la operación
        operacion = Operacion(
            monto=monto,
            comision=comision,
            medio=medio,
            usuario_id=current_user.id,
            sucursal_id=sucursal_id
        )
        
        db.session.add(operacion)
        db.session.commit()
        
        flash('Operación registrada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la operación: {str(e)}', 'error')
    
    return redirect(url_for('operaciones'))

@app.route('/editar_operacion/<int:operacion_id>', methods=['POST'])
@login_required
def editar_operacion(operacion_id):
    try:
        operacion = Operacion.query.get_or_404(operacion_id)
        
        # Verificar permisos
        if not current_user.es_admin and operacion.sucursal_id != current_user.sucursal_id:
            flash('No tienes permisos para editar esta operación', 'error')
            return redirect(url_for('operaciones'))
        
        # Obtener datos del formulario
        monto = float(request.form.get('monto'))
        comision = float(request.form.get('comision'))
        medio = request.form.get('medio')
        
        # Validaciones
        if monto <= 0:
            flash('El monto debe ser mayor a 0', 'error')
            return redirect(url_for('operaciones'))
        
        if comision < 0:
            flash('La comisión no puede ser negativa', 'error')
            return redirect(url_for('operaciones'))
        
        # Actualizar la operación
        operacion.monto = monto
        operacion.comision = comision
        operacion.medio = medio
        
        db.session.commit()
        
        flash('Operación actualizada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al actualizar la operación: {str(e)}', 'error')
    
    return redirect(url_for('operaciones'))

@app.route('/eliminar_operacion/<int:operacion_id>', methods=['POST'])
@login_required
def eliminar_operacion(operacion_id):
    try:
        operacion = Operacion.query.get_or_404(operacion_id)
        
        # Verificar permisos
        if not current_user.es_admin and operacion.sucursal_id != current_user.sucursal_id:
            flash('No tienes permisos para eliminar esta operación', 'error')
            return redirect(url_for('operaciones'))
        
        db.session.delete(operacion)
        db.session.commit()
        
        flash('Operación eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar la operación: {str(e)}', 'error')
    
    return redirect(url_for('operaciones'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Crear datos de prueba si no existen
        if not Sucursal.query.first():
            sucursal_default = Sucursal(nombre='Sucursal Principal', direccion='Dirección Principal')
            db.session.add(sucursal_default)
            db.session.commit()
        
        if not Usuario.query.first():
            sucursal_default = Sucursal.query.first()
            
            # Crear usuario admin
            admin = Usuario()
            admin.username = 'admin'
            admin.email = 'admin@sisagent.com'
            admin.password_hash = generate_password_hash('admin123')
            admin.nombre_completo = 'Administrador SISAGENT'
            admin.es_admin = True
            admin.sucursal_id = sucursal_default.id
            db.session.add(admin)
            
            # Crear usuario normal
            usuario1 = Usuario()
            usuario1.username = 'usuario1'
            usuario1.email = 'usuario1@sisagent.com'
            usuario1.password_hash = generate_password_hash('password123')
            usuario1.nombre_completo = 'Usuario Normal'
            usuario1.es_admin = False
            usuario1.sucursal_id = sucursal_default.id
            db.session.add(usuario1)
            
            db.session.commit()
    
    print("🚀 INICIANDO SERVIDOR FINAL")
    print("=" * 40)
    print("✅ Base de datos inicializada")
    print("🌐 Servidor ejecutándose en: http://127.0.0.1:5000")
    print("👤 Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("📝 Características:")
    print("   - Edición por formulario tradicional")
    print("   - Modal de Bootstrap")
    print("   - Sin errores de JSON")
    print("   - Base de datos SQLite limpia")
    
    app.run(debug=True, use_reloader=False, port=5000) 