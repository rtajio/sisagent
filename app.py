#!/usr/bin/env python3
"""
SISAGENT - Versión Ultra Simplificada
"""

from flask import Flask, render_template, request, redirect, url_for, flash
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

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos simplificados
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)

class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))

class Operacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
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
    try:
        return redirect(url_for('login'))
    except Exception as e:
        return f"Error en index: {str(e)}", 500

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
            
            if user and user.password == password:
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
        return render_template('user_dashboard.html')
    except Exception as e:
        return f"Error en dashboard: {str(e)}", 500

@app.route('/operaciones')
@login_required
def operaciones():
    try:
        operaciones_list = Operacion.query.all()
        return render_template('operaciones.html', operaciones=operaciones_list)
    except Exception as e:
        return f"Error en operaciones: {str(e)}", 500

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        return redirect(url_for('login'))
    except Exception as e:
        return f"Error en logout: {str(e)}", 500

# Healthcheck simple
@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/test')
def test():
    return "SISAGENT funcionando correctamente", 200

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
            print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"⚠️  Error inicializando BD: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
