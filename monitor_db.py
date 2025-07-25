#!/usr/bin/env python3
"""
Script de Monitoreo de Base de Datos
"""

import os
import time
import sqlite3
from datetime import datetime

def monitorear_db():
    db_path = "instance/sisagent_protegida.db"
    
    if not os.path.exists(db_path):
        print(f"❌ ALERTA: Base de datos no encontrada en {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas principales
        cursor.execute("SELECT COUNT(*) FROM usuario")
        usuarios = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM operacion")
        operaciones = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sucursal")
        sucursales = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ DB OK - Usuarios: {usuarios}, Operaciones: {operaciones}, Sucursales: {sucursales}")
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

if __name__ == "__main__":
    while True:
        monitorear_db()
        time.sleep(30)  # Verificar cada 30 segundos
