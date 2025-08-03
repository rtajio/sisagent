#!/usr/bin/env python3
"""
Diagnóstico final del sistema de tareos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Tareo, OperacionTareo, Usuario
from datetime import datetime
import pytz

def diagnostico_final():
    """Diagnóstico completo del sistema de tareos"""
    
    with app.app_context():
        print("=== DIAGNÓSTICO FINAL DEL SISTEMA DE TAREOS ===\n")
        
        # 1. Verificar tareos existentes
        tareos = Tareo.query.all()
        print(f"📋 Tareos encontrados: {len(tareos)}")
        
        for i, tareo in enumerate(tareos, 1):
            fecha_actual = datetime.now(pytz.timezone('America/Lima')).date()
            fecha_tareo = tareo.fecha_creacion.date()
            habilitado = fecha_actual == fecha_tareo
            
            print(f"\n{i}. {tareo.nombre}")
            print(f"   ID: {tareo.id}")
            print(f"   Estado: {tareo.estado}")
            print(f"   Usuario: {tareo.usuario.nombre_completo}")
            print(f"   Fecha creación: {tareo.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
            print(f"   Habilitado para hoy: {'✅ Sí' if habilitado else '❌ No'}")
            
            # Contar operaciones
            operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
            completadas = sum(1 for op in operaciones if op.completado)
            print(f"   Operaciones: {completadas}/{len(operaciones)} completadas")
            
            if habilitado:
                print(f"   🔗 URL: http://localhost:5000/tareos/{tareo.id}")
        
        # 2. Verificar el tareo más reciente (debería ser el del día actual)
        if tareos:
            tareo_reciente = max(tareos, key=lambda t: t.fecha_creacion)
            print(f"\n🎯 TAREO MÁS RECIENTE:")
            print(f"   Nombre: {tareo_reciente.nombre}")
            print(f"   ID: {tareo_reciente.id}")
            print(f"   Estado: {tareo_reciente.estado}")
            
            fecha_actual = datetime.now(pytz.timezone('America/Lima')).date()
            fecha_tareo = tareo_reciente.fecha_creacion.date()
            
            if fecha_actual == fecha_tareo:
                print("   ✅ ESTE TAREO ESTÁ HABILITADO PARA HOY")
                print("   ✅ Las operaciones se pueden completar normalmente")
                
                # Verificar operaciones
                operaciones = OperacionTareo.query.filter_by(tareo_id=tareo_reciente.id).all()
                if operaciones:
                    print(f"\n📝 Operaciones disponibles:")
                    for i, op in enumerate(operaciones, 1):
                        estado = "✅ Completada" if op.completado else "⏳ Pendiente"
                        print(f"   {i}. {op.nombre} ({op.medio}) - {estado}")
                    
                    # Simular completar una operación
                    operacion_pendiente = next((op for op in operaciones if not op.completado), None)
                    if operacion_pendiente:
                        print(f"\n🧪 Simulando completar: {operacion_pendiente.nombre}")
                        
                        # Marcar como completada
                        operacion_pendiente.completado = True
                        operacion_pendiente.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
                        
                        # Calcular nuevo estado
                        from sqlalchemy import func, case
                        stats = db.session.query(
                            func.count(OperacionTareo.id).label('total'),
                            func.sum(case((OperacionTareo.completado == True, 1), else_=0)).label('completadas')
                        ).filter(OperacionTareo.tareo_id == tareo_reciente.id).first()
                        
                        total = stats.total or 0
                        completadas = stats.completadas or 0
                        
                        if completadas == total and total > 0:
                            tareo_reciente.estado = 'completado'
                            tareo_reciente.fecha_completado = datetime.now(pytz.timezone('America/Lima'))
                            print("   → Tareo marcado como COMPLETADO")
                        elif completadas > 0:
                            tareo_reciente.estado = 'en_progreso'
                            print("   → Tareo marcado como EN PROGRESO")
                        
                        db.session.commit()
                        print("   ✅ Cambios guardados")
                        
                        # Verificar resultado
                        db.session.refresh(tareo_reciente)
                        print(f"   📊 Estado final: {tareo_reciente.estado}")
                    else:
                        print("   ℹ️  Todas las operaciones ya están completadas")
                else:
                    print("   ⚠️  No hay operaciones en este tareo")
            else:
                print("   ❌ ESTE TAREO NO ESTÁ HABILITADO PARA HOY")
                print("   ❌ Las operaciones no se pueden completar")
        
        # 3. Resumen final
        print(f"\n📊 RESUMEN FINAL:")
        print(f"   Total tareos: {len(tareos)}")
        tareos_habilitados = sum(1 for t in tareos if datetime.now(pytz.timezone('America/Lima')).date() == t.fecha_creacion.date())
        print(f"   Tareos habilitados para hoy: {tareos_habilitados}")
        print(f"   Tareos completados: {sum(1 for t in tareos if t.estado == 'completado')}")
        print(f"   Tareos en progreso: {sum(1 for t in tareos if t.estado == 'en_progreso')}")
        print(f"   Tareos pendientes: {sum(1 for t in tareos if t.estado == 'pendiente')}")
        
        if tareos_habilitados > 0:
            print(f"\n✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
            print(f"   Hay tareos habilitados para el día actual")
            print(f"   Las operaciones se pueden completar normalmente")
        else:
            print(f"\n⚠️  NO HAY TAREOS HABILITADOS PARA HOY")
            print(f"   Necesitas crear un nuevo tareo o ejecutar la aleatorización automática")

if __name__ == "__main__":
    diagnostico_final()
    print("\n=== DIAGNÓSTICO COMPLETADO ===") 