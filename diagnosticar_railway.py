#!/usr/bin/env python3
"""
Script de diagnóstico para Railway - verificar el problema con reportes
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Configuración de zona horaria
peru_tz = pytz.timezone('America/Lima')

def diagnosticar_railway():
    print("🔍 DIAGNÓSTICO DE RAILWAY")
    print("=" * 50)
    
    # 1. Obtener información actual
    ahora_peru = datetime.now(peru_tz)
    hoy_peru = ahora_peru.date()
    print(f"📅 Hora actual en Perú: {ahora_peru}")
    print(f"📅 Fecha actual en Perú: {hoy_peru}")
    
    # 2. Calcular rangos de tiempo para hoy
    inicio_dia_peru = datetime.combine(hoy_peru, datetime.min.time()).replace(tzinfo=peru_tz)
    fin_dia_peru = datetime.combine(hoy_peru, datetime.max.time()).replace(tzinfo=peru_tz)
    
    inicio_dia_utc_naive = inicio_dia_peru.astimezone(pytz.utc).replace(tzinfo=None)
    fin_dia_utc_naive = fin_dia_peru.astimezone(pytz.utc).replace(tzinfo=None)
    
    print(f"⏰ Inicio del día (Peru): {inicio_dia_peru}")
    print(f"⏰ Fin del día (Peru): {fin_dia_peru}")
    print(f"⏰ Inicio del día (UTC Naive): {inicio_dia_utc_naive}")
    print(f"⏰ Fin del día (UTC Naive): {fin_dia_utc_naive}")
    
    # 3. Simular filtro de reporte para "hoy"
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
    
    # 4. Verificar si los rangos son iguales
    print(f"\n🔍 COMPARACIÓN DE RANGOS:")
    print(f"  Dashboard inicio: {inicio_dia_utc_naive}")
    print(f"  Reporte inicio:   {inicio_dia_utc_naive_reporte}")
    print(f"  Dashboard fin:    {fin_dia_utc_naive}")
    print(f"  Reporte fin:      {fin_dia_utc_naive_reporte}")
    
    if inicio_dia_utc_naive == inicio_dia_utc_naive_reporte and fin_dia_utc_naive == fin_dia_utc_naive_reporte:
        print("✅ Los rangos de tiempo son IDÉNTICOS")
    else:
        print("❌ Los rangos de tiempo son DIFERENTES")
    
    # 5. Verificar zona horaria
    print(f"\n🌍 INFORMACIÓN DE ZONA HORARIA:")
    print(f"  Zona horaria Perú: {peru_tz}")
    print(f"  Offset actual: {ahora_peru.utcoffset()}")
    print(f"  DST activo: {ahora_peru.dst()}")
    
    # 6. Verificar fechas de ayer y mañana
    ayer = hoy_peru - timedelta(days=1)
    mañana = hoy_peru + timedelta(days=1)
    
    print(f"\n📅 FECHAS ADICIONALES:")
    print(f"  Ayer: {ayer}")
    print(f"  Hoy: {hoy_peru}")
    print(f"  Mañana: {mañana}")
    
    # 7. Simular filtro para ayer
    fecha_ayer_str = ayer.strftime('%Y-%m-%d')
    fecha_ayer_obj = datetime.strptime(fecha_ayer_str, '%Y-%m-%d').date()
    inicio_ayer_peru = datetime.combine(fecha_ayer_obj, datetime.min.time()).replace(tzinfo=peru_tz)
    inicio_ayer_utc_naive = inicio_ayer_peru.astimezone(pytz.utc).replace(tzinfo=None)
    fin_ayer_peru = datetime.combine(fecha_ayer_obj, datetime.max.time()).replace(tzinfo=peru_tz)
    fin_ayer_utc_naive = fin_ayer_peru.astimezone(pytz.utc).replace(tzinfo=None)
    
    print(f"\n🔍 FILTRO PARA AYER ({fecha_ayer_str}):")
    print(f"  Inicio ayer (UTC Naive): {inicio_ayer_utc_naive}")
    print(f"  Fin ayer (UTC Naive): {fin_ayer_utc_naive}")

if __name__ == "__main__":
    diagnosticar_railway() 