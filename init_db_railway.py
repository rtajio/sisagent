#!/usr/bin/env python3
"""
Script para inicializar la base de datos en Railway
"""

import os
from app import app, db, Usuario, Sucursal, MedioPago, Operacion

def init_database():
    """Inicializar la base de datos con datos básicos"""
    
    print("🚀 Inicializando base de datos en Railway...")
    
    with app.app_context():
        try:
            # Crear todas las tablas
            print("📋 Creando tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # Verificar si ya existen datos
            if Usuario.query.first():
                print("✅ Base de datos ya tiene datos")
                return
            
            # Crear usuario administrador
            print("👤 Creando usuario administrador...")
            admin = Usuario(
                username='admin',
                password='admin123',
                nombre='Administrador',
                es_admin=True
            )
            db.session.add(admin)
            
            # Crear sucursal por defecto
            print("🏢 Creando sucursal por defecto...")
            sucursal = Sucursal(
                nombre='Sucursal Principal',
                direccion='Dirección Principal'
            )
            db.session.add(sucursal)
            
            # Crear medios de pago básicos
            print("💳 Creando medios de pago...")
            medios = [
                MedioPago(nombre='Efectivo', descripcion='Pago en efectivo'),
                MedioPago(nombre='Tarjeta', descripcion='Pago con tarjeta'),
                MedioPago(nombre='Transferencia', descripcion='Transferencia bancaria')
            ]
            for medio in medios:
                db.session.add(medio)
            
            # Crear operación de ejemplo
            print("📊 Creando operación de ejemplo...")
            operacion = Operacion(
                numero='OP001',
                monto=100.0,
                metodo_pago='Efectivo',
                comision=5.0,
                usuario_id=1,
                sucursal_id=1
            )
            db.session.add(operacion)
            
            # Guardar todos los cambios
            db.session.commit()
            print("✅ Base de datos inicializada exitosamente")
            
        except Exception as e:
            print(f"❌ Error al inicializar base de datos: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    init_database()
