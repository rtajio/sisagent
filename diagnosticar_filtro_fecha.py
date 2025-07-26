#!/usr/bin/env python3
"""
Script específico para diagnosticar el problema del filtro de fecha en reportes
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

def diagnosticar_filtro_fecha():
    print("🔍 DIAGNÓSTICO DE FILTRO DE FECHA")
    print("=" * 50)
    
    # 1. Buscar sucursal TECKNOVATION
    sucursal = Sucursal.query.filter_by(nombre='TECKNOVATION').first()
    if not sucursal:
        print("❌ Sucursal TECKNOVATION no encontrada")
        return
    
    print(f"🏢 Sucursal: {sucursal.nombre} (ID: {sucursal.id})")
    
    # 2. Simular el filtro exacto que está fallando
    fecha_inicio = "2025-07-26"  # Fecha que envía el frontend
    fecha_fin = "2025-07-26"     # Fecha que envía el frontend
    sucursal_id = str(sucursal.id)
    
    print(f"\n🔍 SIMULANDO FILTRO EXACTO:")
    print(f"  fecha_inicio: '{fecha_inicio}'")
    print(f"  fecha_fin: '{fecha_fin}'")
    print(f"  sucursal_id: '{sucursal_id}'")
    
    # 3. Procesar fechas como en la función de reportes
    query = Operacion.query
    
    if fecha_inicio:
        fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        inicio_dia_peru = datetime.combine(fecha_inicio_obj, datetime.min.time()).replace(tzinfo=peru_tz)
        inicio_dia_utc_naive = inicio_dia_peru.astimezone(pytz.utc).replace(tzinfo=None)
        query = query.filter(Operacion.hora >= inicio_dia_utc_naive)
        
        print(f"\n📅 PROCESAMIENTO FECHA INICIO:")
        print(f"  fecha_inicio_obj: {fecha_inicio_obj}")
        print(f"  inicio_dia_peru: {inicio_dia_peru}")
        print(f"  inicio_dia_utc_naive: {inicio_dia_utc_naive}")
    
    if fecha_fin:
        fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        fin_dia_peru = datetime.combine(fecha_fin_obj, datetime.max.time()).replace(tzinfo=peru_tz)
        fin_dia_utc_naive = fin_dia_peru.astimezone(pytz.utc).replace(tzinfo=None)
        query = query.filter(Operacion.hora <= fin_dia_utc_naive)
        
        print(f"\n📅 PROCESAMIENTO FECHA FIN:")
        print(f"  fecha_fin_obj: {fecha_fin_obj}")
        print(f"  fin_dia_peru: {fin_dia_peru}")
        print(f"  fin_dia_utc_naive: {fin_dia_utc_naive}")
    
    if sucursal_id and sucursal_id.strip():
        try:
            sucursal_id_int = int(sucursal_id)
            query = query.filter(Operacion.sucursal_id == sucursal_id_int)
            print(f"\n🏢 FILTRO SUCURSAL: {sucursal_id_int}")
        except ValueError:
            print(f"❌ Error al convertir sucursal_id '{sucursal_id}' a integer")
    
    # 4. Ejecutar query
    operaciones = query.order_by(Operacion.hora.desc()).all()
    
    print(f"\n📊 RESULTADOS:")
    print(f"  Total operaciones encontradas: {len(operaciones)}")
    
    # 5. Agrupar por fecha para ver qué fechas aparecen
    operaciones_por_fecha = {}
    for op in operaciones:
        fecha = op.hora.date()
        if fecha not in operaciones_por_fecha:
            operaciones_por_fecha[fecha] = []
        operaciones_por_fecha[fecha].append(op)
    
    print(f"\n📅 OPERACIONES POR FECHA:")
    for fecha in sorted(operaciones_por_fecha.keys(), reverse=True):
        ops = operaciones_por_fecha[fecha]
        total_fecha = sum(float(op.comision) for op in ops)
        print(f"  {fecha}: {len(ops)} operaciones, Total comisión: S/ {total_fecha:.2f}")
        
        # Mostrar las primeras 3 operaciones de cada fecha
        for op in ops[:3]:
            print(f"    - ID: {op.id}, Hora: {op.hora}, Comisión: S/ {op.comision}")
        if len(ops) > 3:
            print(f"    ... y {len(ops) - 3} operaciones más")
    
    # 6. Verificar si hay operaciones fuera del rango esperado
    fecha_esperada = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    operaciones_fuera_rango = []
    
    for op in operaciones:
        if op.hora.date() != fecha_esperada:
            operaciones_fuera_rango.append(op)
    
    if operaciones_fuera_rango:
        print(f"\n❌ PROBLEMA ENCONTRADO:")
        print(f"  Se encontraron {len(operaciones_fuera_rango)} operaciones fuera del rango esperado")
        print(f"  Fecha esperada: {fecha_esperada}")
        print(f"  Fechas encontradas: {list(set(op.hora.date() for op in operaciones_fuera_rango))}")
        
        # Mostrar algunas operaciones problemáticas
        print(f"\n🔍 OPERACIONES PROBLEMÁTICAS (primeras 5):")
        for op in operaciones_fuera_rango[:5]:
            print(f"  - ID: {op.id}, Fecha: {op.hora.date()}, Hora: {op.hora}, Comisión: S/ {op.comision}")
    else:
        print(f"\n✅ FILTRO FUNCIONANDO CORRECTAMENTE")
        print(f"  Todas las operaciones están en la fecha esperada: {fecha_esperada}")
    
    # 7. Calcular totales
    total_comision = sum(float(op.comision) for op in operaciones)
    print(f"\n💰 TOTALES:")
    print(f"  Total comisión: S/ {total_comision:.2f}")
    print(f"  Total operaciones: {len(operaciones)}")

if __name__ == "__main__":
    with app.app_context():
        diagnosticar_filtro_fecha() 