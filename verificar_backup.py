#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificar que el backup no modificó la base de datos original"""

import sqlite3
import os
import sys

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 80)
print("🔍 VERIFICANDO QUE EL BACKUP NO MODIFICÓ LA BASE DE DATOS")
print("=" * 80)
print()

# Verificar base de datos original
db_files = [
    "sisagent_consolidada.db",
    "instance/sisagent_consolidada.db",
    "instance/sisagent.db"
]

for db_file in db_files:
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Verificar si existe la tabla
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM usuario")
                total = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM usuario WHERE username='admin'")
                tiene_admin = cursor.fetchone()[0] > 0
                
                cursor.execute("SELECT username FROM usuario LIMIT 5")
                usuarios = [row[0] for row in cursor.fetchall()]
                
                print(f"✅ {db_file}:")
                print(f"   - Total usuarios: {total}")
                print(f"   - Tiene admin: {'Sí' if tiene_admin else 'No'}")
                print(f"   - Primeros usuarios: {', '.join(usuarios)}")
                print()
            else:
                print(f"⚠️  {db_file}: No tiene tabla 'usuario'")
                print()
            
            conn.close()
        except Exception as e:
            print(f"❌ Error al verificar {db_file}: {e}")
            print()

print("=" * 80)
print("✅ Verificación completada")
print("=" * 80)

