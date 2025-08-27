#!/usr/bin/env python3
"""
Script para crear usuario administrador en Railway (solo si no existe)
"""

import os
from app import app, db, Usuario

def crear_admin():
    """Crear usuario administrador solo si no existe"""
    
    print("👤 Verificando usuario administrador...")
    
    with app.app_context():
        try:
            # Verificar si ya existe un usuario admin
            admin_existente = Usuario.query.filter_by(username='admin').first()
            
            if admin_existente:
                print("✅ Usuario administrador ya existe")
                return
            
            # Crear usuario administrador
            print("👤 Creando usuario administrador...")
            admin = Usuario(
                username='admin',
                password='admin123',
                nombre='Administrador',
                es_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario administrador creado exitosamente")
            print("📝 Credenciales: admin / admin123")
            
        except Exception as e:
            print(f"❌ Error al crear administrador: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    crear_admin() 