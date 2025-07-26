#!/usr/bin/env python3
"""
Script para diagnosticar inconsistencias en el dashboard del usuario
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Operacion, Usuario

def diagnosticar_inconsistencia():
    """Diagnosticar inconsistencias en el dashboard"""
    with app.app_context():
        try:
            print("🔍 DIAGNÓSTICO DE INCONSISTENCIAS EN DASHBOARD")
            print("=" * 60)
            
            # Buscar el usuario 73800418
            usuario = Usuario.query.filter_by(username='73800418').first()
            if not usuario:
                print("❌ Usuario 73800418 no encontrado")
                return
            
            print(f"✅ Usuario 73800418: ID={usuario.id}, Nombre={usuario.nombre_completo}")
            
            # Obtener fecha actual en Perú
            peru_tz = pytz.timezone('America/Lima')
            hoy = datetime.now(peru_tz).date()
            ahora = datetime.now(peru_tz)
            
            print(f"\n📅 Fecha actual en Perú: {hoy}")
            print(f"🕐 Hora actual en Perú: {ahora}")
            
            # Todas las operaciones del usuario
            todas_operaciones = Operacion.query.filter_by(
                usuario_id=usuario.id
            ).order_by(Operacion.hora.desc()).all()
            
            print(f"\n📊 TODAS las operaciones del usuario ({len(todas_operaciones)}):")
            for op in todas_operaciones:
                fecha_op = op.hora.date()
                print(f"  - ID: {op.id}, Monto: {op.monto}, Comisión: {op.comision}, Hora: {op.hora}, Fecha: {fecha_op}")
            
            # Operaciones de hoy (según filtro del dashboard)
            operaciones_hoy = Operacion.query.filter_by(
                usuario_id=usuario.id
            ).filter(
                db.func.date(Operacion.hora) == hoy
            ).order_by(Operacion.hora.desc()).all()
            
            print(f"\n📅 Operaciones de HOY según filtro ({len(operaciones_hoy)}):")
            for op in operaciones_hoy:
                print(f"  - ID: {op.id}, Monto: {op.monto}, Comisión: {op.comision}, Hora: {op.hora}")
            
            # Calcular comisión de hoy
            total_comision_hoy = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0)).filter(
                Operacion.usuario_id == usuario.id,
                db.func.date(Operacion.hora) == hoy
            ).scalar() or 0
            
            print(f"\n💰 Comisión total de hoy: S/ {total_comision_hoy}")
            print(f"📊 Cantidad de operaciones de hoy: {len(operaciones_hoy)}")
            
            # Verificar operaciones recientes (últimas 24 horas)
            hace_24_horas = ahora - timedelta(hours=24)
            operaciones_recientes = Operacion.query.filter_by(
                usuario_id=usuario.id
            ).filter(
                Operacion.hora >= hace_24_horas
            ).order_by(Operacion.hora.desc()).all()
            
            print(f"\n🕐 Operaciones últimas 24 horas ({len(operaciones_recientes)}):")
            for op in operaciones_recientes:
                fecha_op = op.hora.date()
                print(f"  - ID: {op.id}, Monto: {op.monto}, Comisión: {op.comision}, Hora: {op.hora}, Fecha: {fecha_op}")
            
            # Verificar si hay operaciones con fechas diferentes
            fechas_unicas = set(op.hora.date() for op in todas_operaciones)
            print(f"\n📅 Fechas únicas de operaciones: {fechas_unicas}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    diagnosticar_inconsistencia() 