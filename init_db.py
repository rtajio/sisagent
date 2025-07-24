#!/usr/bin/env python3
"""
Script de inicialización de base de datos para Railway
"""
import os
from app import app, db, Usuario
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializar la base de datos y crear usuario admin"""
    with app.app_context():
        print("🔧 Creando tablas de base de datos...")
        db.create_all()
        print("✅ Tablas creadas exitosamente")
        
        # Crear usuario admin por defecto si no existe
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            print("👤 Creando usuario administrador...")
            admin = Usuario(
                username='admin',
                email='admin@sisagent.com',
                password_hash=generate_password_hash('61442159'),
                nombre_completo='Administrador SISAGENT',
                es_admin=True,
                sucursal_id=None
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado")
        else:
            print("ℹ️ Usuario administrador ya existe")
        
        print("🎉 Inicialización completada")

if __name__ == "__main__":
    init_database()
