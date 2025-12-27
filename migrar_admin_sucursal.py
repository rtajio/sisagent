#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar la base de datos y agregar el campo es_admin_sucursal
"""

import os
import sys
import sqlite3

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def migrar_base_datos():
    """Agregar campo es_admin_sucursal a la tabla usuario si no existe"""
    
    print("=" * 80)
    print("🔄 MIGRACIÓN: Agregar campo es_admin_sucursal")
    print("=" * 80)
    print()
    
    # Buscar bases de datos
    db_files = [
        "instance/sisagent_consolidada.db",
        "sisagent_consolidada.db",
        "instance/sisagent.db",
        "sisagent.db"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                print(f"📂 Procesando: {db_file}")
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Verificar si existe la tabla usuario
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
                if not cursor.fetchone():
                    print(f"   ⚠️  La tabla 'usuario' no existe")
                    conn.close()
                    continue
                
                # Verificar si la columna ya existe
                cursor.execute("PRAGMA table_info(usuario)")
                columnas = [col[1] for col in cursor.fetchall()]
                
                if 'es_admin_sucursal' in columnas:
                    print(f"   ✅ La columna 'es_admin_sucursal' ya existe")
                else:
                    print(f"   🔧 Agregando columna 'es_admin_sucursal'...")
                    try:
                        cursor.execute("ALTER TABLE usuario ADD COLUMN es_admin_sucursal BOOLEAN DEFAULT 0")
                        conn.commit()
                        print(f"   ✅ Columna 'es_admin_sucursal' agregada exitosamente")
                    except Exception as e:
                        print(f"   ❌ Error al agregar columna: {e}")
                
                conn.close()
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
    
    print("=" * 80)
    print("✅ MIGRACIÓN COMPLETADA")
    print("=" * 80)

if __name__ == "__main__":
    migrar_base_datos()

