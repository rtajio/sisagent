#!/usr/bin/env python3
"""
Script para probar la actualización de estado de tareos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Tareo, OperacionTareo, Usuario
from datetime import datetime
import pytz

def test_tareo_status_update():
    """Probar la lógica de actualización de estado de tareos"""
    
    with app.app_context():
        print("=== PRUEBA DE ACTUALIZACIÓN DE ESTADO DE TAREOS ===\n")
        
        # Buscar un tareo existente
        tareo = Tareo.query.first()
        if not tareo:
            print("❌ No se encontró ningún tareo en la base de datos")
            return
        
        print(f"📋 Tareo encontrado: {tareo.nombre}")
        print(f"   Estado actual: {tareo.estado}")
        print(f"   Usuario asignado: {tareo.usuario.nombre_completo}")
        print(f"   Sucursal: {tareo.sucursal.nombre}")
        
        # Obtener operaciones del tareo
        operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
        print(f"\n📊 Operaciones del tareo: {len(operaciones)}")
        
        if not operaciones:
            print("❌ No hay operaciones en este tareo")
            return
        
        # Mostrar estado actual de cada operación
        print("\n🔍 Estado actual de las operaciones:")
        completadas = 0
        for i, op in enumerate(operaciones, 1):
            estado = "✅ Completada" if op.completado else "⏳ Pendiente"
            print(f"   {i}. {op.nombre} ({op.medio}) - {estado}")
            if op.completado:
                completadas += 1
        
        print(f"\n📈 Resumen: {completadas}/{len(operaciones)} operaciones completadas")
        
        # Simular la lógica de actualización de estado
        print("\n🔄 Simulando lógica de actualización de estado...")
        
        from sqlalchemy import func, case
        
        # Contar operaciones totales y completadas
        stats = db.session.query(
            func.count(OperacionTareo.id).label('total'),
            func.sum(case((OperacionTareo.completado == True, 1), else_=0)).label('completadas')
        ).filter(OperacionTareo.tareo_id == tareo.id).first()
        
        total_operaciones = stats.total or 0
        operaciones_completadas = stats.completadas or 0
        
        print(f"   Total operaciones: {total_operaciones}")
        print(f"   Operaciones completadas: {operaciones_completadas}")
        
        # Determinar el nuevo estado
        if operaciones_completadas == total_operaciones and total_operaciones > 0:
            nuevo_estado = 'completado'
            print("   → Estado debería ser: COMPLETADO")
        elif operaciones_completadas > 0:
            nuevo_estado = 'en_progreso'
            print("   → Estado debería ser: EN PROGRESO")
        else:
            nuevo_estado = 'pendiente'
            print("   → Estado debería ser: PENDIENTE")
        
        print(f"   Estado actual en BD: {tareo.estado}")
        print(f"   Estado calculado: {nuevo_estado}")
        
        if tareo.estado != nuevo_estado:
            print(f"\n⚠️  PROBLEMA DETECTADO: El estado no coincide!")
            print(f"   Estado en BD: {tareo.estado}")
            print(f"   Estado calculado: {nuevo_estado}")
            
            # Actualizar el estado manualmente
            print("\n🔧 Actualizando estado manualmente...")
            tareo.estado = nuevo_estado
            if nuevo_estado == 'completado':
                tareo.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
            elif nuevo_estado == 'pendiente':
                tareo.fecha_completado = None
            
            db.session.commit()
            print("✅ Estado actualizado en la base de datos")
        else:
            print("\n✅ El estado está correcto")
        
        # Verificar si hay algún problema con las operaciones
        print("\n🔍 Verificando operaciones individuales...")
        for op in operaciones:
            if op.completado and not op.fecha_completado:
                print(f"   ⚠️  Operación {op.id} marcada como completada pero sin fecha_completado")
            elif not op.completado and op.fecha_completado:
                print(f"   ⚠️  Operación {op.id} no completada pero con fecha_completado")

def test_completar_operacion():
    """Probar la función completar_operacion_tareo"""
    
    with app.app_context():
        print("\n=== PRUEBA DE FUNCIÓN COMPLETAR_OPERACION_TAREO ===\n")
        
        # Buscar una operación pendiente
        operacion = OperacionTareo.query.filter_by(completado=False).first()
        if not operacion:
            print("❌ No se encontró ninguna operación pendiente")
            return
        
        print(f"📋 Operación encontrada: {operacion.nombre}")
        print(f"   Tareo: {operacion.tareo.nombre}")
        print(f"   Estado actual: {'Completada' if operacion.completado else 'Pendiente'}")
        
        # Simular completar la operación
        print("\n🔄 Simulando completar operación...")
        
        # Marcar como completada
        operacion.completado = True
        operacion.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
        
        # Calcular nuevo estado del tareo
        from sqlalchemy import func, case
        
        stats = db.session.query(
            func.count(OperacionTareo.id).label('total'),
            func.sum(case((OperacionTareo.completado == True, 1), else_=0)).label('completadas')
        ).filter(OperacionTareo.tareo_id == operacion.tareo_id).first()
        
        total_operaciones = stats.total or 0
        operaciones_completadas = stats.completadas or 0
        
        print(f"   Total operaciones: {total_operaciones}")
        print(f"   Operaciones completadas: {operaciones_completadas}")
        
        # Actualizar estado del tareo
        if operaciones_completadas == total_operaciones and total_operaciones > 0:
            operacion.tareo.estado = 'completado'
            operacion.tareo.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
            print("   → Tareo marcado como COMPLETADO")
        elif operaciones_completadas > 0:
            operacion.tareo.estado = 'en_progreso'
            print("   → Tareo marcado como EN PROGRESO")
        else:
            operacion.tareo.estado = 'pendiente'
            print("   → Tareo marcado como PENDIENTE")
        
        db.session.commit()
        print("✅ Cambios guardados en la base de datos")
        
        # Verificar resultado
        db.session.refresh(operacion.tareo)
        print(f"\n📊 Resultado:")
        print(f"   Estado del tareo: {operacion.tareo.estado}")
        print(f"   Fecha completado del tareo: {operacion.tareo.fecha_completado}")

if __name__ == "__main__":
    test_tareo_status_update()
    test_completar_operacion()
    print("\n=== PRUEBA COMPLETADA ===") 