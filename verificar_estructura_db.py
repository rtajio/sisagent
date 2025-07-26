#!/usr/bin/env python3
"""
Script para verificar la estructura de las tablas en backups
"""

import os
import sqlite3

def verificar_estructura(db_path):
    """Verificar estructura de tablas"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = cursor.fetchall()
        
        print(f"\n📋 TABLAS EN {db_path}:")
        for tabla in tablas:
            print(f"  - {tabla[0]}")
            
            # Verificar estructura de cada tabla
            cursor.execute(f"PRAGMA table_info({tabla[0]})")
            columnas = cursor.fetchall()
            print(f"    Columnas:")
            for col in columnas:
                print(f"      - {col[1]} ({col[2]})")
        
        # Verificar datos en usuario
        try:
            cursor.execute("SELECT * FROM usuario LIMIT 3")
            usuarios = cursor.fetchall()
            print(f"\n👥 USUARIOS (primeros 3):")
            for user in usuarios:
                print(f"  - {user}")
        except Exception as e:
            print(f"❌ Error leyendo usuarios: {e}")
        
        # Verificar datos en operacion
        try:
            cursor.execute("SELECT * FROM operacion LIMIT 3")
            operaciones = cursor.fetchall()
            print(f"\n📊 OPERACIONES (primeras 3):")
            for op in operaciones:
                print(f"  - {op}")
        except Exception as e:
            print(f"❌ Error leyendo operaciones: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error con {db_path}: {e}")

def main():
    print("🔍 VERIFICANDO ESTRUCTURA DE BACKUPS")
    print("=" * 60)
    
    db_file = 'instance/sisagent.db'
    
    if os.path.exists(db_file):
        verificar_estructura(db_file)
    else:
        print(f"❌ No existe: {db_file}")

if __name__ == "__main__":
    main() 