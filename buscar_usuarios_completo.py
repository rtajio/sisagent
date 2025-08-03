#!/usr/bin/env python3
"""
Script completo para buscar usuarios en TODAS las bases de datos
"""

import sqlite3
import os
import glob

def buscar_usuarios_completo():
    """Buscar usuarios en todas las bases de datos del proyecto"""
    
    print("=== BÚSQUEDA COMPLETA DE USUARIOS ===\n")
    
    # Buscar todos los archivos .db en todo el proyecto
    db_files = []
    
    # Buscar en directorio raíz
    db_files.extend(glob.glob("*.db"))
    
    # Buscar en instance/
    if os.path.exists("instance"):
        db_files.extend(glob.glob("instance/*.db"))
    
    # Buscar en backups/ y subdirectorios
    if os.path.exists("backups"):
        db_files.extend(glob.glob("backups/**/*.db", recursive=True))
    
    print(f"📁 Archivos de base de datos encontrados: {len(db_files)}")
    for file in db_files:
        print(f"   - {file}")
    
    todos_usuarios = []
    
    for file_path in db_files:
        if not os.path.exists(file_path):
            continue
            
        file_size = os.path.getsize(file_path)
        print(f"\n🔍 Verificando: {file_path} ({file_size} bytes)")
        
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # Verificar si existe tabla usuario
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
            if not cursor.fetchone():
                print(f"   ❌ No tiene tabla usuario")
                continue
            
            # Contar usuarios
            cursor.execute("SELECT COUNT(*) FROM usuario")
            count = cursor.fetchone()[0]
            print(f"   ✅ {count} usuarios")
            
            # Obtener usuarios
            try:
                cursor.execute("SELECT id, username, nombre_completo, email, es_admin FROM usuario")
            except:
                try:
                    cursor.execute("SELECT id, username, nombre_completo, email, es_admin, activo FROM usuario")
                except:
                    cursor.execute("SELECT id, username, nombre_completo, email, es_admin, activo, sucursal_id FROM usuario")
            
            usuarios = cursor.fetchall()
            
            for usuario in usuarios:
                if len(usuario) >= 5:
                    id_user, username, nombre, email, es_admin = usuario[:5]
                    
                    todos_usuarios.append({
                        'archivo': file_path,
                        'id': id_user,
                        'username': username,
                        'nombre': nombre,
                        'email': email,
                        'es_admin': es_admin
                    })
                    
                    print(f"   👤 {id_user:2} | {username:<12} | {nombre:<20}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    # Eliminar duplicados por username
    usuarios_unicos = {}
    for user in todos_usuarios:
        username = user['username']
        if username not in usuarios_unicos:
            usuarios_unicos[username] = user
        else:
            # Mantener el más reciente (sisagent_consolidada.db tiene prioridad)
            if user['archivo'] == 'instance/sisagent_consolidada.db':
                usuarios_unicos[username] = user
    
    print(f"\n" + "="*100)
    print(f"📊 RESUMEN FINAL: {len(usuarios_unicos)} USUARIOS ÚNICOS ENCONTRADOS")
    print("="*100)
    
    # Mostrar usuarios únicos ordenados por ID
    usuarios_ordenados = sorted(usuarios_unicos.values(), key=lambda x: x['id'])
    
    for i, user in enumerate(usuarios_ordenados, 1):
        admin_str = "✅" if user['es_admin'] else "❌"
        archivo_short = user['archivo'].replace('instance/', '').replace('backups/', '')
        print(f"{i:2}. {user['id']:<3} | {user['username']:<12} | {user['nombre']:<25} | {user['email']:<30} | {admin_str:<5} | {archivo_short}")
    
    print("-" * 100)
    
    # Verificar si encontramos los 12 usuarios
    if len(usuarios_unicos) == 12:
        print(f"\n✅ ¡PERFECTO! Se encontraron exactamente 12 usuarios únicos")
    elif len(usuarios_unicos) > 12:
        print(f"\n⚠️  Se encontraron {len(usuarios_unicos)} usuarios (más de 12)")
        print("   Posibles duplicados o usuarios adicionales")
    else:
        print(f"\n❌ Solo se encontraron {len(usuarios_unicos)} usuarios (faltan {12 - len(usuarios_unicos)})")
    
    # Mostrar estadísticas por archivo
    print(f"\n📊 ESTADÍSTICAS POR ARCHIVO:")
    archivos_stats = {}
    for user in todos_usuarios:
        archivo = user['archivo']
        if archivo not in archivos_stats:
            archivos_stats[archivo] = []
        archivos_stats[archivo].append(user['username'])
    
    for archivo, usernames in archivos_stats.items():
        archivo_short = archivo.replace('instance/', '').replace('backups/', '')
        print(f"   {archivo_short}: {len(usernames)} usuarios")
    
    return usuarios_unicos

if __name__ == "__main__":
    buscar_usuarios_completo() 