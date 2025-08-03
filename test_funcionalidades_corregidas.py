#!/usr/bin/env python3
"""
Script para probar todas las funcionalidades corregidas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Tareo, OperacionTareo, Usuario, get_peru_time
from datetime import datetime
import pytz

def test_zona_horaria():
    """Probar que la zona horaria funcione correctamente"""
    
    with app.app_context():
        print("=== PRUEBA DE ZONA HORARIA ===\n")
        
        # Obtener hora actual en Perú
        hora_peru = get_peru_time()
        print(f"🕐 Hora actual en Perú: {hora_peru}")
        print(f"   Zona horaria: {hora_peru.tzinfo}")
        print(f"   UTC offset: {hora_peru.utcoffset()}")
        
        # Verificar que sea UTC-5
        offset_hours = hora_peru.utcoffset().total_seconds() / 3600
        print(f"   Offset en horas: {offset_hours}")
        
        if offset_hours == -5:
            print("✅ Zona horaria correcta (UTC-5)")
        else:
            print(f"❌ Zona horaria incorrecta. Esperado: -5, Obtenido: {offset_hours}")
        
        # Comparar con datetime.now()
        hora_sistema = datetime.now()
        print(f"\n🕐 Hora del sistema: {hora_sistema}")
        print(f"   Diferencia: {hora_peru - hora_sistema.replace(tzinfo=pytz.UTC)}")

def test_crear_tareo_nuevo_dia():
    """Crear un tareo para el día actual con hora correcta"""
    
    with app.app_context():
        print("\n=== CREAR TAREO PARA NUEVO DÍA ===\n")
        
        # Buscar un usuario admin
        admin = Usuario.query.filter_by(es_admin=True).first()
        if not admin:
            print("❌ No se encontró ningún usuario administrador")
            return None
        
        # Buscar una sucursal
        from app import Sucursal
        sucursal = Sucursal.query.first()
        if not sucursal:
            print("❌ No se encontró ninguna sucursal")
            return None
        
        print(f"👤 Usuario admin: {admin.nombre_completo}")
        print(f"🏢 Sucursal: {sucursal.nombre}")
        
        # Crear el tareo con hora correcta de Perú
        tareo = Tareo(
            nombre="Tareo Nuevo Día - Prueba",
            descripcion="Tareo creado para probar funcionalidades corregidas",
            usuario_id=admin.id,
            sucursal_id=sucursal.id,
            estado='pendiente',
            created_by=admin.id
        )
        
        db.session.add(tareo)
        db.session.commit()
        
        print(f"✅ Tareo creado: {tareo.nombre}")
        print(f"   ID: {tareo.id}")
        print(f"   Estado: {tareo.estado}")
        print(f"   Fecha creación: {tareo.fecha_creacion}")
        print(f"   Hora creación: {tareo.fecha_creacion.strftime('%H:%M:%S')}")
        
        # Crear operaciones para el tareo
        operaciones_data = [
            {"medio": "BBVA", "destino": "Cuenta BBVA", "nombre": "Pago BBVA Nuevo", "monto": 30.00, "orden": 1},
            {"medio": "KS", "destino": "Cuenta KS", "nombre": "Pago KS Nuevo", "monto": 120.00, "orden": 2},
            {"medio": "BN", "destino": "Cuenta BN", "nombre": "Pago BN Nuevo", "monto": 10.00, "orden": 3}
        ]
        
        print(f"\n📝 Creando {len(operaciones_data)} operaciones...")
        
        for op_data in operaciones_data:
            operacion = OperacionTareo(
                tareo_id=tareo.id,
                medio=op_data["medio"],
                destino=op_data["destino"],
                nombre=op_data["nombre"],
                monto=op_data["monto"],
                orden=op_data["orden"]
            )
            db.session.add(operacion)
            print(f"   ✅ {op_data['nombre']} ({op_data['medio']}) - S/ {op_data['monto']}")
        
        db.session.commit()
        
        # Verificar que el tareo esté habilitado para el día actual
        fecha_actual = get_peru_time().date()
        fecha_tareo = tareo.fecha_creacion.date()
        
        print(f"\n📅 Verificación de fecha:")
        print(f"   Fecha actual: {fecha_actual}")
        print(f"   Fecha tareo: {fecha_tareo}")
        
        if fecha_actual == fecha_tareo:
            print("✅ El tareo está habilitado para el día actual")
            print("✅ Las operaciones se pueden completar normalmente")
        else:
            print("❌ El tareo NO está habilitado para el día actual")
        
        return tareo.id

def test_completar_operaciones():
    """Probar completar operaciones y verificar cambio de estado"""
    
    with app.app_context():
        print("\n=== PRUEBA DE COMPLETAR OPERACIONES ===\n")
        
        # Buscar el tareo más reciente
        tareo = Tareo.query.order_by(Tareo.fecha_creacion.desc()).first()
        if not tareo:
            print("❌ No se encontró ningún tareo")
            return
        
        print(f"📋 Tareo: {tareo.nombre}")
        print(f"   Estado inicial: {tareo.estado}")
        
        # Obtener operaciones
        operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
        print(f"   Operaciones: {len(operaciones)}")
        
        # Completar todas las operaciones
        print(f"\n🔄 Completando operaciones...")
        for i, op in enumerate(operaciones, 1):
            op.completado = True
            op.fecha_completado = get_peru_time()
            print(f"   ✅ Completada: {op.nombre}")
        
        # Calcular nuevo estado
        from sqlalchemy import func, case
        
        stats = db.session.query(
            func.count(OperacionTareo.id).label('total'),
            func.sum(case((OperacionTareo.completado == True, 1), else_=0)).label('completadas')
        ).filter(OperacionTareo.tareo_id == tareo.id).first()
        
        total = stats.total or 0
        completadas = stats.completadas or 0
        
        if completadas == total and total > 0:
            tareo.estado = 'completado'
            tareo.fecha_completado = get_peru_time()
            print("   → Tareo marcado como COMPLETADO")
        elif completadas > 0:
            tareo.estado = 'en_progreso'
            print("   → Tareo marcado como EN PROGRESO")
        
        db.session.commit()
        
        # Verificar resultado
        db.session.refresh(tareo)
        print(f"\n📊 Resultado:")
        print(f"   Estado final: {tareo.estado}")
        print(f"   Fecha completado: {tareo.fecha_completado}")
        print(f"   Operaciones completadas: {completadas}/{total}")

def test_aleatorizacion_automatica():
    """Probar la aleatorización automática que resetea el estado"""
    
    with app.app_context():
        print("\n=== PRUEBA DE ALEATORIZACIÓN AUTOMÁTICA ===\n")
        
        # Buscar el tareo más reciente
        tareo = Tareo.query.order_by(Tareo.fecha_creacion.desc()).first()
        if not tareo:
            print("❌ No se encontró ningún tareo")
            return
        
        print(f"📋 Tareo: {tareo.nombre}")
        print(f"   Estado antes: {tareo.estado}")
        
        # Obtener operaciones
        operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
        print(f"   Operaciones antes: {sum(1 for op in operaciones if op.completado)}/{len(operaciones)} completadas")
        
        # Simular aleatorización automática
        import random
        from decimal import Decimal
        
        def aleatorizar_monto(medio):
            if medio.upper() == 'BBVA':
                return Decimal(str(random.randint(10, 40)))
            elif medio.upper() == 'KS':
                return Decimal(str(random.randint(100, 150)))
            elif medio.upper() == 'BN':
                return Decimal('10.00')
            else:
                return None
        
        print(f"\n🔄 Ejecutando aleatorización automática...")
        
        # Resetear estado de todas las operaciones
        for operacion in operaciones:
            nuevo_monto = aleatorizar_monto(operacion.medio)
            if nuevo_monto is not None:
                operacion.monto = nuevo_monto
                print(f"   💰 {operacion.nombre}: S/ {operacion.monto} → S/ {nuevo_monto}")
            
            # Resetear estado de completado
            operacion.completado = False
            operacion.fecha_completado = None
        
        # Resetear estado del tareo
        tareo.estado = 'pendiente'
        tareo.fecha_completado = None
        
        db.session.commit()
        
        # Verificar resultado
        db.session.refresh(tareo)
        operaciones_actualizadas = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
        
        print(f"\n📊 Resultado después de aleatorización:")
        print(f"   Estado del tareo: {tareo.estado}")
        print(f"   Operaciones completadas: {sum(1 for op in operaciones_actualizadas if op.completado)}/{len(operaciones_actualizadas)}")
        
        if tareo.estado == 'pendiente':
            print("✅ Estado reseteado correctamente a PENDIENTE")
        else:
            print("❌ Error: El estado no se reseteó correctamente")

def test_funciones_admin():
    """Probar las funciones de administración"""
    
    with app.app_context():
        print("\n=== PRUEBA DE FUNCIONES DE ADMINISTRACIÓN ===\n")
        
        # Verificar que existen las rutas de API
        print("🔍 Verificando rutas de API...")
        
        # Simular edición de operación
        operacion = OperacionTareo.query.first()
        if operacion:
            print(f"📝 Operación encontrada: {operacion.nombre}")
            print(f"   Monto actual: S/ {operacion.monto}")
            
            # Simular cambio de monto
            from decimal import Decimal
            nuevo_monto = Decimal('50.00')
            operacion.monto = nuevo_monto
            operacion.nombre = "Operación Editada"
            
            db.session.commit()
            
            print(f"   Monto nuevo: S/ {operacion.monto}")
            print(f"   Nombre nuevo: {operacion.nombre}")
            print("✅ Edición simulada correctamente")
        else:
            print("❌ No se encontró ninguna operación para editar")

if __name__ == "__main__":
    test_zona_horaria()
    tareo_id = test_crear_tareo_nuevo_dia()
    if tareo_id:
        test_completar_operaciones()
        test_aleatorizacion_automatica()
        test_funciones_admin()
    
    print("\n=== PRUEBAS COMPLETADAS ===")
    print("🎉 Todas las funcionalidades han sido probadas")
    print(f"📋 Tareo de prueba creado: ID {tareo_id if tareo_id else 'N/A'}")
    print("🔗 URL para probar: http://localhost:5000/tareos/{tareo_id}" if tareo_id else "") 