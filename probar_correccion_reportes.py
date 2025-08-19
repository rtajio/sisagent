#!/usr/bin/env python3
"""
Script para probar la corrección específica de reportes con timezone
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Operacion
from datetime import datetime
import pytz

def probar_correccion_reportes():
    """Probar la corrección específica de reportes"""
    
    print("🔧 PROBANDO CORRECCIÓN DE REPORTES")
    print("=" * 50)
    
    with app.app_context():
        # Obtener zona horaria de Perú
        peru_tz = pytz.timezone('America/Lima')
        
        # Fechas específicas del problema
        fecha_18 = datetime(2025, 8, 18).date()
        fecha_19 = datetime(2025, 8, 19).date()
        
        print(f"📅 Fecha 18/08/2025: {fecha_18}")
        print(f"📅 Fecha 19/08/2025: {fecha_19}")
        
        # 1. Probar filtro antiguo (problemático)
        print(f"\n1️⃣ Probando filtro antiguo (db.func.date):")
        
        query_antiguo = Operacion.query
        query_antiguo = query_antiguo.filter(db.func.date(Operacion.hora) >= fecha_19)
        query_antiguo = query_antiguo.filter(db.func.date(Operacion.hora) <= fecha_19)
        
        operaciones_antiguo = query_antiguo.order_by(Operacion.hora.desc()).all()
        
        print(f"   Operaciones con filtro antiguo: {len(operaciones_antiguo)}")
        
        # Verificar si hay operaciones del 18/08/2025
        operaciones_incorrectas_antiguo = []
        for op in operaciones_antiguo:
            if op.hora.date() == fecha_18:
                operaciones_incorrectas_antiguo.append(op)
        
        if operaciones_incorrectas_antiguo:
            print(f"   ❌ PROBLEMA: {len(operaciones_incorrectas_antiguo)} operaciones del 18/08/2025 aparecen")
        else:
            print(f"   ✅ Correcto: No hay operaciones del 18/08/2025")
        
        # 2. Probar filtro nuevo (corregido)
        print(f"\n2️⃣ Probando filtro nuevo (timezone específico):")
        
        # Crear fechas con timezone
        inicio_19_peru = datetime.combine(fecha_19, datetime.min.time()).replace(tzinfo=peru_tz)
        fin_19_peru = datetime.combine(fecha_19, datetime.max.time()).replace(tzinfo=peru_tz)
        
        print(f"   Inicio 19/08/2025 (Perú): {inicio_19_peru}")
        print(f"   Fin 19/08/2025 (Perú): {fin_19_peru}")
        
        query_nuevo = Operacion.query
        query_nuevo = query_nuevo.filter(Operacion.hora >= inicio_19_peru)
        query_nuevo = query_nuevo.filter(Operacion.hora <= fin_19_peru)
        
        operaciones_nuevo = query_nuevo.order_by(Operacion.hora.desc()).all()
        
        print(f"   Operaciones con filtro nuevo: {len(operaciones_nuevo)}")
        
        # Verificar si hay operaciones del 18/08/2025
        operaciones_incorrectas_nuevo = []
        for op in operaciones_nuevo:
            if op.hora.date() == fecha_18:
                operaciones_incorrectas_nuevo.append(op)
        
        if operaciones_incorrectas_nuevo:
            print(f"   ❌ PROBLEMA: {len(operaciones_incorrectas_nuevo)} operaciones del 18/08/2025 aparecen")
        else:
            print(f"   ✅ Correcto: No hay operaciones del 18/08/2025")
        
        # 3. Comparar resultados
        print(f"\n3️⃣ Comparación de resultados:")
        
        if len(operaciones_antiguo) != len(operaciones_nuevo):
            print(f"   ⚠️  Los filtros devuelven diferentes cantidades:")
            print(f"      - Filtro antiguo: {len(operaciones_antiguo)} operaciones")
            print(f"      - Filtro nuevo: {len(operaciones_nuevo)} operaciones")
        else:
            print(f"   ✅ Ambos filtros devuelven la misma cantidad: {len(operaciones_antiguo)} operaciones")
        
        # 4. Verificar operaciones específicas
        print(f"\n4️⃣ Verificando operaciones específicas:")
        
        # Mostrar las primeras 5 operaciones de cada filtro
        print(f"   Filtro antiguo (primeras 5):")
        for i, op in enumerate(operaciones_antiguo[:5]):
            print(f"      {i+1}. ID: {op.id}, Hora: {op.hora}, Fecha: {op.hora.date()}")
        
        print(f"   Filtro nuevo (primeras 5):")
        for i, op in enumerate(operaciones_nuevo[:5]):
            print(f"      {i+1}. ID: {op.id}, Hora: {op.hora}, Fecha: {op.hora.date()}")
        
        # 5. Conclusión
        print(f"\n5️⃣ CONCLUSIÓN:")
        
        if operaciones_incorrectas_antiguo and not operaciones_incorrectas_nuevo:
            print(f"   ✅ La corrección funciona correctamente")
            print(f"   ✅ El filtro nuevo elimina las operaciones incorrectas")
        elif operaciones_incorrectas_antiguo and operaciones_incorrectas_nuevo:
            print(f"   ❌ El problema persiste en ambos filtros")
            print(f"   🔍 Se necesita investigación adicional")
        elif not operaciones_incorrectas_antiguo and not operaciones_incorrectas_nuevo:
            print(f"   ✅ Ambos filtros funcionan correctamente")
            print(f"   🔍 No hay operaciones problemáticas en la base de datos local")
        else:
            print(f"   ⚠️  Resultado inesperado")
            print(f"   🔍 Se necesita más análisis")

if __name__ == "__main__":
    probar_correccion_reportes() 