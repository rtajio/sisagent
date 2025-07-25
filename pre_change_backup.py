#!/usr/bin/env python3
"""
Script para hacer respaldo antes de cambios importantes
"""

import os
import shutil
from datetime import datetime
from pathlib import Path

def create_pre_change_backup():
    """Crear respaldo antes de cambios importantes"""
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
    backup_name = f"pre_change_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    
    try:
        # Hacer copia de la base de datos
        shutil.copy2(db_file, backup_path)
        
        # Obtener información del archivo
        file_size = os.path.getsize(backup_path)
        size_mb = file_size / (1024 * 1024)
        
        print("🛡️ Respaldo de seguridad creado antes de cambios")
        print(f"📁 Archivo: {backup_name}")
        print(f"📊 Tamaño: {size_mb:.2f} MB")
        print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ Puedes proceder con los cambios de forma segura")
        
        return backup_path
    except Exception as e:
        print(f"❌ Error al crear respaldo: {e}")
        return None

def main():
    """Función principal"""
    print("🛡️ Respaldo de Seguridad SISAGENT")
    print("=" * 40)
    print("Este script crea un respaldo de la base de datos")
    print("antes de hacer cambios importantes en el sistema.")
    print("=" * 40)
    
    confirm = input("¿Crear respaldo de seguridad? (sí/no): ").lower()
    if confirm in ['sí', 'si', 'yes', 'y', 's']:
        backup_path = create_pre_change_backup()
        if backup_path:
            print(f"\n🎯 Respaldo creado exitosamente en: {backup_path}")
            print("💡 Para restaurar más tarde, usa: python backup_db.py restore N")
        else:
            print("❌ No se pudo crear el respaldo")
    else:
        print("❌ Respaldo cancelado")

if __name__ == "__main__":
    main() 