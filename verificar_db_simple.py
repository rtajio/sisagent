#!/usr/bin/env python3
"""
Script simple para verificar la base de datos
"""

import os
import sys

# Configurar variables de entorno para Railway
os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/sisagent'

try:
    from app import app, db
    
    with app.app_context():
        print("🔍 Verificando base de datos...")
        
        # Verificar conexión
        with db.engine.connect() as conn:
            result = conn.execute(db.text("SELECT COUNT(*) FROM operacion"))
            count = result.fetchone()[0]
            print(f"✅ Operaciones en la base de datos: {count}")
            
            # Verificar usuarios
            result = conn.execute(db.text("SELECT COUNT(*) FROM usuario"))
            count = result.fetchone()[0]
            print(f"✅ Usuarios en la base de datos: {count}")
            
            # Verificar sucursales
            result = conn.execute(db.text("SELECT COUNT(*) FROM sucursal"))
            count = result.fetchone()[0]
            print(f"✅ Sucursales en la base de datos: {count}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔍 Verificando configuración...")
    
    # Verificar variables de entorno
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'No configurada')}")
    
    # Verificar archivos
    if os.path.exists('app.py'):
        print("✅ app.py existe")
    else:
        print("❌ app.py no existe") 