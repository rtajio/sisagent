#!/usr/bin/env python3
"""
Script para crear un tareo de prueba con operaciones BBVA, KS y BN
para probar la funcionalidad de aleatorización de montos
"""

import os
import sys
from datetime import datetime
from decimal import Decimal

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Tareo, OperacionTareo, Usuario, Sucursal
import pytz

# Configuración de zona horaria
peru_tz = pytz.timezone('America/Lima')

def crear_tareo_prueba_aleatorizacion():
    """Crear un tareo de prueba con operaciones BBVA, KS y BN"""
    
    with app.app_context():
        print("🔧 CREANDO TAREO DE PRUEBA PARA ALEATORIZACIÓN")
        print("=" * 60)
        
        # 1. Obtener usuario administrador
        print("\n1️⃣ BUSCANDO USUARIO ADMINISTRADOR:")
        admin = Usuario.query.filter_by(es_admin=True).first()
        if not admin:
            print("   ❌ No se encontró ningún usuario administrador")
            return
        
        print(f"   ✅ Administrador encontrado: {admin.nombre_completo}")
        
        # 2. Obtener sucursal
        print("\n2️⃣ BUSCANDO SUCURSAL:")
        sucursal = Sucursal.query.first()
        if not sucursal:
            print("   ❌ No se encontró ninguna sucursal")
            return
        
        print(f"   ✅ Sucursal encontrada: {sucursal.nombre}")
        
        # 3. Crear tareo de prueba
        print("\n3️⃣ CREANDO TAREO DE PRUEBA:")
        
        # Verificar si ya existe un tareo de prueba
        tareo_existente = Tareo.query.filter_by(
            nombre="Tareo Prueba Aleatorización",
            usuario_id=admin.id
        ).first()
        
        if tareo_existente:
            print("   ⚠️  Ya existe un tareo de prueba. Eliminando...")
            db.session.delete(tareo_existente)
            db.session.commit()
        
        # Crear nuevo tareo
        tareo = Tareo(
            nombre="Tareo Prueba Aleatorización",
            descripcion="Tareo creado para probar la funcionalidad de aleatorización de montos con operaciones BBVA, KS y BN",
            usuario_id=admin.id,
            sucursal_id=sucursal.id,
            estado='pendiente',
            created_by=admin.id
        )
        
        db.session.add(tareo)
        db.session.commit()
        
        print(f"   ✅ Tareo creado: {tareo.nombre}")
        print(f"   📅 Fecha creación: {tareo.fecha_creacion}")
        
        # 4. Crear operaciones de prueba
        print("\n4️⃣ CREANDO OPERACIONES DE PRUEBA:")
        
        operaciones_prueba = [
            {
                'medio': 'BBVA',
                'destino': 'Cuenta BBVA',
                'nombre': 'Transferencia BBVA 1',
                'monto': Decimal('25.00'),
                'orden': 1
            },
            {
                'medio': 'BBVA',
                'destino': 'Cuenta BBVA',
                'nombre': 'Transferencia BBVA 2',
                'monto': Decimal('30.00'),
                'orden': 2
            },
            {
                'medio': 'KS',
                'destino': 'Cuenta KS',
                'nombre': 'Transferencia KS 1',
                'monto': Decimal('120.00'),
                'orden': 3
            },
            {
                'medio': 'KS',
                'destino': 'Cuenta KS',
                'nombre': 'Transferencia KS 2',
                'monto': Decimal('135.00'),
                'orden': 4
            },
            {
                'medio': 'BN',
                'destino': 'Cuenta BN',
                'nombre': 'Transferencia BN 1',
                'monto': Decimal('10.00'),
                'orden': 5
            },
            {
                'medio': 'BN',
                'destino': 'Cuenta BN',
                'nombre': 'Transferencia BN 2',
                'monto': Decimal('10.00'),
                'orden': 6
            },
            {
                'medio': 'YAPE',
                'destino': 'Cuenta YAPE',
                'nombre': 'Transferencia YAPE (no se aleatoriza)',
                'monto': Decimal('50.00'),
                'orden': 7
            }
        ]
        
        operaciones_creadas = []
        for op_data in operaciones_prueba:
            operacion = OperacionTareo(
                tareo_id=tareo.id,
                medio=op_data['medio'],
                destino=op_data['destino'],
                nombre=op_data['nombre'],
                monto=op_data['monto'],
                orden=op_data['orden'],
                completado=False
            )
            
            db.session.add(operacion)
            operaciones_creadas.append(operacion)
        
        db.session.commit()
        
        print(f"   ✅ Operaciones creadas: {len(operaciones_creadas)}")
        
        # Mostrar resumen de operaciones
        print("\n5️⃣ RESUMEN DE OPERACIONES CREADAS:")
        for i, op in enumerate(operaciones_creadas, 1):
            print(f"   {i}. {op.medio} - {op.nombre} - S/ {op.monto}")
        
        # 6. Verificar reglas de aleatorización
        print("\n6️⃣ REGLAS DE ALEATORIZACIÓN:")
        print("   • BBVA: S/ 10 - S/ 40 (aleatorio)")
        print("   • KS: S/ 100 - S/ 150 (aleatorio)")
        print("   • BN: S/ 10 (fijo)")
        print("   • Otros medios: Sin cambios")
        
        # 7. Información de acceso
        print("\n7️⃣ INFORMACIÓN DE ACCESO:")
        print(f"   🔗 URL del tareo: /tareos/{tareo.id}")
        print(f"   👤 Usuario: {admin.username}")
        print(f"   🔑 Contraseña: (la que configuraste)")
        
        print("\n" + "=" * 60)
        print("✅ TAREO DE PRUEBA CREADO EXITOSAMENTE")
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Inicia sesión como administrador")
        print("   2. Ve a /tareos para ver tus tareos")
        print("   3. Haz clic en el tareo 'Tareo Prueba Aleatorización'")
        print("   4. Usa el botón 'Aleatorizar Montos' para probar la funcionalidad")
        print("   5. Verifica que los montos cambien según las reglas establecidas")

if __name__ == "__main__":
    print("🚀 CREANDO TAREO DE PRUEBA PARA ALEATORIZACIÓN")
    print("=" * 60)
    
    try:
        crear_tareo_prueba_aleatorizacion()
    except Exception as e:
        print(f"❌ Error al crear tareo de prueba: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎯 PROCESO FINALIZADO") 