#!/usr/bin/env python3
"""
Script para inicializar solo las tablas en Railway (sin crear datos duplicados)
"""

import os
from app import app, db, Usuario, Sucursal, MedioPago, Operacion

def init_database():
    """Inicializar solo las tablas en Railway"""
    
    print("🚀 Inicializando tablas en Railway...")
    
    with app.app_context():
        try:
            # Crear todas las tablas
            print("📋 Creando tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Verificar si ya existen datos
            if Usuario.query.first():
                print("✅ Base de datos ya tiene datos - no se crearán duplicados")
                return
            
            print("✅ Base de datos lista para usar")
            print("📝 Nota: Los datos se pueden agregar manualmente desde la aplicación")
            
        except Exception as e:
            print(f"❌ Error al inicializar tablas: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_database()
