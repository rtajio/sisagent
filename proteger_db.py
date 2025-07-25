#!/usr/bin/env python3
"""
Sistema de Protección de Base de Datos
"""

import os
import shutil
import time
from datetime import datetime

def proteger_base_datos():
    db_principal = "instance/sisagent_consolidada.db"
    db_backup = "instance/sisagent_backup.db"
    
    # Crear backup automático cada hora
    if os.path.exists(db_principal):
        # Verificar si necesitamos hacer backup
        if not os.path.exists(db_backup) or            (time.time() - os.path.getmtime(db_backup)) > 3600:  # 1 hora
            
            shutil.copy2(db_principal, db_backup)
            print(f"🔄 Backup automático creado: {datetime.now()}")
    
    # Verificar integridad
    if os.path.exists(db_principal):
        tamaño = os.path.getsize(db_principal)
        if tamaño < 1000:  # Si es muy pequeño, restaurar
            if os.path.exists(db_backup):
                shutil.copy2(db_backup, db_principal)
                print("🔄 Base de datos restaurada desde backup")
                return False
        return True
    return False

if __name__ == "__main__":
    while True:
        proteger_base_datos()
        time.sleep(300)  # Verificar cada 5 minutos
