#!/usr/bin/env python3
"""
Script para verificar qué base de datos está usando el servidor
"""

import os
import sqlite3
from app import app, db, Sucursal, Usuario

def verificar_servidor_db():
    """Verificar qué base de datos está usando el servidor"""
    
    print("🔍 VERIFICANDO BASE DE DATOS DEL SERVIDOR")
    print("=" * 45)
    
    # 1. Verificar archivos de base de datos
    print("1. Archivos de base de datos en el directorio:")
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    for db_file in db_files:
        size = os.path.getsize(db_file)
        print(f"   - {db_file} ({size} bytes)")
    
    # 2. Verificar configuración de la app
    print(f"\n2. Configuración de la aplicación:")
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    print(f"   - URI de base de datos: {db_uri}")
    
    # 3. Verificar conexión directa
    print(f"\n3. Verificando conexión directa...")
    try:
        with app.app_context():
            # Verificar sucursales
            sucursales = Sucursal.query.filter_by(activa=True).all()
            print(f"   ✅ Conexión exitosa")
            print(f"   - Sucursales activas: {len(sucursales)}")
            
            # Verificar usuarios
            usuarios = Usuario.query.all()
            print(f"   - Usuarios totales: {len(usuarios)}")
            
            # Mostrar detalles
            print(f"\n4. Detalles de sucursales:")
            for sucursal in sucursales:
                print(f"   - ID: {sucursal.id} | {sucursal.nombre} | Activa: {sucursal.activa}")
            
            print(f"\n5. Detalles de usuarios:")
            for usuario in usuarios:
                print(f"   - ID: {usuario.id} | {usuario.username} | Admin: {usuario.es_admin}")
            
            return len(sucursales) > 0
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def verificar_archivo_db():
    """Verificar el archivo de base de datos directamente"""
    
    print(f"\n6. Verificando archivo de base de datos directamente...")
    
    # Buscar archivo sisagent.db
    if os.path.exists('sisagent.db'):
        print(f"   ✅ Archivo sisagent.db encontrado")
        
        try:
            # Conectar directamente
            conn = sqlite3.connect('sisagent.db')
            cursor = conn.cursor()
            
            # Verificar tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   - Tablas encontradas: {[table[0] for table in tables]}")
            
            # Verificar sucursales
            cursor.execute("SELECT id, nombre, activa FROM sucursal WHERE activa = 1;")
            sucursales = cursor.fetchall()
            print(f"   - Sucursales activas: {len(sucursales)}")
            
            for sucursal in sucursales:
                print(f"     * ID: {sucursal[0]} | {sucursal[1]} | Activa: {sucursal[2]}")
            
            # Verificar usuarios
            cursor.execute("SELECT id, username, es_admin FROM usuario;")
            usuarios = cursor.fetchall()
            print(f"   - Usuarios totales: {len(usuarios)}")
            
            for usuario in usuarios:
                print(f"     * ID: {usuario[0]} | {usuario[1]} | Admin: {usuario[2]}")
            
            conn.close()
            return len(sucursales) > 0
            
        except Exception as e:
            print(f"   ❌ Error accediendo al archivo: {e}")
            return False
    else:
        print(f"   ❌ Archivo sisagent.db no encontrado")
        return False

if __name__ == "__main__":
    try:
        # Verificar base de datos del servidor
        servidor_ok = verificar_servidor_db()
        
        # Verificar archivo directamente
        archivo_ok = verificar_archivo_db()
        
        print(f"\n📊 RESUMEN:")
        print(f"   - Servidor conecta: {'✅' if servidor_ok else '❌'}")
        print(f"   - Archivo accesible: {'✅' if archivo_ok else '❌'}")
        
        if servidor_ok and archivo_ok:
            print(f"\n✅ TODO CORRECTO")
            print(f"   La base de datos está funcionando")
            print(f"   El problema debe estar en el frontend")
        else:
            print(f"\n❌ PROBLEMA EN LA BASE DE DATOS")
            print(f"   Revisa los errores anteriores")
            
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}") 