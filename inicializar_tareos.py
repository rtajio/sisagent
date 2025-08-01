#!/usr/bin/env python3
"""
Script para inicializar las tablas del módulo de Tareos
"""

import os
import sys
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytz

# Configuración de zona horaria
peru_tz = pytz.timezone('America/Lima')

# Configuración de la aplicación Flask
app = Flask(__name__)

# Configuración para Railway
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Usando PostgreSQL en Railway: {database_url[:20]}...")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_consolidada.db'
    print("✅ Usando SQLite para desarrollo local")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos (copiados de app.py)
class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    activa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(peru_tz))

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(peru_tz))

class Tareo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, en_progreso, completado
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(peru_tz))
    fecha_completado = db.Column(db.DateTime, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Relaciones
    usuario = db.relationship('Usuario', foreign_keys=[usuario_id], backref='tareos_asignados')
    sucursal = db.relationship('Sucursal', backref='tareos')
    creador = db.relationship('Usuario', foreign_keys=[created_by], backref='tareos_creados')
    operaciones = db.relationship('OperacionTareo', backref='tareo', lazy=True, cascade='all, delete-orphan')

class OperacionTareo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tareo_id = db.Column(db.Integer, db.ForeignKey('tareo.id'), nullable=False)
    medio = db.Column(db.String(20), nullable=False)
    destino = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    completado = db.Column(db.Boolean, default=False)
    fecha_completado = db.Column(db.DateTime, nullable=True)
    orden = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(peru_tz))

def inicializar_tareos():
    print("🔧 INICIALIZANDO MÓDULO DE TAREOS")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Crear las tablas
            print("📋 Creando tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Verificar que las tablas existen
            print("\n🔍 Verificando tablas creadas...")
            
            # Verificar tabla Tareo
            try:
                tareos_count = Tareo.query.count()
                print(f"✅ Tabla 'tareo' existe - {tareos_count} registros")
            except Exception as e:
                print(f"❌ Error al verificar tabla 'tareo': {e}")
            
            # Verificar tabla OperacionTareo
            try:
                operaciones_count = OperacionTareo.query.count()
                print(f"✅ Tabla 'operacion_tareo' existe - {operaciones_count} registros")
            except Exception as e:
                print(f"❌ Error al verificar tabla 'operacion_tareo': {e}")
            
            print("\n🎉 Módulo de Tareos inicializado correctamente!")
            print("\n📝 Próximos pasos:")
            print("1. Accede a la aplicación como administrador")
            print("2. Ve a la sección 'Tareos' en el sidebar")
            print("3. Crea tu primer tareo asignando operaciones a usuarios")
            
        except Exception as e:
            print(f"❌ Error al inicializar: {e}")
            return False
    
    return True

if __name__ == "__main__":
    inicializar_tareos() 