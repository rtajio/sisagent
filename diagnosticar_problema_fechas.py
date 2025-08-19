#!/usr/bin/env python3
"""
Script para diagnosticar el problema específico de fechas en reportes.
Verifica por qué se están mostrando operaciones del 18/08/2025 desde las 19:00:00
cuando se filtra por 19/08/2025.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Operacion
from datetime import datetime, timedelta
import pytz

def diagnosticar_problema_fechas():
    """Diagnosticar el problema específico de fechas"""
    
    print("🔍 DIAGNÓSTICO ESPECÍFICO DE FECHAS")
    print("=" * 50)
    
    with app.app_context():
        # Obtener zona horaria de Perú
        peru_tz = pytz.timezone('America/Lima')
        
        # Fechas específicas del problema
        fecha_18 = datetime(2025, 8, 18).date()
        fecha_19 = datetime(2025, 8, 19).date()
        
        print(f"📅 Fecha 18/08/2025: {fecha_18}")
        print(f"📅 Fecha 19/08/2025: {fecha_19}")
        
        # 1. Verificar operaciones del 18/08/2025
        print(f"\n1️⃣ Operaciones del 18/08/2025:")
        operaciones_18 = Operacion.query.filter(
            db.func.date(Operacion.hora) == fecha_18
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"   Total operaciones del 18/08/2025: {len(operaciones_18)}")
        
        # Mostrar operaciones después de las 19:00 del 18/08/2025
        operaciones_18_19 = []
        for op in operaciones_18:
            if op.hora.hour >= 19:
                operaciones_18_19.append(op)
        
        print(f"   Operaciones del 18/08/2025 después de las 19:00: {len(operaciones_18_19)}")
        
        for op in operaciones_18_19:
            print(f"   - ID: {op.id}, Hora: {op.hora}, Fecha: {op.hora.date()}, Comisión: {op.comision}")
        
        # 2. Verificar operaciones del 19/08/2025
        print(f"\n2️⃣ Operaciones del 19/08/2025:")
        operaciones_19 = Operacion.query.filter(
            db.func.date(Operacion.hora) == fecha_19
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"   Total operaciones del 19/08/2025: {len(operaciones_19)}")
        
        for op in operaciones_19[:10]:  # Mostrar las primeras 10
            print(f"   - ID: {op.id}, Hora: {op.hora}, Fecha: {op.hora.date()}, Comisión: {op.comision}")
        
        # 3. Probar filtro específico que debería usar el reporte
        print(f"\n3️⃣ Probando filtro específico para reporte (fecha_inicio=19/08/2025, fecha_fin=19/08/2025):")
        
        # Simular el filtro del reporte
        query = Operacion.query
        query = query.filter(db.func.date(Operacion.hora) >= fecha_19)
        query = query.filter(db.func.date(Operacion.hora) <= fecha_19)
        
        operaciones_filtradas = query.order_by(Operacion.hora.desc()).all()
        
        print(f"   Operaciones encontradas con filtro: {len(operaciones_filtradas)}")
        
        # Verificar si hay operaciones del 18/08/2025 en el resultado
        operaciones_incorrectas = []
        for op in operaciones_filtradas:
            if op.hora.date() == fecha_18:
                operaciones_incorrectas.append(op)
        
        if operaciones_incorrectas:
            print(f"   ❌ PROBLEMA ENCONTRADO: {len(operaciones_incorrectas)} operaciones del 18/08/2025 aparecen en el filtro del 19/08/2025")
            for op in operaciones_incorrectas:
                print(f"      - ID: {op.id}, Hora: {op.hora}, Fecha: {op.hora.date()}")
        else:
            print(f"   ✅ Correcto: No hay operaciones del 18/08/2025 en el filtro del 19/08/2025")
        
        # 4. Verificar el formato de las fechas en la base de datos
        print(f"\n4️⃣ Verificando formato de fechas en la base de datos:")
        
        # Obtener algunas operaciones para ver el formato
        operaciones_muestra = Operacion.query.order_by(Operacion.hora.desc()).limit(5).all()
        
        for op in operaciones_muestra:
            print(f"   - ID: {op.id}")
            print(f"     Hora completa: {op.hora}")
            print(f"     Tipo de dato: {type(op.hora)}")
            print(f"     Tiene timezone: {op.hora.tzinfo is not None}")
            if op.hora.tzinfo:
                print(f"     Timezone: {op.hora.tzinfo}")
            print(f"     Fecha extraída: {op.hora.date()}")
            print(f"     db.func.date(): {db.func.date(op.hora)}")
            print()
        
        # 5. Probar filtro alternativo usando timezone
        print(f"\n5️⃣ Probando filtro alternativo con timezone:")
        
        # Crear fechas con timezone
        inicio_19_peru = datetime.combine(fecha_19, datetime.min.time()).replace(tzinfo=peru_tz)
        fin_19_peru = datetime.combine(fecha_19, datetime.max.time()).replace(tzinfo=peru_tz)
        
        print(f"   Inicio 19/08/2025 (Perú): {inicio_19_peru}")
        print(f"   Fin 19/08/2025 (Perú): {fin_19_peru}")
        
        # Probar filtro con rango de tiempo
        query_tz = Operacion.query.filter(
            Operacion.hora >= inicio_19_peru,
            Operacion.hora <= fin_19_peru
        )
        
        operaciones_tz = query_tz.order_by(Operacion.hora.desc()).all()
        
        print(f"   Operaciones con filtro timezone: {len(operaciones_tz)}")
        
        # Verificar si hay operaciones del 18/08/2025
        operaciones_incorrectas_tz = []
        for op in operaciones_tz:
            if op.hora.date() == fecha_18:
                operaciones_incorrectas_tz.append(op)
        
        if operaciones_incorrectas_tz:
            print(f"   ❌ PROBLEMA PERSISTE: {len(operaciones_incorrectas_tz)} operaciones del 18/08/2025 aparecen")
        else:
            print(f"   ✅ Filtro timezone funciona correctamente")
        
        # 6. Recomendación de solución
        print(f"\n6️⃣ RECOMENDACIÓN DE SOLUCIÓN:")
        
        if operaciones_incorrectas:
            print(f"   🔧 El problema está en el filtro db.func.date()")
            print(f"   🔧 Se recomienda usar filtro con timezone específico")
            print(f"   🔧 Modificar la función api_reportes_operaciones")
        else:
            print(f"   ✅ El filtro actual funciona correctamente")
            print(f"   🔍 El problema podría estar en otro lugar")

if __name__ == "__main__":
    diagnosticar_problema_fechas() 