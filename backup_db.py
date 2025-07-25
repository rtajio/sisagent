#!/usr/bin/env python3
"""
Script para hacer respaldo automático de la base de datos
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_database():
    """Hacer respaldo de la base de datos"""
    db_file = "sisagent.db"
    
    if not Path(db_file).exists():
        print("📊 No hay base de datos para respaldar")
        return None
    
    # Crear directorio de respaldos si no existe
    backup_dir = "database_backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generar nombre del respaldo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"db_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        # Hacer copia de la base de datos
        shutil.copy2(db_file, backup_path)
        print(f"✅ Respaldo de base de datos creado: {backup_name}")
        return backup_path
    except Exception as e:
        print(f"❌ Error al crear respaldo: {e}")
        return None

def restore_database(backup_path):
    """Restaurar base de datos desde un respaldo"""
    if not Path(backup_path).exists():
        print(f"❌ Archivo de respaldo no encontrado: {backup_path}")
        return False
    
    try:
        # Hacer respaldo del estado actual antes de restaurar
        current_backup = backup_database()
        
        # Restaurar desde el respaldo
        shutil.copy2(backup_path, "sisagent.db")
        print(f"✅ Base de datos restaurada desde: {backup_path}")
        
        if current_backup:
            print(f"📁 Respaldo del estado anterior: {current_backup}")
        
        return True
    except Exception as e:
        print(f"❌ Error al restaurar base de datos: {e}")
        return False

def list_backups():
    """Listar todos los respaldos disponibles"""
    backup_dir = "database_backups"
    
    if not os.path.exists(backup_dir):
        print("📁 No hay respaldos disponibles")
        return []
    
    backups = []
    for file in os.listdir(backup_dir):
        if file.endswith('.db'):
            file_path = os.path.join(backup_dir, file)
            file_size = os.path.getsize(file_path)
            file_time = os.path.getmtime(file_path)
            backups.append({
                'name': file,
                'path': file_path,
                'size': file_size,
                'time': file_time
            })
    
    # Ordenar por fecha (más reciente primero)
    backups.sort(key=lambda x: x['time'], reverse=True)
    
    if not backups:
        print("📁 No hay respaldos disponibles")
        return []
    
    print("📋 Respaldos de base de datos disponibles:")
    print("=" * 60)
    for i, backup in enumerate(backups, 1):
        size_mb = backup['size'] / (1024 * 1024)
        date_str = datetime.fromtimestamp(backup['time']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {backup['name']}")
        print(f"   📅 Fecha: {date_str}")
        print(f"   📊 Tamaño: {size_mb:.2f} MB")
        print("-" * 60)
    
    return backups

def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) < 2:
        print("🛡️ Script de Respaldo de Base de Datos SISAGENT")
        print("=" * 50)
        print("Uso:")
        print("  python backup_db.py backup     - Crear respaldo")
        print("  python backup_db.py list       - Listar respaldos")
        print("  python backup_db.py restore N  - Restaurar respaldo N")
        return
    
    command = sys.argv[1].lower()
    
    if command == "backup":
        backup_database()
    
    elif command == "list":
        list_backups()
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Debes especificar el número del respaldo a restaurar")
            return
        
        try:
            backup_index = int(sys.argv[2]) - 1
            backups = list_backups()
            
            if 0 <= backup_index < len(backups):
                backup_path = backups[backup_index]['path']
                confirm = input(f"⚠️ ¿Restaurar desde {backups[backup_index]['name']}? (sí/no): ").lower()
                if confirm in ['sí', 'si', 'yes', 'y', 's']:
                    restore_database(backup_path)
                else:
                    print("❌ Restauración cancelada")
            else:
                print("❌ Número de respaldo inválido")
        except ValueError:
            print("❌ Por favor ingresa un número válido")
    
    else:
        print(f"❌ Comando desconocido: {command}")

if __name__ == "__main__":
    main() 