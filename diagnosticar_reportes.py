#!/usr/bin/env python3
"""
Script de diagnóstico para verificar el problema con reportes
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pytz

# Configuración de zona horaria
peru_tz = pytz.timezone('America/Lima')

# Configuración de la aplicación Flask
app = Flask(__name__)

# Configuración para Railway
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Usando PostgreSQL en Railway: {database_url[:20]}...")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_consolidada.db'
    print("✅ Usando SQLite para desarrollo local")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos
class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    activa = db.Column(db.Boolean, default=True)

class Operacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    comision = db.Column(db.Numeric(10, 2), nullable=False)
    medio = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.DateTime, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=True)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(100), nullable=False)

def diagnosticar_problema():
    print("🔍 DIAGNÓSTICO DE REPORTES")
    print("=" * 50)
    
    # 1. Obtener información actual
    ahora_peru = datetime.now(peru_tz)
    hoy_peru = ahora_peru.date()
    print(f"📅 Hora actual en Perú: {ahora_peru}")
    print(f"📅 Fecha actual en Perú: {hoy_peru}")
    
    # 2. Buscar sucursal TECKNOVATION
    sucursal = Sucursal.query.filter_by(nombre='TECKNOVATION').first()
    if not sucursal:
        print("❌ Sucursal TECKNOVATION no encontrada")
        return
    
    print(f"🏢 Sucursal encontrada: {sucursal.nombre} (ID: {sucursal.id})")
    
    # 3. Calcular rangos de tiempo para hoy
    inicio_dia_peru = datetime.combine(hoy_peru, datetime.min.time()).replace(tzinfo=peru_tz)
    fin_dia_peru = datetime.combine(hoy_peru, datetime.max.time()).replace(tzinfo=peru_tz)
    
    inicio_dia_utc_naive = inicio_dia_peru.astimezone(pytz.utc).replace(tzinfo=None)
    fin_dia_utc_naive = fin_dia_peru.astimezone(pytz.utc).replace(tzinfo=None)
    
    print(f"⏰ Inicio del día (Peru): {inicio_dia_peru}")
    print(f"⏰ Fin del día (Peru): {fin_dia_peru}")
    print(f"⏰ Inicio del día (UTC Naive): {inicio_dia_utc_naive}")
    print(f"⏰ Fin del día (UTC Naive): {fin_dia_utc_naive}")
    
    # 4. Buscar operaciones de TECKNOVATION para hoy (método dashboard)
    operaciones_hoy = db.session.query(Operacion).filter(
        Operacion.sucursal_id == sucursal.id,
        Operacion.hora >= inicio_dia_utc_naive,
        Operacion.hora <= fin_dia_utc_naive
    ).order_by(Operacion.hora.desc()).all()
    
    print(f"\n📊 OPERACIONES DE HOY (método dashboard): {len(operaciones_hoy)}")
    total_comision_hoy = sum(float(op.comision) for op in operaciones_hoy)
    print(f"💰 Total comisión de hoy: S/ {total_comision_hoy:.2f}")
    
    for op in operaciones_hoy:
        print(f"  - ID: {op.id}, Hora: {op.hora}, Fecha: {op.hora.date()}, Comisión: S/ {op.comision}")
    
    # 5. Buscar TODAS las operaciones de TECKNOVATION
    todas_operaciones = db.session.query(Operacion).filter(
        Operacion.sucursal_id == sucursal.id
    ).order_by(Operacion.hora.desc()).all()
    
    print(f"\n📊 TODAS LAS OPERACIONES DE TECKNOVATION: {len(todas_operaciones)}")
    
    # Agrupar por fecha
    operaciones_por_fecha = {}
    for op in todas_operaciones:
        fecha = op.hora.date()
        if fecha not in operaciones_por_fecha:
            operaciones_por_fecha[fecha] = []
        operaciones_por_fecha[fecha].append(op)
    
    for fecha in sorted(operaciones_por_fecha.keys(), reverse=True):
        ops = operaciones_por_fecha[fecha]
        total_fecha = sum(float(op.comision) for op in ops)
        print(f"  📅 {fecha}: {len(ops)} operaciones, Total: S/ {total_fecha:.2f}")
        for op in ops[:3]:  # Mostrar solo las primeras 3
            print(f"    - ID: {op.id}, Hora: {op.hora}, Comisión: S/ {op.comision}")
        if len(ops) > 3:
            print(f"    ... y {len(ops) - 3} operaciones más")
    
    # 6. Simular filtro de reporte para "hoy"
    fecha_hoy_str = hoy_peru.strftime('%Y-%m-%d')
    print(f"\n🔍 SIMULANDO FILTRO DE REPORTE PARA: {fecha_hoy_str}")
    
    # Procesar como en reportes
    fecha_inicio_obj = datetime.strptime(fecha_hoy_str, '%Y-%m-%d').date()
    inicio_dia_peru_reporte = datetime.combine(fecha_inicio_obj, datetime.min.time()).replace(tzinfo=peru_tz)
    inicio_dia_utc_naive_reporte = inicio_dia_peru_reporte.astimezone(pytz.utc).replace(tzinfo=None)
    
    fecha_fin_obj = datetime.strptime(fecha_hoy_str, '%Y-%m-%d').date()
    fin_dia_peru_reporte = datetime.combine(fecha_fin_obj, datetime.max.time()).replace(tzinfo=peru_tz)
    fin_dia_utc_naive_reporte = fin_dia_peru_reporte.astimezone(pytz.utc).replace(tzinfo=None)
    
    print(f"⏰ Inicio reporte (Peru): {inicio_dia_peru_reporte}")
    print(f"⏰ Fin reporte (Peru): {fin_dia_peru_reporte}")
    print(f"⏰ Inicio reporte (UTC Naive): {inicio_dia_utc_naive_reporte}")
    print(f"⏰ Fin reporte (UTC Naive): {fin_dia_utc_naive_reporte}")
    
    # Buscar operaciones con filtro de reporte
    operaciones_reporte = db.session.query(Operacion).filter(
        Operacion.sucursal_id == sucursal.id,
        Operacion.hora >= inicio_dia_utc_naive_reporte,
        Operacion.hora <= fin_dia_utc_naive_reporte
    ).order_by(Operacion.hora.desc()).all()
    
    print(f"\n📊 OPERACIONES CON FILTRO DE REPORTE: {len(operaciones_reporte)}")
    total_comision_reporte = sum(float(op.comision) for op in operaciones_reporte)
    print(f"💰 Total comisión reporte: S/ {total_comision_reporte:.2f}")
    
    for op in operaciones_reporte:
        print(f"  - ID: {op.id}, Hora: {op.hora}, Fecha: {op.hora.date()}, Comisión: S/ {op.comision}")
    
    # 7. Verificar si hay diferencias
    print(f"\n🔍 COMPARACIÓN:")
    print(f"  Dashboard: {len(operaciones_hoy)} operaciones, S/ {total_comision_hoy:.2f}")
    print(f"  Reporte: {len(operaciones_reporte)} operaciones, S/ {total_comision_reporte:.2f}")
    
    if len(operaciones_hoy) != len(operaciones_reporte):
        print("❌ ¡DIFERENCIA ENCONTRADA! Los métodos no coinciden")
        
        # Encontrar diferencias
        ids_dashboard = {op.id for op in operaciones_hoy}
        ids_reporte = {op.id for op in operaciones_reporte}
        
        solo_dashboard = ids_dashboard - ids_reporte
        solo_reporte = ids_reporte - ids_dashboard
        
        if solo_dashboard:
            print(f"  Operaciones solo en dashboard: {solo_dashboard}")
        if solo_reporte:
            print(f"  Operaciones solo en reporte: {solo_reporte}")
    else:
        print("✅ Los métodos coinciden")

if __name__ == "__main__":
    with app.app_context():
        diagnosticar_problema() 