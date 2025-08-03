#!/usr/bin/env python3
"""
Script final para contar todos los usuarios únicos
"""

import sqlite3
import os

def conteo_final_usuarios():
    """Conteo final de todos los usuarios únicos"""
    
    print("=== CONTEO FINAL DE USUARIOS ===\n")
    
    # Listar todos los archivos .db
    instance_files = [f for f in os.listdir('instance') if f.endswith('.db')]
    todos_usuarios = []
    
    for file in instance_files:
        file_path = f"instance/{file}"
        print(f"🔍 Verificando: {file}")
        
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
            cursor.execute("SELECT id, username, nombre_completo, email, es_admin FROM usuario")
            usuarios = cursor.fetchall()
            
            for usuario in usuarios:
                id_user, username, nombre, email, es_admin = usuario
                todos_usuarios.append({
                    'archivo': file,
                    'id': id_user,
                    'username': username,
                    'nombre': nombre,
                    'email': email,
                    'es_admin': es_admin
                })
                
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
            # Mantener el de sisagent_consolidada.db si existe
            if user['archivo'] == 'sisagent_consolidada.db':
                usuarios_unicos[username] = user
    
    print(f"\n" + "="*80)
    print(f"📊 RESUMEN FINAL: {len(usuarios_unicos)} USUARIOS ÚNICOS")
    print("="*80)
    
    # Mostrar usuarios únicos ordenados por ID
    usuarios_ordenados = sorted(usuarios_unicos.values(), key=lambda x: x['id'])
    
    for i, user in enumerate(usuarios_ordenados, 1):
        admin_str = "✅" if user['es_admin'] else "❌"
        print(f"{i:2}. {user['id']:<3} | {user['username']:<12} | {user['nombre']:<25} | {user['email']:<30} | {admin_str}")
    
    print("-" * 80)
    
    # Verificar si son exactamente 12
    if len(usuarios_unicos) == 12:
        print(f"\n✅ ¡PERFECTO! Se encontraron exactamente 12 usuarios únicos")
    elif len(usuarios_unicos) > 12:
        print(f"\n⚠️  Se encontraron {len(usuarios_unicos)} usuarios (más de 12)")
        print("   Posibles duplicados o usuarios adicionales")
    else:
        print(f"\n❌ Solo se encontraron {len(usuarios_unicos)} usuarios (faltan {12 - len(usuarios_unicos)})")
        print("   Los usuarios faltantes podrían estar en:")
        print("   - Archivos de backup no detectados")
        print("   - Otra ubicación de base de datos")
        print("   - Archivos temporales")
    
    return usuarios_unicos

if __name__ == "__main__":
    conteo_final_usuarios() 