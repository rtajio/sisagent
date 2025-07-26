#!/usr/bin/env python3
"""
Script para verificar el estado de las operaciones en la base de datos
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Operacion, Usuario, Sucursal

def verificar_operaciones():
    """Verificar el estado de las operaciones"""
    with app.app_context():
        try:
            # Verificar conexión a la base de datos
            print("🔍 Verificando conexión a la base de datos...")
            db.engine.execute("SELECT 1")
            print("✅ Conexión exitosa")
            
            # Contar operaciones
            total_operaciones = Operacion.query.count()
            print(f"📊 Total de operaciones: {total_operaciones}")
            
            # Operaciones de hoy
            peru_tz = pytz.timezone('America/Lima')
            hoy = datetime.now(peru_tz).date()
            
            operaciones_hoy = Operacion.query.filter(
                db.func.date(Operacion.hora) == hoy
            ).count()
            print(f"📅 Operaciones de hoy ({hoy}): {operaciones_hoy}")
            
            # Últimas 5 operaciones
            ultimas_operaciones = Operacion.query.order_by(
                Operacion.hora.desc()
            ).limit(5).all()
            
            print("\n🕐 Últimas 5 operaciones:")
            for op in ultimas_operaciones:
                print(f"  - ID: {op.id}, Monto: {op.monto}, Hora: {op.hora}")
            
            # Verificar usuarios y sucursales
            total_usuarios = Usuario.query.count()
            total_sucursales = Sucursal.query.count()
            print(f"\n👥 Total usuarios: {total_usuarios}")
            print(f"🏢 Total sucursales: {total_sucursales}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN DE OPERACIONES")
    print("=" * 50)
    verificar_operaciones() 