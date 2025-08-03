#!/usr/bin/env python3
"""
Búsqueda exhaustiva de usuarios en todo el proyecto
"""

import sqlite3
import os
import glob
import re

def busqueda_exhaustiva_usuarios():
    """Búsqueda exhaustiva de usuarios en todo el proyecto"""
    
    print("=== BÚSQUEDA EXHAUSTIVA DE USUARIOS ===\n")
    
    # 1. Buscar TODOS los archivos de base de datos
    print("🔍 PASO 1: Buscando archivos de base de datos...")
    db_files = []
    
    # Buscar en todo el proyecto recursivamente
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
                full_path = os.path.join(root, file)
                db_files.append(full_path)
    
    print(f"📁 Archivos de BD encontrados: {len(db_files)}")
    for file in db_files:
        print(f"   - {file}")
    
    # 2. Buscar en archivos de texto y scripts
    print(f"\n🔍 PASO 2: Buscando usuarios en archivos de texto...")
    text_files = []
    
    # Buscar en archivos Python, SQL, TXT, etc.
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.py', '.sql', '.txt', '.md', '.json', '.csv')):
                full_path = os.path.join(root, file)
                text_files.append(full_path)
    
    print(f"📁 Archivos de texto encontrados: {len(text_files)}")
    
    # 3. Buscar usuarios en bases de datos
    print(f"\n🔍 PASO 3: Extrayendo usuarios de bases de datos...")
    todos_usuarios = []
    
    for file_path in db_files:
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            continue
            
        file_size = os.path.getsize(file_path)
        print(f"\n📊 Verificando: {file_path} ({file_size} bytes)")
        
        try:
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            
            # Verificar si existe tabla usuario
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"   Tablas encontradas: {[t[0] for t in tables]}")
            
            # Buscar tabla usuario o similar
            usuario_table = None
            for table in tables:
                table_name = table[0].lower()
                if 'usuario' in table_name or 'user' in table_name:
                    usuario_table = table[0]
                    break
            
            if usuario_table:
                print(f"   ✅ Tabla de usuarios encontrada: {usuario_table}")
                
                # Obtener estructura de la tabla
                cursor.execute(f"PRAGMA table_info({usuario_table})")
                columns = cursor.fetchall()
                print(f"   Columnas: {[col[1] for col in columns]}")
                
                # Contar usuarios
                cursor.execute(f"SELECT COUNT(*) FROM {usuario_table}")
                count = cursor.fetchone()[0]
                print(f"   👥 {count} usuarios encontrados")
                
                # Intentar diferentes consultas
                try:
                    cursor.execute(f"SELECT * FROM {usuario_table}")
                    usuarios = cursor.fetchall()
                    
                    for i, usuario in enumerate(usuarios):
                        print(f"   👤 Usuario {i+1}: {usuario}")
                        
                        # Intentar extraer información básica
                        if len(usuario) >= 3:
                            user_data = {
                                'archivo': file_path,
                                'id': usuario[0] if len(usuario) > 0 else i+1,
                                'username': str(usuario[1]) if len(usuario) > 1 else f"user_{i+1}",
                                'nombre': str(usuario[2]) if len(usuario) > 2 else f"Usuario {i+1}",
                                'email': str(usuario[3]) if len(usuario) > 3 else f"user{i+1}@sisagent.com",
                                'es_admin': bool(usuario[4]) if len(usuario) > 4 else False
                            }
                            todos_usuarios.append(user_data)
                
                except Exception as e:
                    print(f"   ❌ Error al leer usuarios: {e}")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Error al abrir {file_path}: {e}")
    
    # 4. Buscar usuarios en archivos de texto
    print(f"\n🔍 PASO 4: Buscando usuarios en archivos de texto...")
    
    # Patrones para buscar usuarios
    patterns = [
        r'username["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        r'email["\']?\s*[:=]\s*["\']([^"\']+@[^"\']+)["\']',
        r'nombre_completo["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        r'usuario["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        r'user["\']?\s*[:=]\s*["\']([^"\']+)["\']'
    ]
    
    for file_path in text_files[:20]:  # Limitar a 20 archivos para no sobrecargar
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        print(f"   📄 {file_path}: {len(matches)} coincidencias")
                        for match in matches[:5]:  # Mostrar solo las primeras 5
                            print(f"      - {match}")
        except:
            pass
    
    # 5. Resumen final
    print(f"\n" + "="*100)
    print(f"📊 RESUMEN FINAL DE BÚSQUEDA EXHAUSTIVA")
    print("="*100)
    
    # Eliminar duplicados por username
    usuarios_unicos = {}
    for user in todos_usuarios:
        username = user['username']
        if username not in usuarios_unicos:
            usuarios_unicos[username] = user
        else:
            # Mantener el más reciente
            if 'consolidada' in user['archivo']:
                usuarios_unicos[username] = user
    
    print(f"👥 USUARIOS ÚNICOS ENCONTRADOS: {len(usuarios_unicos)}")
    print("-" * 100)
    
    for i, (username, user) in enumerate(sorted(usuarios_unicos.items(), key=lambda x: x[1]['id']), 1):
        admin_str = "✅" if user['es_admin'] else "❌"
        archivo_short = user['archivo'].replace('./', '').replace('instance/', '').replace('backups/', '')
        print(f"{i:2}. {user['id']:<3} | {user['username']:<15} | {user['nombre']:<25} | {user['email']:<30} | {admin_str:<5} | {archivo_short}")
    
    print("-" * 100)
    
    if len(usuarios_unicos) == 12:
        print(f"\n✅ ¡PERFECTO! Se encontraron exactamente 12 usuarios únicos")
    elif len(usuarios_unicos) > 12:
        print(f"\n⚠️  Se encontraron {len(usuarios_unicos)} usuarios (más de 12)")
    else:
        print(f"\n❌ Solo se encontraron {len(usuarios_unicos)} usuarios (faltan {12 - len(usuarios_unicos)})")
        print(f"\n🔍 Posibles causas de usuarios faltantes:")
        print(f"   - Usuarios eliminados durante desarrollo")
        print(f"   - Archivos de BD corruptos o vacíos")
        print(f"   - Usuarios en archivos no detectados")
        print(f"   - Usuarios en formato diferente")
    
    return usuarios_unicos

if __name__ == "__main__":
    busqueda_exhaustiva_usuarios() 