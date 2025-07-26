#!/usr/bin/env python3
"""
Script para verificar los backups de base de datos locales
"""

import os
import sqlite3
from datetime import datetime

def verificar_db(db_path):
    """Verificar una base de datos SQLite"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si existe la tabla operacion
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operacion'")
        if not cursor.fetchone():
            return None
        
        # Contar operaciones totales
        cursor.execute("SELECT COUNT(*) FROM operacion")
        total_operaciones = cursor.fetchone()[0]
        
        # Contar operaciones del usuario 73800418
        cursor.execute("SELECT COUNT(*) FROM operacion WHERE usuario_id = (SELECT id FROM usuario WHERE username = '73800418')")
        operaciones_usuario = cursor.fetchone()[0]
        
        # Obtener operaciones del usuario 73800418
        cursor.execute("""
            SELECT o.id, o.monto, o.comision, o.hora, u.username 
            FROM operacion o 
            JOIN usuario u ON o.usuario_id = u.id 
            WHERE u.username = '73800418' 
            ORDER BY o.hora DESC
        """)
        operaciones = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_operaciones': total_operaciones,
            'operaciones_usuario': operaciones_usuario,
            'operaciones': operaciones
        }
        
    except Exception as e:
        print(f"❌ Error con {db_path}: {e}")
        return None

def main():
    print("🔍 VERIFICANDO BACKUPS DE BASE DE DATOS")
    print("=" * 60)
    
    # Lista de archivos de base de datos
    db_files = [
        'instance/sisagent.db',
        'instance/sisagent_consolidada.db', 
        'instance/sisagent_protegida.db',
        'instance/sisagent_final.db',
        'instance/sisagent_simple.db',
        'instance/sisagent_definitivo.db'
    ]
    
    mejores_backups = []
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n📁 Verificando: {db_file}")
            print("-" * 40)
            
            result = verificar_db(db_file)
            if result:
                print(f"✅ Total operaciones: {result['total_operaciones']}")
                print(f"✅ Operaciones usuario 73800418: {result['operaciones_usuario']}")
                
                if result['operaciones_usuario'] > 0:
                    print("📋 Últimas operaciones del usuario:")
                    for op in result['operaciones'][:5]:  # Mostrar solo las últimas 5
                        print(f"  - ID: {op[0]}, Monto: {op[1]}, Comisión: {op[2]}, Hora: {op[3]}")
                
                mejores_backups.append({
                    'file': db_file,
                    'total': result['total_operaciones'],
                    'usuario': result['operaciones_usuario']
                })
            else:
                print("❌ No válida o sin datos")
        else:
            print(f"❌ No existe: {db_file}")
    
    # Mostrar el mejor backup
    if mejores_backups:
        print("\n🏆 MEJOR BACKUP ENCONTRADO:")
        print("=" * 60)
        
        mejor = max(mejores_backups, key=lambda x: x['usuario'])
        print(f"📁 Archivo: {mejor['file']}")
        print(f"📊 Total operaciones: {mejor['total']}")
        print(f"👤 Operaciones usuario 73800418: {mejor['usuario']}")
        
        return mejor['file']
    else:
        print("\n❌ No se encontraron backups válidos")
        return None

if __name__ == "__main__":
    mejor_backup = main() 