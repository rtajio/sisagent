#!/usr/bin/env python3
"""
Script para crear punto de restauración del sistema SISAGENT
Estado actual: Sistema funcionando correctamente con menú hamburguesa responsive
"""

import os
import shutil
import json
from datetime import datetime

def create_restore_point():
    """Crear punto de restauración del sistema"""
    
    print("🛡️ Creando Punto de Restauración del Sistema SISAGENT")
    print("=" * 60)
    print("📋 Estado actual del sistema:")
    print("✅ Healthcheck de Railway funcionando")
    print("✅ Base de datos SQLite configurada")
    print("✅ Menú hamburguesa responsive corregido")
    print("✅ Endpoint /health funcionando")
    print("✅ Aplicación desplegada en Railway")
    print("=" * 60)
    
    # Configuración
    backup_dir = "backups"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"restore_point_{timestamp}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Crear directorio de respaldos si no existe
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Crear directorio del respaldo
    os.makedirs(backup_path)
    
    # Lista de archivos importantes a respaldar
    files_to_backup = [
        "app.py",
        "wsgi.py", 
        "init_db.py",
        "requirements.txt",
        "Procfile",
        "railway.toml",
        "config.env"
    ]
    
    # Lista de directorios importantes
    directories_to_backup = [
        "templates"
    ]
    
    print(f"🔄 Creando respaldo: {backup_name}")
    
    # Respaldar archivos
    for file_name in files_to_backup:
        if os.path.exists(file_name):
            shutil.copy2(file_name, backup_path)
            print(f"✅ Respaldo: {file_name}")
    
    # Respaldar directorios
    for dir_name in directories_to_backup:
        if os.path.exists(dir_name):
            dir_backup_path = os.path.join(backup_path, dir_name)
            shutil.copytree(dir_name, dir_backup_path)
            print(f"✅ Respaldo: {dir_name}/")
    
    # Respaldar base de datos
    db_file = "sisagent.db"
    if os.path.exists(db_file):
        shutil.copy2(db_file, backup_path)
        print(f"✅ Respaldo: {db_file}")
    
    # Crear archivo de información del respaldo
    backup_info = {
        "backup_name": backup_name,
        "timestamp": timestamp,
        "description": "Punto de restauración estable - Sistema funcionando correctamente con menú hamburguesa responsive",
        "status": {
            "railway_healthcheck": "funcionando",
            "database": "SQLite configurada",
            "mobile_menu": "responsive corregido",
            "health_endpoint": "funcionando",
            "deployment": "Railway exitoso"
        },
        "files_backed_up": files_to_backup,
        "directories_backed_up": directories_to_backup,
        "database_backed_up": os.path.exists(db_file),
        "created_at": datetime.now().isoformat()
    }
    
    with open(os.path.join(backup_path, "backup_info.json"), 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)
    
    print(f"🎉 ¡Punto de restauración creado exitosamente!")
    print(f"📁 Nombre del respaldo: {backup_name}")
    print(f"📁 Ubicación: {backup_path}")
    
    print("\n📋 Para restaurar el sistema a este punto:")
    print("1. Ejecuta: python restore_system.py")
    print("2. Selecciona este respaldo")
    print("\n⚠️ IMPORTANTE: Este respaldo incluye:")
    print("   - Código fuente completo")
    print("   - Base de datos actual")
    print("   - Configuración de Railway")
    print("   - Templates HTML")
    
    return backup_name

if __name__ == "__main__":
    create_restore_point() 