#!/usr/bin/env python3
"""
Script para diagnosticar la inconsistencia entre dashboard y reportes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import Operacion, Sucursal
from datetime import datetime
import pytz

def diagnosticar_inconsistencia():
    """Diagnosticar por qué hay diferencias entre dashboard y reportes"""
    
    print("🔍 DIAGNÓSTICO DE INCONSISTENCIA DASHBOARD vs REPORTES")
    print("=" * 60)
    
    with app.app_context():
        # Obtener zona horaria de Perú
        peru_tz = pytz.timezone('America/Lima')
        ahora = datetime.now(peru_tz)
        hoy = ahora.date()
        
        print(f"📅 Fecha actual en Perú: {hoy}")
        print(f"🕐 Hora actual en Perú: {ahora}")
        
        # Método 1: Dashboard (usando db.func.date)
        print("\n📊 MÉTODO 1: Dashboard (db.func.date)")
        print("-" * 40)
        
        comisiones_dashboard = db.session.query(
            Operacion.sucursal_id,
            db.func.sum(Operacion.comision).label('total')
        ).filter(
            db.func.date(Operacion.hora) == hoy
        ).group_by(Operacion.sucursal_id).all()
        
        for cd in comisiones_dashboard:
            sucursal = Sucursal.query.get(cd.sucursal_id)
            print(f"   - {sucursal.nombre}: S/ {cd.total}")
        
        # Método 2: Reportes (usando rangos de tiempo)
        print("\n📊 MÉTODO 2: Reportes (rangos de tiempo)")
        print("-" * 40)
        
        inicio_fecha = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=peru_tz)
        fin_fecha = datetime.combine(hoy, datetime.max.time()).replace(tzinfo=peru_tz)
        
        comisiones_reportes = db.session.query(
            Operacion.sucursal_id,
            db.func.sum(Operacion.comision).label('total')
        ).filter(
            Operacion.hora >= inicio_fecha,
            Operacion.hora <= fin_fecha
        ).group_by(Operacion.sucursal_id).all()
        
        for cr in comisiones_reportes:
            sucursal = Sucursal.query.get(cr.sucursal_id)
            print(f"   - {sucursal.nombre}: S/ {cr.total}")
        
        # Verificar operaciones específicas de TECKNOVATION
        print("\n🔍 VERIFICACIÓN ESPECÍFICA: TECKNOVATION")
        print("-" * 40)
        
        tecknovation = Sucursal.query.filter_by(nombre='TECKNOVATION').first()
        if tecknovation:
            print(f"   Sucursal ID: {tecknovation.id}")
            
            # Operaciones usando método dashboard
            ops_dashboard = Operacion.query.filter(
                Operacion.sucursal_id == tecknovation.id,
                db.func.date(Operacion.hora) == hoy
            ).all()
            
            print(f"   Operaciones (Dashboard): {len(ops_dashboard)}")
            for op in ops_dashboard:
                print(f"     - ID: {op.id}, Hora: {op.hora}, Comisión: S/ {op.comision}")
            
            # Operaciones usando método reportes
            ops_reportes = Operacion.query.filter(
                Operacion.sucursal_id == tecknovation.id,
                Operacion.hora >= inicio_fecha,
                Operacion.hora <= fin_fecha
            ).all()
            
            print(f"   Operaciones (Reportes): {len(ops_reportes)}")
            for op in ops_reportes:
                print(f"     - ID: {op.id}, Hora: {op.hora}, Comisión: S/ {op.comision}")
        
        # Verificar todas las operaciones de hoy
        print("\n🔍 TODAS LAS OPERACIONES DE HOY")
        print("-" * 40)
        
        todas_ops = Operacion.query.filter(
            db.func.date(Operacion.hora) == hoy
        ).order_by(Operacion.hora).all()
        
        print(f"   Total operaciones de hoy: {len(todas_ops)}")
        for op in todas_ops:
            sucursal = Sucursal.query.get(op.sucursal_id)
            print(f"     - {sucursal.nombre}: {op.hora} - S/ {op.comision}")

if __name__ == "__main__":
    diagnosticar_inconsistencia() 