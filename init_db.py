#!/usr/bin/env python3
"""
Script de inicialización de base de datos para Railway
"""
import os
import sys
import time
from sqlalchemy import text

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

def init_database():
    """Inicializar la base de datos y crear usuario admin"""
    # Diagnóstico primero
    debug_database_config()
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔧 Intento {attempt + 1}/{max_retries}: Conectando a la base de datos...")
            
            # Importar después del diagnóstico para evitar errores tempranos
            from app import app, db, Usuario
            from werkzeug.security import generate_password_hash
            
            with app.app_context():
                # Verificar conexión a la base de datos usando la sintaxis correcta de SQLAlchemy 2.0
                with db.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                    connection.commit()
                print("✅ Conexión a la base de datos establecida")
                
                print("🔧 Creando tablas de base de datos...")
                db.create_all()
                print("✅ Tablas creadas exitosamente")
                
                # Crear usuario admin por defecto si no existe
                admin = Usuario.query.filter_by(username='admin').first()
                if not admin:
                    print("👤 Creando usuario administrador...")
                    admin = Usuario(
                        username='admin',
                        email='admin@sisagent.com',
                        password_hash=generate_password_hash('61442159'),
                        nombre_completo='Administrador SISAGENT',
                        es_admin=True,
                        sucursal_id=None
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("✅ Usuario administrador creado")
                else:
                    print("ℹ️ Usuario administrador ya existe")
                
                print("🎉 Inicialización completada exitosamente")
                return True
                
        except Exception as e:
            print(f"❌ Error en intento {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                print(f"⏳ Reintentando en {retry_delay} segundos...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Backoff exponencial
            else:
                print("💥 Error fatal: No se pudo inicializar la base de datos después de todos los intentos")
                return False
    
    return False

if __name__ == "__main__":
    success = init_database()
    if not success:
        sys.exit(1)
