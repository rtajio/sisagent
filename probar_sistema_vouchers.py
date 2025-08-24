#!/usr/bin/env python3
"""
Script para probar el sistema completo de vouchers
"""

import webbrowser
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

# Crear una aplicación Flask simple para probar
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_vouchers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuración de zona horaria
peru_tz = pytz.timezone('America/Lima')

# Modelos de prueba
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)

class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))

class Operacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=False)
    medio = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.DateTime, default=datetime.now(peru_tz))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref='operaciones')
    sucursal = db.relationship('Sucursal', backref='operaciones')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas de prueba
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('operaciones'))
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('login_simple.html')

@app.route('/operaciones')
@login_required
def operaciones():
    operaciones_list = Operacion.query.all()
    return render_template('operaciones_simple.html', operaciones=operaciones_list)

@app.route('/voucher/<int:operacion_id>/<tamaño>')
@login_required
def generar_voucher(operacion_id, tamaño):
    """Genera un voucher para una operación específica"""
    operacion = Operacion.query.get_or_404(operacion_id)
    
    # Validar tamaño
    if tamaño not in ['58mm', '80mm']:
        tamaño = '80mm'  # Por defecto
    
    # Seleccionar plantilla según tamaño
    template = f'voucher_{tamaño}.html'
    
    return render_template(template, operacion=operacion)

@app.route('/operaciones/<int:operacion_id>/voucher')
@login_required
def imprimir_voucher(operacion_id):
    """Página para seleccionar tamaño de voucher e imprimir"""
    operacion = Operacion.query.get_or_404(operacion_id)
    return render_template('seleccionar_voucher.html', operacion=operacion)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Crear datos de prueba
def crear_datos_prueba():
    with app.app_context():
        db.create_all()
        
        # Crear usuario de prueba
        if not Usuario.query.filter_by(username='admin').first():
            usuario = Usuario(
                username='admin',
                nombre_completo='Administrador Test',
                password_hash=generate_password_hash('admin123'),
                es_admin=True
            )
            db.session.add(usuario)
        
        # Crear sucursal de prueba
        if not Sucursal.query.filter_by(nombre='Sucursal Central').first():
            sucursal = Sucursal(
                nombre='Sucursal Central',
                direccion='Av. Principal 123'
            )
            db.session.add(sucursal)
        
        # Crear operaciones de prueba
        if not Operacion.query.first():
            usuario = Usuario.query.filter_by(username='admin').first()
            sucursal = Sucursal.query.filter_by(nombre='Sucursal Central').first()
            
            operaciones = [
                Operacion(monto=150.00, comision=7.50, medio='BBVA', usuario_id=usuario.id, sucursal_id=sucursal.id),
                Operacion(monto=250.00, comision=12.50, medio='BCP', usuario_id=usuario.id, sucursal_id=sucursal.id),
                Operacion(monto=100.00, comision=5.00, medio='YAPE', usuario_id=usuario.id, sucursal_id=sucursal.id),
            ]
            
            for op in operaciones:
                db.session.add(op)
        
        db.session.commit()

if __name__ == '__main__':
    print("🎫 Sistema de Vouchers - Prueba Completa")
    print("📋 Creando datos de prueba...")
    
    crear_datos_prueba()
    
    print("✅ Datos de prueba creados")
    print("🔗 Accede a: http://127.0.0.1:5002")
    print("👤 Usuario: admin")
    print("🔑 Contraseña: admin123")
    print("🎯 Funcionalidades disponibles:")
    print("   - Ver operaciones")
    print("   - Generar vouchers (58mm y 80mm)")
    print("   - Imprimir vouchers")
    
    # Abrir en el navegador
    webbrowser.open('http://127.0.0.1:5002')
    
    # Ejecutar el servidor
    app.run(host='127.0.0.1', port=5002, debug=True)
