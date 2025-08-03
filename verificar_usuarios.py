#!/usr/bin/env python3
"""
Script para verificar todos los usuarios en la base de datos
"""

import sqlite3
import os

def verificar_usuarios():
    """Verificar todos los usuarios en la base de datos"""
    
    # Conectar a la base de datos
    db_path = 'instance/sisagent_consolidada.db'
    
    if not os.path.exists(db_path):
        print(f"❌ No se encontró la base de datos en: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== VERIFICACIÓN COMPLETA DE USUARIOS ===\n")
    
    # 1. Verificar tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("📋 Tablas en la base de datos:")
    for table in tables:
        print(f"   - {table[0]}")
    print()
    
    # 2. Verificar tabla usuario
    try:
        cursor.execute("SELECT COUNT(*) FROM usuario")
        total_usuarios = cursor.fetchone()[0]
        print(f"👥 Total de usuarios en tabla 'usuario': {total_usuarios}")
        
        # Obtener todos los usuarios
        cursor.execute("""
            SELECT id, username, nombre_completo, email, es_admin, activo, sucursal_id, created_at
            FROM usuario 
            ORDER BY id
        """)
        usuarios = cursor.fetchall()
        
        print(f"\n📊 DETALLE DE USUARIOS ({len(usuarios)} encontrados):")
        print("=" * 100)
        print(f"{'ID':<3} | {'Username':<12} | {'Nombre Completo':<25} | {'Email':<30} | {'Admin':<5} | {'Activo':<6} | {'Sucursal':<8} | {'Creado':<10}")
        print("-" * 100)
        
        for usuario in usuarios:
            id_user, username, nombre, email, es_admin, activo, sucursal, created = usuario
            admin_str = "✅" if es_admin else "❌"
            activo_str = "✅" if activo else "❌"
            sucursal_str = str(sucursal) if sucursal else "None"
            created_str = str(created)[:10] if created else "N/A"
            
            print(f"{id_user:<3} | {username:<12} | {nombre:<25} | {email:<30} | {admin_str:<5} | {activo_str:<6} | {sucursal_str:<8} | {created_str:<10}")
        
        print("=" * 100)
        
        # 3. Verificar si hay usuarios inactivos
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE activo = 0")
        inactivos = cursor.fetchone()[0]
        if inactivos > 0:
            print(f"\n⚠️  Usuarios inactivos: {inactivos}")
            cursor.execute("SELECT username, nombre_completo FROM usuario WHERE activo = 0")
            inactivos_list = cursor.fetchall()
            for user in inactivos_list:
                print(f"   - {user[0]} ({user[1]})")
        
        # 4. Verificar usuarios sin sucursal
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE sucursal_id IS NULL")
        sin_sucursal = cursor.fetchone()[0]
        if sin_sucursal > 0:
            print(f"\n⚠️  Usuarios sin sucursal asignada: {sin_sucursal}")
            cursor.execute("SELECT username, nombre_completo FROM usuario WHERE sucursal_id IS NULL")
            sin_sucursal_list = cursor.fetchall()
            for user in sin_sucursal_list:
                print(f"   - {user[0]} ({user[1]})")
        
        # 5. Verificar si hay otros archivos de BD
        print(f"\n🔍 Verificando otros archivos de base de datos...")
        instance_files = [f for f in os.listdir('instance') if f.endswith('.db')]
        print(f"Archivos .db en carpeta instance: {len(instance_files)}")
        for file in instance_files:
            file_path = f"instance/{file}"
            file_size = os.path.getsize(file_path)
            print(f"   - {file} ({file_size} bytes)")
            
            # Verificar usuarios en cada archivo
            try:
                temp_conn = sqlite3.connect(file_path)
                temp_cursor = temp_conn.cursor()
                temp_cursor.execute("SELECT COUNT(*) FROM usuario")
                user_count = temp_cursor.fetchone()[0]
                print(f"     Usuarios en {file}: {user_count}")
                temp_conn.close()
            except Exception as e:
                print(f"     Error al verificar {file}: {e}")
        
    except Exception as e:
        print(f"❌ Error al verificar usuarios: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    verificar_usuarios() 