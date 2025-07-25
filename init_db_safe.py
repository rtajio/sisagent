#!/usr/bin/env python3
"""
Script de inicialización SEGURO de base de datos para Railway
NO borra datos existentes, solo agrega datos faltantes
"""

import os
import sys
import time
from pathlib import Path

def debug_database_config():
    """Diagnóstico de configuración de base de datos"""
    print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        print(f"✅ DATABASE_URL encontrada")
        if 'postgres' in database_url.lower():
            print("✅ Tipo de base de datos: PostgreSQL")
        elif 'mysql' in database_url.lower():
            print("⚠️ Tipo de base de datos: MySQL (no recomendado para Railway)")
        else:
            print(f"❓ Tipo de base de datos: Desconocido")
    else:
        print("❌ DATABASE_URL no encontrada")
        print("ℹ️ Usando SQLite para desarrollo local")
    
    print("=" * 50)

def safe_init_database():
    """Inicialización SEGURA de la base de datos - NO borra datos existentes"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔧 Intento {attempt + 1}/{max_retries}: Inicialización SEGURA de base de datos...")
            
            # Importar después del diagnóstico
            from app import app, db, Usuario, Sucursal, MedioPago
            from werkzeug.security import generate_password_hash
            
            with app.app_context():
                # Verificar si las tablas existen
                print("🔍 Verificando estructura de base de datos...")
                try:
                    # Intentar una consulta simple para verificar que las tablas existen
                    Usuario.query.first()
                    print("✅ Tablas ya existen, no se recrearán")
                except Exception as e:
                    print("🔧 Tablas no existen, creando estructura...")
                    db.create_all()
                    print("✅ Estructura de base de datos creada")
                
                # Verificar si ya existe un usuario admin
                admin_exists = Usuario.query.filter_by(username='admin').first()
                if admin_exists:
                    print("✅ Usuario admin ya existe")
                else:
                    # Crear usuario admin
                    print("🔧 Creando usuario admin...")
                    admin = Usuario(
                        username='admin',
                        email='admin@sisagent.com',
                        password_hash=generate_password_hash('admin123'),
                        nombre_completo='Administrador del Sistema',
                        es_admin=True
                    )
                    db.session.add(admin)
                    print("✅ Usuario admin creado")
                
                # Verificar si existe sucursal por defecto
                sucursal_default = Sucursal.query.filter_by(nombre='Sucursal Principal').first()
                if not sucursal_default:
                    print("🔧 Creando sucursal por defecto...")
                    sucursal_default = Sucursal(
                        nombre='Sucursal Principal',
                        direccion='Dirección Principal',
                        activa=True
                    )
                    db.session.add(sucursal_default)
                    print("✅ Sucursal por defecto creada")
                else:
                    print("✅ Sucursal por defecto ya existe")
                
                # Crear medios de pago por defecto solo si no existen
                medios_default = [
                    {'abreviado': 'BCP', 'completo': 'Banco de Crédito del Perú'},
                    {'abreviado': 'BBVA', 'completo': 'BBVA Perú'},
                    {'abreviado': 'BN', 'completo': 'Banco de la Nación'},
                    {'abreviado': 'IBK', 'completo': 'Interbank'},
                    {'abreviado': 'KS', 'completo': 'Kashio'},
                    {'abreviado': 'NIUBIZ', 'completo': 'Niubiz'},
                    {'abreviado': 'ICA', 'completo': 'ICA'},
                    {'abreviado': 'CONFIANZA', 'completo': 'Confianza'}
                ]
                
                medios_creados = 0
                for i, medio in enumerate(medios_default):
                    medio_exists = MedioPago.query.filter_by(nombre_abreviado=medio['abreviado']).first()
                    if not medio_exists:
                        print(f"🔧 Creando medio de pago: {medio['abreviado']}")
                        nuevo_medio = MedioPago(
                            nombre_abreviado=medio['abreviado'],
                            nombre_completo=medio['completo'],
                            activo=True,
                            orden=i+1
                        )
                        db.session.add(nuevo_medio)
                        medios_creados += 1
                
                if medios_creados > 0:
                    print(f"✅ {medios_creados} medios de pago creados")
                else:
                    print("✅ Todos los medios de pago ya existen")
                
                # Commit solo si hay cambios
                if db.session.is_modified():
                    db.session.commit()
                    print("✅ Cambios guardados en base de datos")
                else:
                    print("✅ No hay cambios que guardar")
                
                print("✅ Inicialización SEGURA completada - DATOS EXISTENTES PRESERVADOS")
                return True
                
        except Exception as e:
            print(f"❌ Error en intento {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"⏳ Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print("💥 Error fatal: No se pudo inicializar la base de datos después de todos los intentos")
                return False
    
    return False

if __name__ == '__main__':
    debug_database_config()
    success = safe_init_database()
    if success:
        print("🎉 Inicialización SEGURA completada exitosamente")
        print("🛡️ TODOS LOS DATOS EXISTENTES HAN SIDO PRESERVADOS")
        sys.exit(0)
    else:
        print("💥 Error en la inicialización")
        sys.exit(1) 