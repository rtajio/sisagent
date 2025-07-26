#!/usr/bin/env python3
"""
Script para verificar usuarios y operaciones en backups locales
"""

import os
import sqlite3
from datetime import datetime

def verificar_usuarios_db(db_path):
    """Verificar usuarios y operaciones en una base de datos SQLite"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar usuarios
        cursor.execute("SELECT id, username, nombre, es_admin, activo FROM usuario")
        usuarios = cursor.fetchall()
        
        # Verificar operaciones
        cursor.execute("""
            SELECT o.id, o.monto, o.comision, o.hora, u.username 
            FROM operacion o 
            JOIN usuario u ON o.usuario_id = u.id 
            ORDER BY o.hora DESC
        """)
        operaciones = cursor.fetchall()
        
        conn.close()
        
        return {
            'usuarios': usuarios,
            'operaciones': operaciones
        }
        
    except Exception as e:
        print(f"❌ Error con {db_path}: {e}")
        return None

def main():
    print("🔍 VERIFICANDO USUARIOS Y OPERACIONES EN BACKUPS")
    print("=" * 60)
    
    # Usar el backup con más operaciones
    db_file = 'instance/sisagent.db'
    
    if os.path.exists(db_file):
        print(f"\n📁 Analizando: {db_file}")
        print("-" * 40)
        
        result = verificar_usuarios_db(db_file)
        if result:
            print(f"👥 USUARIOS ({len(result['usuarios'])}):")
            for user in result['usuarios']:
                print(f"  - ID: {user[0]}, Username: {user[1]}, Nombre: {user[2]}, Admin: {user[3]}, Activo: {user[4]}")
            
            print(f"\n📊 OPERACIONES ({len(result['operaciones'])}):")
            for op in result['operaciones']:
                print(f"  - ID: {op[0]}, Monto: {op[1]}, Comisión: {op[2]}, Usuario: {op[4]}, Hora: {op[3]}")
            
            return result
        else:
            print("❌ No válida o sin datos")
    else:
        print(f"❌ No existe: {db_file}")
        return None

if __name__ == "__main__":
    main() 