#!/usr/bin/env python3
"""
Script para crear solo las tablas en Railway (sin tocar datos existentes)
"""

import os
from app import app, db

def init_database():
    """Crear solo las tablas en Railway"""
    
    print("🚀 Creando tablas en Railway...")
    
    with app.app_context():
        try:
            # Solo crear las tablas
            print("📋 Creando tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            print("📝 Nota: Los datos existentes se mantienen intactos")
            
        except Exception as e:
            print(f"❌ Error al crear tablas: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_database()
