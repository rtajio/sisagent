#!/usr/bin/env python3
"""
SISAGENT - Adaptado a estructura BD real
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

# Configuración básica
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configuración de base de datos
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Usando PostgreSQL en Railway")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent.db'
    print("✅ Usando SQLite para desarrollo local")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Estabilización de conexión (evita conexiones colgadas en Railway)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 30,
    'pool_size': 5,
    'max_overflow': 10,
}

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo que se adapta a la estructura real de la BD
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Agregar atributos que pueden faltar
    es_admin = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    
    # Relaciones
    sucursal = db.relationship('Sucursal', backref='usuarios')
    
    @property
    def nombre_completo(self):
        return self.username
    
    def check_password(self, password):
        # Usar username como contraseña temporal
        return self.username == password

class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Operacion(db.Model):
    __tablename__ = 'operacion'
    id = db.Column(db.Integer, primary_key=True)
    # Solo usar columnas básicas que seguramente existen
    monto = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, default=0.0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref='operaciones')
    sucursal = db.relationship('Sucursal', backref='operaciones')

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except:
        return None

# Rutas básicas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Usuario y contraseña son requeridos')
                return render_template('login.html')
            
            user = Usuario.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos')
        
        return render_template('login.html')
    except Exception as e:
        print(f"Error en login: {e}")
        return f"Error en login: {str(e)}", 500

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Calcular estadísticas básicas
        total_operaciones = Operacion.query.count()
        total_comision_hoy = 0.0
        total_monto_hoy = 0.0
        
        # Por ahora, usar todas las operaciones ya que no hay fecha
        operaciones_hoy = Operacion.query.all()
        
        for op in operaciones_hoy:
            total_comision_hoy += op.comision or 0.0
            total_monto_hoy += op.monto or 0.0
        
        return render_template('user_dashboard.html', 
                             total_operaciones=total_operaciones,
                             total_comision_hoy=total_comision_hoy,
                             total_monto_hoy=total_monto_hoy)
    except Exception as e:
        return f"Error en dashboard: {str(e)}", 500

@app.route('/operaciones', methods=['GET', 'POST'])
@login_required
def operaciones():
    try:
        # Si llega un POST desde formularios antiguos, evitar caída
        if request.method == 'POST':
            flash('Registro temporalmente redirigido. Use Operaciones solo para consulta.')
            return redirect(url_for('operaciones'))

        operaciones_list = Operacion.query.limit(200).all()
        return render_template('operaciones.html', operaciones=operaciones_list)
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return f"Error en operaciones: {str(e)}", 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Healthcheck simple para Railway
@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/test')
def test():
    return "SISAGENT funcionando correctamente", 200

# ---- Aliases/compat para rutas antiguas (evitan 404/crash) ----
@app.route('/reportes', endpoint='reportes')
@login_required
def reportes_alias():
    return redirect(url_for('operaciones'))

@app.route('/user_dashboard')
def user_dashboard_alias():
    return redirect(url_for('dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard_alias():
    return redirect(url_for('dashboard'))

@app.route('/admin_sucursales')
@app.route('/admin_usuarios')
@app.route('/admin_medios')
@app.route('/admin_tareos')
def admin_sections_alias():
    return redirect(url_for('operaciones'))

@app.route('/registrar_operacion', methods=['GET', 'POST'])
def registrar_operacion_alias():
    flash('Ruta antigua redirigida a Operaciones')
    return redirect(url_for('operaciones'))

@app.route('/tareos_usuario')
def tareos_usuario_alias():
    return redirect(url_for('operaciones'))

# ---- Manejadores de error para mayor estabilidad ----
@app.errorhandler(404)
def handle_404(_e):
    return "Ruta no encontrada", 404

@app.errorhandler(500)
def handle_500(_e):
    try:
        db.session.rollback()
    except Exception:
        pass
    return "Error interno del servidor", 500

if __name__ == '__main__':
    try:
        with app.app_context():
            # NO crear tablas - usar las existentes
            print("✅ Usando base de datos existente")
    except Exception as e:
        print(f"⚠️  Error conectando BD: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
