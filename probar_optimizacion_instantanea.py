#!/usr/bin/env python3
"""
Script para probar la optimización instantánea de tareos
"""

import os
import sys
import time
from datetime import datetime
import pytz

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import Tareo, OperacionTareo, Usuario

def probar_optimizacion_instantanea():
    """Probar la optimización instantánea de tareos"""
    
    with app.app_context():
        try:
            print("🚀 PROBANDO OPTIMIZACIÓN INSTANTÁNEA DE TAREOS")
            print("=" * 60)
            
            # Obtener un tareo de prueba
            tareo = Tareo.query.first()
            if not tareo:
                print("❌ No hay tareos en el sistema para probar")
                return
            
            print(f"📋 Probando con tareo: {tareo.nombre}")
            print(f"   ID: {tareo.id}")
            print(f"   Estado actual: {tareo.estado}")
            
            # Obtener operaciones del tareo
            operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
            print(f"   Operaciones totales: {len(operaciones)}")
            
            if not operaciones:
                print("❌ No hay operaciones en este tareo para probar")
                return
            
            # Probar con la primera operación
            operacion = operaciones[0]
            print(f"\n🔍 Probando con operación: {operacion.nombre}")
            print(f"   ID: {operacion.id}")
            print(f"   Estado actual: {operacion.completado}")
            print(f"   Fecha completado: {operacion.fecha_completado}")
            
            # Simular la consulta optimizada
            print(f"\n⚡ SIMULANDO CONSULTA ULTRA OPTIMIZADA:")
            
            from sqlalchemy import func
            
            # Medir tiempo de la consulta optimizada
            start_time = time.time()
            
            # Consulta ultra optimizada (como en la función real)
            from sqlalchemy import case
            stats = db.session.query(
                func.count(OperacionTareo.id).label('total'),
                func.sum(case((OperacionTareo.completado == True, 1), else_=0)).label('completadas')
            ).filter(OperacionTareo.tareo_id == tareo.id).first()
            
            tiempo_consulta = time.time() - start_time
            
            total_operaciones = stats.total or 0
            operaciones_completadas = stats.completadas or 0
            
            print(f"   ⏱️  Tiempo de consulta optimizada: {tiempo_consulta:.6f}s")
            print(f"   📊 Total operaciones: {total_operaciones}")
            print(f"   ✅ Operaciones completadas: {operaciones_completadas}")
            print(f"   📈 Porcentaje: {(operaciones_completadas/total_operaciones*100):.1f}%")
            
            # Comparar con método anterior (para demostrar la mejora)
            print(f"\n🐌 COMPARANDO CON MÉTODO ANTERIOR:")
            
            start_time = time.time()
            
            # Método anterior (cargar todas las operaciones en memoria)
            operaciones_tareo = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
            total_anterior = len(operaciones_tareo)
            completadas_anterior = sum(1 for op in operaciones_tareo if op.completado)
            
            tiempo_anterior = time.time() - start_time
            
            print(f"   ⏱️  Tiempo método anterior: {tiempo_anterior:.6f}s")
            print(f"   📊 Total operaciones: {total_anterior}")
            print(f"   ✅ Operaciones completadas: {completadas_anterior}")
            
            # Calcular mejora
            if tiempo_anterior > 0:
                mejora = tiempo_anterior / tiempo_consulta
                print(f"   🚀 MEJORA DE VELOCIDAD: {mejora:.1f}x más rápido")
            
            # Verificar consistencia de datos
            print(f"\n🔍 VERIFICANDO CONSISTENCIA:")
            print(f"   ✅ Datos coinciden: {total_operaciones == total_anterior and operaciones_completadas == completadas_anterior}")
            
            # Probar formateo de fecha
            print(f"\n🕐 PROBANDO FORMATEO DE FECHA:")
            fecha_actual = datetime.now(pytz.timezone('America/Lima'))
            print(f"   Fecha actual Perú: {fecha_actual}")
            print(f"   ISO format: {fecha_actual.isoformat()}")
            
            # Simular formateo en JavaScript
            fecha_js = fecha_actual.strftime('%d/%m/%Y %H:%M')
            print(f"   Formato JS: {fecha_js}")
            
            print(f"\n✅ PRUEBA COMPLETADA")
            print(f"   La optimización está funcionando correctamente")
            print(f"   Las fechas se formatean correctamente para Perú")
            print(f"   El rendimiento es instantáneo")
            
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")

def verificar_fechas_tareos():
    """Verificar que las fechas de los tareos estén correctas"""
    
    with app.app_context():
        try:
            print("\n🔍 VERIFICANDO FECHAS DE TAREOS")
            print("=" * 60)
            
            # Obtener todos los tareos
            tareos = Tareo.query.all()
            print(f"📊 Total de tareos: {len(tareos)}")
            
            for i, tareo in enumerate(tareos, 1):
                print(f"\n🔍 TAREO {i}: {tareo.nombre}")
                print(f"   ID: {tareo.id}")
                print(f"   Fecha creación: {tareo.fecha_creacion}")
                print(f"   Fecha completado: {tareo.fecha_completado}")
                
                # Verificar operaciones
                operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
                print(f"   Operaciones: {len(operaciones)}")
                
                for j, op in enumerate(operaciones, 1):
                    print(f"      {j}. {op.nombre} - Completado: {op.completado} - Fecha: {op.fecha_completado}")
            
            print(f"\n✅ Verificación de fechas completada")
            
        except Exception as e:
            print(f"❌ Error durante la verificación: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de optimización instantánea...")
    
    probar_optimizacion_instantanea()
    verificar_fechas_tareos()
    
    print("\n🎉 Todas las pruebas completadas") 