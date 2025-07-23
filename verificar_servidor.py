#!/usr/bin/env python3
"""
Script para verificar el estado del servidor y la base de datos
"""

import os
import sqlite3
from app import app, db, Sucursal, Usuario, Operacion

def verificar_servidor():
    """Verificar el estado del servidor y la base de datos"""
    
    print("🔍 VERIFICANDO ESTADO DEL SERVIDOR")
    print("=" * 40)
    
    # 1. Verificar archivo de base de datos
    print("1. Verificando archivo de base de datos...")
    db_file = "sisagent.db"
    if os.path.exists(db_file):
        print(f"   ✅ Archivo encontrado: {db_file}")
        size = os.path.getsize(db_file)
        print(f"   📊 Tamaño: {size} bytes")
    else:
        print(f"   ❌ Archivo no encontrado: {db_file}")
    
    # 2. Verificar conexión a la base de datos
    print("\n2. Verificando conexión a la base de datos...")
    try:
        with app.app_context():
            # Intentar conectar
            db.engine.connect()
            print("   ✅ Conexión exitosa")
            
            # Verificar tablas
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"   📋 Tablas encontradas: {tables}")
            
            # Verificar datos
            usuarios_count = Usuario.query.count()
            sucursales_count = Sucursal.query.count()
            operaciones_count = Operacion.query.count()
            
            print(f"   👥 Usuarios: {usuarios_count}")
            print(f"   🏢 Sucursales: {sucursales_count}")
            print(f"   💰 Operaciones: {operaciones_count}")
            
            if usuarios_count == 0:
                print("   ⚠️  No hay usuarios en la base de datos")
                return False
            else:
                print("   ✅ Base de datos tiene datos")
                return True
                
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def crear_datos_basicos():
    """Crear datos básicos si no existen"""
    
    print("\n3. Creando datos básicos...")
    
    try:
        with app.app_context():
            # Verificar si ya hay datos
            if Usuario.query.count() > 0:
                print("   ✅ Ya hay datos en la base de datos")
                return True
            
            # Crear sucursal
            sucursal = Sucursal(
                nombre="Sucursal Principal",
                direccion="Dirección Principal",
                activa=True
            )
            db.session.add(sucursal)
            db.session.commit()
            print("   ✅ Sucursal creada")
            
            # Crear usuario admin
            from werkzeug.security import generate_password_hash
            admin = Usuario(
                username='admin',
                email='admin@sisagent.com',
                password_hash=generate_password_hash('admin123'),
                nombre_completo='Administrador SISAGENT',
                es_admin=True,
                sucursal_id=sucursal.id,
                activo=True
            )
            db.session.add(admin)
            db.session.commit()
            print("   ✅ Usuario admin creado")
            
            # Crear usuario normal
            usuario = Usuario(
                username='usuario1',
                email='usuario1@sisagent.com',
                password_hash=generate_password_hash('password123'),
                nombre_completo='Usuario Normal',
                es_admin=False,
                sucursal_id=sucursal.id,
                activo=True
            )
            db.session.add(usuario)
            db.session.commit()
            print("   ✅ Usuario normal creado")
            
            print("   🎉 Datos básicos creados exitosamente")
            return True
            
    except Exception as e:
        print(f"   ❌ Error creando datos: {e}")
        return False

if __name__ == "__main__":
    # Verificar estado actual
    estado_ok = verificar_servidor()
    
    if not estado_ok:
        # Crear datos básicos si es necesario
        crear_datos_basicos()
        
        # Verificar nuevamente
        print("\n4. Verificación final...")
        verificar_servidor()
    
    print("\n🎯 VERIFICACIÓN COMPLETADA")
    print("Si todo está bien, el servidor debería funcionar correctamente.") 