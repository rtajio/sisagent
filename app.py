#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Vouchers - App Simple y Funcional
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from datetime import datetime
import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sisagent.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos básicos
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
    return Usuario.query.get(int(user_id))

# Rutas básicas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('user_dashboard.html')

@app.route('/operaciones')
@login_required
def operaciones():
    operaciones_list = Operacion.query.all()
    return render_template('operaciones.html', operaciones=operaciones_list)

# RUTAS DE HEALTHCHECK - CRÍTICAS PARA RAILWAY
@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/railway-health')
def railway_health():
    return "OK", 200

@app.route('/api/health')
def api_health():
    return "OK", 200

# Ruta de vouchers
@app.route('/voucher/<int:operacion_id>/<tamaño>')
@login_required
def generar_voucher(operacion_id, tamaño):
    operacion = Operacion.query.get_or_404(operacion_id)
    if tamaño not in ['58mm', '80mm']:
        tamaño = '80mm'
    
    template = f'voucher_{tamaño}.html'
    return render_template(template, operacion=operacion)

@app.route('/operaciones/<int:operacion_id>/voucher')
@login_required
def seleccionar_voucher(operacion_id):
    operacion = Operacion.query.get_or_404(operacion_id)
    return render_template('seleccionar_voucher.html', operacion=operacion)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
