#!/usr/bin/env python3
"""
Script para investigar el problema del usuario 73800418
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Operacion, Usuario

def investigar_usuario_73800418():
    """Investigar el problema del usuario 73800418"""
    with app.app_context():
        try:
            print("🔍 INVESTIGANDO USUARIO 73800418")
            print("=" * 60)
            
            # Buscar el usuario
            usuario = Usuario.query.filter_by(username='73800418').first()
            if not usuario:
                print("❌ Usuario 73800418 no encontrado")
                return
            
            print(f"✅ Usuario encontrado: ID={usuario.id}, Nombre={usuario.nombre}")
            
            # Todas las operaciones del usuario
            todas_operaciones = Operacion.query.filter_by(
                usuario_id=usuario.id
            ).order_by(Operacion.hora.desc()).all()
            
            print(f"\n📊 TODAS las operaciones del usuario ({len(todas_operaciones)}):")
            for op in todas_operaciones:
                print(f"  - ID: {op.id}, Monto: {op.monto}, Comisión: {op.comision}, Hora: {op.hora}")
            
            # Operaciones de hoy
            peru_tz = pytz.timezone('America/Lima')
            hoy = datetime.now(peru_tz).date()
            
            operaciones_hoy = Operacion.query.filter_by(
                usuario_id=usuario.id
            ).filter(
                db.func.date(Operacion.hora) == hoy
            ).order_by(Operacion.hora.desc()).all()
            
            print(f"\n📅 Operaciones de HOY ({hoy}) ({len(operaciones_hoy)}):")
            for op in operaciones_hoy:
                print(f"  - ID: {op.id}, Monto: {op.monto}, Comisión: {op.comision}, Hora: {op.hora}")
            
            # Verificar si hay operaciones duplicadas
            print(f"\n🔍 VERIFICANDO DUPLICADOS:")
            montos_hoy = [op.monto for op in operaciones_hoy]
            montos_unicos = set(montos_hoy)
            print(f"  - Montos únicos hoy: {len(montos_unicos)}")
            print(f"  - Total operaciones hoy: {len(montos_hoy)}")
            
            if len(montos_hoy) != len(montos_unicos):
                print("⚠️  ¡HAY DUPLICADOS!")
                for monto in montos_unicos:
                    count = montos_hoy.count(monto)
                    if count > 1:
                        print(f"    - Monto {monto} aparece {count} veces")
            
            # Verificar operaciones recientes (últimas 24 horas)
            ayer = hoy - timedelta(days=1)
            operaciones_recientes = Operacion.query.filter_by(
                usuario_id=usuario.id
            ).filter(
                Operacion.hora >= ayer
            ).order_by(Operacion.hora.desc()).all()
            
            print(f"\n🕐 Operaciones últimas 24 horas ({len(operaciones_recientes)}):")
            for op in operaciones_recientes:
                print(f"  - ID: {op.id}, Monto: {op.monto}, Comisión: {op.comision}, Hora: {op.hora}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    investigar_usuario_73800418() 