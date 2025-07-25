#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para forzar la creación del usuario admin en Railway
"""

import os
import sys
from datetime import datetime

# Configurar variables de entorno para Railway
os.environ['FLASK_ENV'] = 'production'

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def crear_admin_forzado():
    """Fuerza la creación del usuario admin"""
    try:
        print("🚀 Iniciando creación forzada de admin...")
        
        # Importar después de configurar el entorno
        from app import app, db, Usuario
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            print("🔍 Verificando base de datos...")
            
            # Crear tablas si no existen
            db.create_all()
            print("✅ Tablas creadas/verificadas")
            
            # Eliminar usuario admin existente si existe
            admin_existente = Usuario.query.filter_by(username='admin').first()
            if admin_existente:
                print("🗑️ Eliminando usuario admin existente...")
                db.session.delete(admin_existente)
                db.session.commit()
                print("✅ Usuario admin anterior eliminado")
            
            # Crear nuevo usuario admin
            print("👤 Creando nuevo usuario admin...")
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
            
            print("✅ Usuario admin creado exitosamente!")
            print(f"   - Username: {admin.username}")
            print(f"   - Contraseña: 61442159")
            print(f"   - Email: {admin.email}")
            print(f"   - Nombre: {admin.nombre_completo}")
            print(f"   - Es admin: {admin.es_admin}")
            print(f"   - Activo: {admin.activo}")
            print(f"   - ID: {admin.id}")
            
            # Verificar que se creó correctamente
            admin_verificado = Usuario.query.filter_by(username='admin').first()
            if admin_verificado:
                print("✅ Verificación exitosa - Usuario admin disponible")
                return True
            else:
                print("❌ Error - Usuario admin no encontrado después de crear")
                return False
                
    except Exception as e:
        print(f"❌ Error durante la creación: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verificar_conexion_db():
    """Verifica la conexión a la base de datos"""
    try:
        print("🔍 Verificando conexión a base de datos...")
        
        from app import app, db
        
        with app.app_context():
            # Intentar una consulta simple
            result = db.session.execute('SELECT 1')
            print("✅ Conexión a base de datos exitosa")
            return True
            
    except Exception as e:
        print(f"❌ Error de conexión a base de datos: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("🔧 FORZADOR DE CREACIÓN DE ADMIN - RAILWAY")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    # Verificar conexión a base de datos
    if not verificar_conexion_db():
        print("❌ No se puede conectar a la base de datos")
        return
    
    # Crear admin
    if crear_admin_forzado():
        print("\n" + "=" * 60)
        print("🎉 ¡ADMIN CREADO EXITOSAMENTE!")
        print("=" * 60)
        print("🔑 CREDENCIALES:")
        print("   Usuario: admin")
        print("   Contraseña: 61442159")
        print("=" * 60)
        print("🚀 Ahora puedes acceder al sistema")
    else:
        print("\n❌ Error al crear admin")

if __name__ == "__main__":
    main() 