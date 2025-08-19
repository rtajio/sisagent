#!/usr/bin/env python3
"""
Script para eliminar las tablas de comisiones que ya no se necesitan
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def eliminar_tablas_comisiones():
    """Eliminar tablas de comisiones para optimizar el sistema"""

    print("🗑️ ELIMINANDO TABLAS DE COMISIONES")
    print("=" * 50)

    with app.app_context():
        try:
            # Eliminar tabla comision_diaria
            print("📊 Eliminando tabla comision_diaria...")
            db.session.execute(text("DROP TABLE IF EXISTS comision_diaria"))
            
            # Eliminar tabla comision_mensual
            print("📊 Eliminando tabla comision_mensual...")
            db.session.execute(text("DROP TABLE IF EXISTS comision_mensual"))
            
            db.session.commit()
            print("✅ Tablas de comisiones eliminadas exitosamente")
            
            # Verificar que las tablas se eliminaron
            print("\n🔍 Verificando tablas restantes...")
            tablas = db.session.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)).fetchall()
            
            for tabla in tablas:
                print(f"   ✅ {tabla.name}")
            
            print("\n🎯 OPTIMIZACIÓN COMPLETADA")
            print("   - Tablas de comisiones eliminadas")
            print("   - Sistema optimizado para registro instantáneo")
            print("   - Comisiones se calculan en tiempo real")

        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == "__main__":
    eliminar_tablas_comisiones() 