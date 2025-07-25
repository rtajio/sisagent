#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear/verificar el usuario admin en Railway
"""

import os
import sys
from datetime import datetime

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario
from werkzeug.security import generate_password_hash

def print_header():
    print("=" * 60)
    print("🔧 VERIFICADOR Y CREADOR DE USUARIO ADMIN")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

def verificar_admin():
    """Verifica si existe el usuario admin y lo crea si es necesario"""
    try:
        with app.app_context():
            print("🔍 Verificando base de datos...")
            
            # Verificar si existe el usuario admin
            admin = Usuario.query.filter_by(username='admin').first()
            
            if admin:
                print("✅ Usuario admin encontrado:")
                print(f"   - ID: {admin.id}")
                print(f"   - Username: {admin.username}")
                print(f"   - Email: {admin.email}")
                print(f"   - Nombre: {admin.nombre_completo}")
                print(f"   - Es admin: {admin.es_admin}")
                print(f"   - Activo: {admin.activo}")
                print(f"   - Creado: {admin.created_at}")
                
                # Verificar si la contraseña es correcta
                print("\n🔐 Verificando contraseña...")
                from werkzeug.security import check_password_hash
                if check_password_hash(admin.password_hash, '61442159'):
                    print("✅ Contraseña correcta")
                else:
                    print("❌ Contraseña incorrecta - Actualizando...")
                    admin.password_hash = generate_password_hash('61442159')
                    db.session.commit()
                    print("✅ Contraseña actualizada a: 61442159")
                
                return True
            else:
                print("❌ Usuario admin no encontrado - Creando...")
                return crear_admin()
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def crear_admin():
    """Crea el usuario admin"""
    try:
        print("👤 Creando usuario admin...")
        
        admin = Usuario(
            username='admin',
            email='admin@sisagent.com',
            password_hash=generate_password_hash('61442159'),
            nombre_completo='Administrador SISAGENT',
            es_admin=True,
            activo=True,
            sucursal_id=None
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Usuario admin creado exitosamente:")
        print(f"   - Username: admin")
        print(f"   - Contraseña: 61442159")
        print(f"   - Email: admin@sisagent.com")
        print(f"   - Nombre: Administrador SISAGENT")
        print(f"   - Es admin: True")
        print(f"   - Activo: True")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear admin: {str(e)}")
        db.session.rollback()
        return False

def listar_usuarios():
    """Lista todos los usuarios en la base de datos"""
    try:
        print("\n📋 Listando todos los usuarios:")
        usuarios = Usuario.query.all()
        
        if not usuarios:
            print("   No hay usuarios en la base de datos")
            return
        
        for usuario in usuarios:
            print(f"   - ID: {usuario.id} | {usuario.username} | Admin: {usuario.es_admin} | Activo: {usuario.activo}")
            
    except Exception as e:
        print(f"❌ Error al listar usuarios: {str(e)}")

def main():
    print_header()
    
    print("🚀 Iniciando verificación...")
    
    if verificar_admin():
        print("\n✅ Verificación completada exitosamente")
        listar_usuarios()
    else:
        print("\n❌ Error en la verificación")
    
    print("\n" + "=" * 60)
    print("🔑 CREDENCIALES DE ACCESO:")
    print("   Usuario: admin")
    print("   Contraseña: 61442159")
    print("=" * 60)

if __name__ == "__main__":
    main() 