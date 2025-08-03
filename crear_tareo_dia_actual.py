#!/usr/bin/env python3
"""
Script para crear un nuevo tareo para el día actual
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Tareo, OperacionTareo, Usuario, Sucursal
from datetime import datetime
import pytz

def crear_tareo_dia_actual():
    """Crear un nuevo tareo para el día actual"""
    
    with app.app_context():
        print("=== CREAR TAREO PARA EL DÍA ACTUAL ===\n")
        
        # Buscar un usuario admin
        admin = Usuario.query.filter_by(es_admin=True).first()
        if not admin:
            print("❌ No se encontró ningún usuario administrador")
            return
        
        # Buscar una sucursal
        sucursal = Sucursal.query.first()
        if not sucursal:
            print("❌ No se encontró ninguna sucursal")
            return
        
        print(f"👤 Usuario admin: {admin.nombre_completo}")
        print(f"🏢 Sucursal: {sucursal.nombre}")
        
        # Crear el tareo
        tareo = Tareo(
            nombre="Tareo del Día Actual - Prueba",
            descripcion="Tareo creado para probar la funcionalidad de completado",
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
        
        # Crear operaciones para el tareo
        operaciones_data = [
            {"medio": "BBVA", "destino": "Cuenta Principal", "nombre": "Pago BBVA 1", "monto": 25.00, "orden": 1},
            {"medio": "KS", "destino": "Cuenta Secundaria", "nombre": "Pago KS 1", "monto": 125.00, "orden": 2},
            {"medio": "BN", "destino": "Cuenta BN", "nombre": "Pago BN 1", "monto": 10.00, "orden": 3},
            {"medio": "YAPE", "destino": "Cuenta YAPE", "nombre": "Pago YAPE 1", "monto": 50.00, "orden": 4},
            {"medio": "PLIN", "destino": "Cuenta PLIN", "nombre": "Pago PLIN 1", "monto": 75.00, "orden": 5}
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
        fecha_actual = datetime.now(pytz.timezone('America/Lima')).date()
        fecha_tareo = tareo.fecha_creacion.date()
        
        print(f"\n📅 Verificación de fecha:")
        print(f"   Fecha actual: {fecha_actual}")
        print(f"   Fecha tareo: {fecha_tareo}")
        
        if fecha_actual == fecha_tareo:
            print("✅ El tareo está habilitado para el día actual")
            print("✅ Las operaciones se pueden completar normalmente")
        else:
            print("❌ El tareo NO está habilitado para el día actual")
        
        # Mostrar información final
        operaciones = OperacionTareo.query.filter_by(tareo_id=tareo.id).all()
        print(f"\n📊 Resumen final:")
        print(f"   Tareo: {tareo.nombre}")
        print(f"   Estado: {tareo.estado}")
        print(f"   Operaciones: {len(operaciones)}")
        print(f"   URL para probar: /tareos/{tareo.id}")
        
        return tareo.id

if __name__ == "__main__":
    tareo_id = crear_tareo_dia_actual()
    if tareo_id:
        print(f"\n🎉 ¡Tareo creado exitosamente!")
        print(f"   Puedes acceder a él en: http://localhost:5000/tareos/{tareo_id}")
        print(f"   Usuario: admin")
        print(f"   Contraseña: admin123")
    else:
        print("\n❌ Error al crear el tareo") 