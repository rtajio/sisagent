#!/usr/bin/env python3
"""
Script de Restauración del Backup Pre-Deploy Vouchers
"""

import os
import shutil
import sys
from datetime import datetime

def restaurar_backup():
    """Restaurar el sistema desde el backup"""
    
    print("🔄 Iniciando restauración del sistema...")
    
    # Verificar que existe el backup
    backup_dir = "backup_pre_vouchers_20250824_131706"
    if not os.path.exists(backup_dir):
        print("❌ No se encontró el directorio de backup")
        return False
    
    try:
        # 1. Restaurar base de datos
        if os.path.exists(f"backup_pre_vouchers_20250824_131706/sisagent.db"):
            shutil.copy2(f"backup_pre_vouchers_20250824_131706/sisagent.db", "sisagent.db")
            print("✅ Base de datos restaurada")
        
        # 2. Restaurar archivos principales
        archivos_principales = [
            'app.py', 'config.py', 'requirements.txt', 'Procfile',
            'runtime.txt', 'railway.json', 'railway.toml', 'wsgi.py',
            'gunicorn.conf.py'
        ]
        
        for archivo in archivos_principales:
            if os.path.exists(f"backup_pre_vouchers_20250824_131706/README_OPTIMIZED.md"):
                shutil.copy2(f"backup_pre_vouchers_20250824_131706/README_OPTIMIZED.md", archivo)
                print(f"✅ {archivo} restaurado")
        
        # 3. Restaurar templates
        if os.path.exists(f"backup_pre_vouchers_20250824_131706/templates"):
            if os.path.exists("templates"):
                shutil.rmtree("templates")
            shutil.copytree(f"backup_pre_vouchers_20250824_131706/templates", "templates")
            print("✅ Templates restaurados")
        
        # 4. Restaurar archivos de configuración
        archivos_config = ['.env', '.gitignore', 'README.md', 'README_OPTIMIZED.md']
        for archivo in archivos_config:
            if os.path.exists(f"backup_pre_vouchers_20250824_131706/README_OPTIMIZED.md"):
                shutil.copy2(f"backup_pre_vouchers_20250824_131706/README_OPTIMIZED.md", archivo)
                print(f"✅ {archivo} restaurado")
        
        # 5. Restaurar instance
        if os.path.exists(f"backup_pre_vouchers_20250824_131706/instance"):
            if os.path.exists("instance"):
                shutil.rmtree("instance")
            shutil.copytree(f"backup_pre_vouchers_20250824_131706/instance", "instance")
            print("✅ Directorio instance restaurado")
        
        # 6. Restaurar logs
        if os.path.exists(f"backup_pre_vouchers_20250824_131706/logs"):
            if os.path.exists("logs"):
                shutil.rmtree("logs")
            shutil.copytree(f"backup_pre_vouchers_20250824_131706/logs", "logs")
            print("✅ Logs restaurados")
        
        print("✅ Restauración completada exitosamente")
        print("🔄 El sistema ha sido restaurado al estado anterior al deploy de vouchers")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la restauración: {e}")
        return False

if __name__ == '__main__':
    restaurar_backup()
