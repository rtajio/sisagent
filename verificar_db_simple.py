#!/usr/bin/env python3
"""
Script para verificar y corregir la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def verificar_db_simple():
    """Verificar y corregir la base de datos"""

    print("🔍 VERIFICANDO BASE DE DATOS")
    print("=" * 40)

    with app.app_context():
        try:
            # Verificar tablas existentes
            print("📊 Verificando tablas...")
            tablas = db.session.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)).fetchall()
            
            for tabla in tablas:
                print(f"   ✅ {tabla.name}")
            
            # Verificar si existe la tabla medio_pago
            if not any(tabla.name == 'medio_pago' for tabla in tablas):
                print("❌ Tabla medio_pago no encontrada")
                print("🔧 Creando tabla medio_pago...")
                
                # Crear tabla medio_pago
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS medio_pago (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_abreviado VARCHAR(20) UNIQUE NOT NULL,
                        nombre_completo VARCHAR(100) NOT NULL,
                        activo BOOLEAN DEFAULT 1,
                        orden INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # Insertar medios de pago básicos
                db.session.execute(text("""
                    INSERT OR IGNORE INTO medio_pago (nombre_abreviado, nombre_completo, activo, orden)
                    VALUES 
                    ('EFECTIVO', 'Efectivo', 1, 1),
                    ('YAPE', 'Yape', 1, 2),
                    ('PLIN', 'Plin', 1, 3),
                    ('TRANSFERENCIA', 'Transferencia Bancaria', 1, 4),
                    ('DEPOSITO', 'Depósito Bancario', 1, 5)
                """))
                
                db.session.commit()
                print("✅ Tabla medio_pago creada y poblada")
            
            # Verificar si existe la tabla medio_sucursal
            if not any(tabla.name == 'medio_sucursal' for tabla in tablas):
                print("❌ Tabla medio_sucursal no encontrada")
                print("🔧 Creando tabla medio_sucursal...")
                
                db.session.execute(text("""
                    CREATE TABLE IF NOT EXISTS medio_sucursal (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sucursal_id INTEGER NOT NULL,
                        medio_pago_id INTEGER NOT NULL,
                        activo BOOLEAN DEFAULT 1,
                        FOREIGN KEY (sucursal_id) REFERENCES sucursal (id),
                        FOREIGN KEY (medio_pago_id) REFERENCES medio_pago (id)
                    )
                """))
                
                db.session.commit()
                print("✅ Tabla medio_sucursal creada")
            
            print("\n🎯 VERIFICACIÓN COMPLETADA")
            print("   - Base de datos verificada")
            print("   - Tablas faltantes creadas")
            print("   - Sistema listo para usar")

        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    verificar_db_simple() 