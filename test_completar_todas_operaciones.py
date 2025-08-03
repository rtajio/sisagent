#!/usr/bin/env python3
"""
Script para completar todas las operaciones de un tareo y verificar el cambio de estado
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Tareo, OperacionTareo, Usuario
from datetime import datetime
import pytz

def completar_todas_operaciones():
    """Completar todas las operaciones de un tareo y verificar el cambio de estado"""
    
    with app.app_context():
        print("=== COMPLETAR TODAS LAS OPERACIONES DE UN TAREO ===\n")
        
        # Buscar un tareo existente
        tareo = Tareo.query.first()
        if not tareo:
            print("❌ No se encontró ningún tareo en la base de datos")
            return
        
        print(f"📋 Tareo encontrado: {tareo.nombre}")
        print(f"   Estado inicial: {tareo.estado}")
        print(f"   Usuario asignado: {tareo.usuario.nombre_completo}")
        
        # Obtener operaciones del tareo
        operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
        print(f"\n📊 Operaciones del tareo: {len(operaciones)}")
        
        if not operaciones:
            print("❌ No hay operaciones en este tareo")
            return
        
        # Mostrar estado inicial
        print("\n🔍 Estado inicial de las operaciones:")
        completadas_inicial = 0
        for i, op in enumerate(operaciones, 1):
            estado = "✅ Completada" if op.completado else "⏳ Pendiente"
            print(f"   {i}. {op.nombre} ({op.medio}) - {estado}")
            if op.completado:
                completadas_inicial += 1
        
        print(f"\n📈 Estado inicial: {completadas_inicial}/{len(operaciones)} operaciones completadas")
        
        # Completar todas las operaciones pendientes
        print("\n🔄 Completando todas las operaciones pendientes...")
        operaciones_completadas = 0
        
        for op in operaciones:
            if not op.completado:
                op.completado = True
                op.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
                operaciones_completadas += 1
                print(f"   ✅ Completada: {op.nombre}")
        
        if operaciones_completadas == 0:
            print("   ℹ️  Todas las operaciones ya estaban completadas")
        
        # Calcular nuevo estado del tareo
        from sqlalchemy import func, case
        
        stats = db.session.query(
            func.count(OperacionTareo.id).label('total'),
            func.sum(case((OperacionTareo.completado == True, 1), else_=0)).label('completadas')
        ).filter(OperacionTareo.tareo_id == tareo.id).first()
        
        total_operaciones = stats.total or 0
        operaciones_completadas_total = stats.completadas or 0
        
        print(f"\n📊 Después de completar operaciones:")
        print(f"   Total operaciones: {total_operaciones}")
        print(f"   Operaciones completadas: {operaciones_completadas_total}")
        
        # Actualizar estado del tareo
        if operaciones_completadas_total == total_operaciones and total_operaciones > 0:
            tareo.estado = 'completado'
            tareo.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
            print("   → Tareo marcado como COMPLETADO")
        elif operaciones_completadas_total > 0:
            tareo.estado = 'en_progreso'
            print("   → Tareo marcado como EN PROGRESO")
        else:
            tareo.estado = 'pendiente'
            print("   → Tareo marcado como PENDIENTE")
        
        # Guardar cambios
        db.session.commit()
        print("✅ Cambios guardados en la base de datos")
        
        # Verificar resultado final
        db.session.refresh(tareo)
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   Estado del tareo: {tareo.estado}")
        print(f"   Fecha completado del tareo: {tareo.fecha_completado}")
        
        # Verificar que todas las operaciones estén completadas
        operaciones_final = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
        completadas_final = sum(1 for op in operaciones_final if op.completado)
        
        print(f"   Operaciones completadas: {completadas_final}/{len(operaciones_final)}")
        
        if tareo.estado == 'completado':
            print("\n🎉 ¡ÉXITO! El tareo está marcado como COMPLETADO")
        else:
            print(f"\n⚠️  El tareo no está marcado como completado. Estado actual: {tareo.estado}")

def verificar_fecha_tareo():
    """Verificar si el tareo está habilitado para el día actual"""
    
    with app.app_context():
        print("\n=== VERIFICACIÓN DE FECHA DEL TAREO ===\n")
        
        tareo = Tareo.query.first()
        if not tareo:
            print("❌ No se encontró ningún tareo")
            return
        
        fecha_actual = datetime.now(pytz.timezone('America/Lima')).date()
        fecha_tareo = tareo.fecha_creacion.date()
        
        print(f"📅 Fecha actual: {fecha_actual}")
        print(f"📅 Fecha del tareo: {fecha_tareo}")
        print(f"📅 Fecha de creación del tareo: {tareo.fecha_creacion}")
        
        if fecha_actual == fecha_tareo:
            print("✅ El tareo está habilitado para el día actual")
        else:
            print("❌ El tareo NO está habilitado para el día actual")
            print("   Esto significa que las operaciones no se pueden completar")

if __name__ == "__main__":
    verificar_fecha_tareo()
    completar_todas_operaciones()
    print("\n=== PRUEBA COMPLETADA ===") 