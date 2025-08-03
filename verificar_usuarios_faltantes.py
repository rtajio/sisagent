#!/usr/bin/env python3
"""
Script para encontrar los usuarios faltantes
"""

import sqlite3
import os

def verificar_usuarios_faltantes():
    """Verificar usuarios faltantes en todas las bases de datos"""
    
    print("=== BUSCANDO LOS 12 USUARIOS ===\n")
    
    instance_files = [f for f in os.listdir('instance') if f.endswith('.db')]
    todos_usuarios = []
    
    for file in instance_files:
        file_path = f"instance/{file}"
        print(f"\n🔍 Verificando: {file}")
        
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # Verificar estructura de la tabla
            cursor.execute("PRAGMA table_info(usuario)")
            columnas = cursor.fetchall()
            print(f"   Columnas en tabla usuario: {[col[1] for col in columnas]}")
            
            # Intentar diferentes consultas según la estructura
            try:
                # Consulta completa
                cursor.execute("""
                    SELECT id, username, nombre_completo, email, es_admin, activo, sucursal_id
                    FROM usuario 
                    ORDER BY id
                """)
            except:
                try:
                    # Consulta sin sucursal_id
                    cursor.execute("""
                        SELECT id, username, nombre_completo, email, es_admin, activo
                        FROM usuario 
                        ORDER BY id
                    """)
                except:
                    # Consulta básica
                    cursor.execute("""
                        SELECT id, username, nombre_completo, email, es_admin
                        FROM usuario 
                        ORDER BY id
                    """)
            
            usuarios_archivo = cursor.fetchall()
            print(f"   ✅ Encontrados {len(usuarios_archivo)} usuarios")
            
            for usuario in usuarios_archivo:
                if len(usuario) >= 5:
                    id_user, username, nombre, email, es_admin = usuario[:5]
                    activo = usuario[5] if len(usuario) > 5 else 1
                    sucursal = usuario[6] if len(usuario) > 6 else None
                    
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
                    
                    print(f"   👤 {id_user:2} | {username:<12} | {nombre:<20}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        finally:
            if 'conn' in locals():
                conn.close()
    
    # Eliminar duplicados y mostrar usuarios únicos
    usuarios_unicos = {}
    for user in todos_usuarios:
        username = user['username']
        if username not in usuarios_unicos:
            usuarios_unicos[username] = user
        else:
            # Mantener el más reciente
            if user['archivo'] == 'sisagent_consolidada.db':
                usuarios_unicos[username] = user
    
    print(f"\n" + "="*80)
    print(f"📊 TOTAL DE USUARIOS ÚNICOS: {len(usuarios_unicos)}")
    print("="*80)
    
    for username, user in sorted(usuarios_unicos.items(), key=lambda x: x[1]['id']):
        admin_str = "✅" if user['es_admin'] else "❌"
        print(f"{user['id']:<3} | {user['username']:<12} | {user['nombre']:<25} | {user['email']:<30} | {admin_str:<5} | {user['archivo']}")
    
    print("-" * 80)
    
    if len(usuarios_unicos) == 12:
        print(f"\n✅ ¡PERFECTO! Se encontraron exactamente 12 usuarios")
    elif len(usuarios_unicos) > 12:
        print(f"\n⚠️  Se encontraron {len(usuarios_unicos)} usuarios (más de 12)")
    else:
        print(f"\n❌ Solo se encontraron {len(usuarios_unicos)} usuarios (faltan {12 - len(usuarios_unicos)})")
        
        # Verificar si hay usuarios en otros archivos que no se detectaron
        print(f"\n🔍 Verificando archivos adicionales...")
        
        # Verificar si hay archivos de backup
        backup_files = [f for f in os.listdir('backups') if f.endswith('.db')] if os.path.exists('backups') else []
        for backup_file in backup_files:
            print(f"   Verificando backup: {backup_file}")
            # Aquí podrías agregar lógica para verificar backups si es necesario

if __name__ == "__main__":
    verificar_usuarios_faltantes() 