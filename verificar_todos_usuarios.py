#!/usr/bin/env python3
"""
Script para verificar TODOS los usuarios en TODAS las bases de datos
"""

import sqlite3
import os

def verificar_todos_usuarios():
    """Verificar todos los usuarios en todas las bases de datos"""
    
    print("=== VERIFICACIÓN DE TODOS LOS USUARIOS EN TODAS LAS BD ===\n")
    
    # Listar todos los archivos .db
    instance_files = [f for f in os.listdir('instance') if f.endswith('.db')]
    print(f"📁 Archivos de base de datos encontrados: {len(instance_files)}")
    
    todos_usuarios = []
    
    for file in instance_files:
        file_path = f"instance/{file}"
        file_size = os.path.getsize(file_path)
        
        print(f"\n🔍 Verificando: {file} ({file_size} bytes)")
        print("-" * 50)
        
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # Verificar si existe la tabla usuario
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM usuario")
                user_count = cursor.fetchone()[0]
                print(f"   ✅ Tabla 'usuario' encontrada con {user_count} usuarios")
                
                # Obtener todos los usuarios de este archivo
                cursor.execute("""
                    SELECT id, username, nombre_completo, email, es_admin, activo, sucursal_id
                    FROM usuario 
                    ORDER BY id
                """)
                usuarios_archivo = cursor.fetchall()
                
                for usuario in usuarios_archivo:
                    id_user, username, nombre, email, es_admin, activo, sucursal = usuario
                    todos_usuarios.append({
                        'archivo': file,
                        'id': id_user,
                        'username': username,
                        'nombre': nombre,
                        'email': email,
                        'es_admin': es_admin,
                        'activo': activo,
                        'sucursal': sucursal
                    })
                    print(f"   👤 {id_user:2} | {username:<12} | {nombre:<20} | {'Admin' if es_admin else 'User'}")
            else:
                print(f"   ❌ No se encontró tabla 'usuario' en {file}")
                
        except Exception as e:
            print(f"   ❌ Error al verificar {file}: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    # Mostrar resumen total
    print(f"\n" + "="*80)
    print(f"📊 RESUMEN TOTAL: {len(todos_usuarios)} USUARIOS ENCONTRADOS")
    print("="*80)
    
    # Eliminar duplicados por username
    usuarios_unicos = {}
    for user in todos_usuarios:
        username = user['username']
        if username not in usuarios_unicos:
            usuarios_unicos[username] = user
        else:
            # Si hay duplicado, mantener el más reciente (archivo más grande)
            if user['archivo'] == 'sisagent_consolidada.db':
                usuarios_unicos[username] = user
    
    print(f"\n👥 USUARIOS ÚNICOS ({len(usuarios_unicos)}):")
    print("-" * 80)
    print(f"{'ID':<3} | {'Username':<12} | {'Nombre Completo':<25} | {'Email':<30} | {'Admin':<5} | {'Archivo':<20}")
    print("-" * 80)
    
    for username, user in sorted(usuarios_unicos.items(), key=lambda x: x[1]['id']):
        admin_str = "✅" if user['es_admin'] else "❌"
        print(f"{user['id']:<3} | {user['username']:<12} | {user['nombre']:<25} | {user['email']:<30} | {admin_str:<5} | {user['archivo']:<20}")
    
    print("-" * 80)
    
    # Verificar si encontramos los 12 usuarios
    if len(usuarios_unicos) == 12:
        print(f"\n✅ ¡PERFECTO! Se encontraron exactamente 12 usuarios únicos")
    elif len(usuarios_unicos) > 12:
        print(f"\n⚠️  Se encontraron {len(usuarios_unicos)} usuarios (más de 12)")
    else:
        print(f"\n❌ Solo se encontraron {len(usuarios_unicos)} usuarios (faltan {12 - len(usuarios_unicos)})")
    
    return usuarios_unicos

if __name__ == "__main__":
    verificar_todos_usuarios() 