#!/usr/bin/env python3
"""
Script de inicio inteligente para SISAGENT
Solo inicializa la base de datos cuando es necesario y hace respaldo automático
"""

import os
import sys
from pathlib import Path

def backup_database():
    """Hacer respaldo automático de la base de datos"""
    try:
        from backup_db import backup_database as backup_db_func
        return backup_db_func()
    except ImportError:
        print("⚠️ Script de respaldo no disponible")
        return None

def check_database_exists():
    """Verificar si la base de datos ya existe"""
    db_file = "sisagent.db"
    return Path(db_file).exists()

def check_database_initialized():
    """Verificar si la base de datos ya está inicializada"""
    try:
        from app import app, db, Usuario
        
        with app.app_context():
            # Verificar si existe al menos un usuario admin
            admin_exists = Usuario.query.filter_by(username='admin').first()
            return admin_exists is not None
    except Exception as e:
        print(f"⚠️ Error verificando base de datos: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando SISAGENT...")
    
    # Hacer respaldo automático antes de cualquier operación
    print("🛡️ Creando respaldo automático de la base de datos...")
    backup_path = backup_database()
    if backup_path:
        print(f"✅ Respaldo creado: {backup_path}")
    
    # Usar inicialización SEGURA que preserva datos existentes
    print("🔧 Ejecutando inicialización SEGURA (preserva datos existentes)...")
    os.system("python init_db_safe.py")
    
    print("🎯 Iniciando aplicación con Gunicorn...")
    
    # Obtener el puerto de las variables de entorno
    port = os.environ.get('PORT', '5000')
    
    # Comando para iniciar Gunicorn
    gunicorn_cmd = f"gunicorn wsgi:application --bind 0.0.0.0:{port} --workers 2 --timeout 120"
    
    print(f"🚀 Ejecutando: {gunicorn_cmd}")
    os.system(gunicorn_cmd)

if __name__ == "__main__":
    main() 