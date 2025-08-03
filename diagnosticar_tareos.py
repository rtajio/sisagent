#!/usr/bin/env python3
"""
Script para diagnosticar problemas con fechas de completado y progreso de tareos
"""

import os
import sys
from datetime import datetime
import pytz

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app import Tareo, OperacionTareo, Usuario

def diagnosticar_tareos():
    """Diagnosticar el estado actual de los tareos y operaciones"""
    
    with app.app_context():
        try:
            print("🔍 DIAGNÓSTICO DE TAREOS Y OPERACIONES")
            print("=" * 60)
            
            # Obtener todos los tareos
            tareos = Tareo.query.all()
            print(f"📊 Total de tareos en el sistema: {len(tareos)}")
            
            if not tareos:
                print("❌ No hay tareos en el sistema")
                return
            
            # Analizar cada tareo
            for i, tareo in enumerate(tareos, 1):
                print(f"\n🔍 TAREO {i}: {tareo.nombre}")
                print(f"   ID: {tareo.id}")
                print(f"   Estado: {tareo.estado}")
                print(f"   Usuario: {tareo.usuario.nombre_completo}")
                print(f"   Sucursal: {tareo.sucursal.nombre}")
                print(f"   Fecha creación: {tareo.fecha_creacion}")
                print(f"   Fecha completado: {tareo.fecha_completado}")
                
                # Obtener operaciones del tareo
                operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).order_by(OperacionTareo.orden).all()
                print(f"   📋 Operaciones: {len(operaciones)}")
                
                if operaciones:
                    completadas = 0
                    for j, op in enumerate(operaciones, 1):
                        estado = "✅ Completada" if op.completado else "⏳ Pendiente"
                        fecha = op.fecha_completado.strftime('%d/%m/%Y %H:%M') if op.fecha_completado else "N/A"
                        print(f"      {j}. {op.nombre} - {estado} - Fecha: {fecha}")
                        if op.completado:
                            completadas += 1
                    
                    print(f"   📈 Progreso: {completadas}/{len(operaciones)} ({completadas/len(operaciones)*100:.1f}%)")
                    
                    # Verificar consistencia
                    if completadas == len(operaciones) and tareo.estado != 'completado':
                        print(f"   ⚠️  INCONSISTENCIA: Todas las operaciones están completadas pero el tareo no está marcado como completado")
                    elif completadas == 0 and tareo.estado != 'pendiente':
                        print(f"   ⚠️  INCONSISTENCIA: Ninguna operación está completada pero el tareo no está marcado como pendiente")
                    elif 0 < completadas < len(operaciones) and tareo.estado != 'en_progreso':
                        print(f"   ⚠️  INCONSISTENCIA: Algunas operaciones están completadas pero el tareo no está marcado como en progreso")
                else:
                    print("   ❌ No hay operaciones en este tareo")
            
            # Verificar operaciones sin fecha de completado pero marcadas como completadas
            print(f"\n🔍 VERIFICANDO OPERACIONES SIN FECHA DE COMPLETADO:")
            operaciones_sin_fecha = OperacionTareo.query.filter(
                OperacionTareo.completado == True,
                OperacionTareo.fecha_completado.is_(None)
            ).all()
            
            if operaciones_sin_fecha:
                print(f"   ⚠️  Encontradas {len(operaciones_sin_fecha)} operaciones marcadas como completadas pero sin fecha:")
                for op in operaciones_sin_fecha:
                    print(f"      - ID: {op.id}, Tareo: {op.tareo.nombre}, Operación: {op.nombre}")
            else:
                print("   ✅ Todas las operaciones completadas tienen fecha de completado")
            
            # Verificar operaciones con fecha pero no marcadas como completadas
            operaciones_con_fecha_sin_completar = OperacionTareo.query.filter(
                OperacionTareo.completado == False,
                OperacionTareo.fecha_completado.isnot(None)
            ).all()
            
            if operaciones_con_fecha_sin_completar:
                print(f"   ⚠️  Encontradas {len(operaciones_con_fecha_sin_completar)} operaciones con fecha pero no marcadas como completadas:")
                for op in operaciones_con_fecha_sin_completar:
                    print(f"      - ID: {op.id}, Tareo: {op.tareo.nombre}, Operación: {op.nombre}, Fecha: {op.fecha_completado}")
            else:
                print("   ✅ No hay operaciones con fecha pero sin marcar como completadas")
                
        except Exception as e:
            print(f"❌ Error durante el diagnóstico: {e}")

def corregir_inconsistencias():
    """Corregir inconsistencias encontradas en los tareos"""
    
    with app.app_context():
        try:
            print("\n🔧 CORRIGIENDO INCONSISTENCIAS")
            print("=" * 60)
            
            # Corregir operaciones marcadas como completadas pero sin fecha
            operaciones_sin_fecha = OperacionTareo.query.filter(
                OperacionTareo.completado == True,
                OperacionTareo.fecha_completado.is_(None)
            ).all()
            
            if operaciones_sin_fecha:
                print(f"🔧 Agregando fechas de completado a {len(operaciones_sin_fecha)} operaciones...")
                for op in operaciones_sin_fecha:
                    op.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
                    print(f"   ✅ Operación {op.id} ({op.nombre}) - Fecha agregada")
            
            # Corregir operaciones con fecha pero no marcadas como completadas
            operaciones_con_fecha_sin_completar = OperacionTareo.query.filter(
                OperacionTareo.completado == False,
                OperacionTareo.fecha_completado.isnot(None)
            ).all()
            
            if operaciones_con_fecha_sin_completar:
                print(f"🔧 Marcando como completadas {len(operaciones_con_fecha_sin_completar)} operaciones...")
                for op in operaciones_con_fecha_sin_completar:
                    op.completado = True
                    print(f"   ✅ Operación {op.id} ({op.nombre}) - Marcada como completada")
            
            # Recalcular estados de tareos
            tareos = Tareo.query.all()
            print(f"🔧 Recalculando estados de {len(tareos)} tareos...")
            
            for tareo in tareos:
                operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
                total_operaciones = len(operaciones)
                operaciones_completadas = sum(1 for op in operaciones if op.completado)
                
                # Determinar el nuevo estado
                if operaciones_completadas == total_operaciones and total_operaciones > 0:
                    nuevo_estado = 'completado'
                    if not tareo.fecha_completado:
                        tareo.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
                elif operaciones_completadas > 0:
                    nuevo_estado = 'en_progreso'
                else:
                    nuevo_estado = 'pendiente'
                    tareo.fecha_completado = None
                
                if tareo.estado != nuevo_estado:
                    print(f"   🔄 Tareo {tareo.id} ({tareo.nombre}): {tareo.estado} → {nuevo_estado}")
                    tareo.estado = nuevo_estado
            
            # Commit de todos los cambios
            db.session.commit()
            print("✅ Todas las inconsistencias han sido corregidas")
            
        except Exception as e:
            print(f"❌ Error durante la corrección: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("🚀 Iniciando diagnóstico de tareos...")
    
    diagnosticar_tareos()
    
    # Preguntar si quiere corregir inconsistencias
    print("\n" + "=" * 60)
    respuesta = input("¿Deseas corregir las inconsistencias encontradas? (s/n): ").lower().strip()
    
    if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
        corregir_inconsistencias()
        print("\n🔄 Ejecutando diagnóstico final...")
        diagnosticar_tareos()
    else:
        print("❌ No se realizaron correcciones")
    
    print("\n🎉 Diagnóstico completado") 