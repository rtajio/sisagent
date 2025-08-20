#!/usr/bin/env python3
"""
WSGI entry point para Railway
"""
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

def init_db_on_startup():
    """Inicializar la base de datos al importar el módulo"""
    try:
        from app import app, db, Usuario, Sucursal, MedioPago
        from werkzeug.security import generate_password_hash
        
        with app.app_context():
            # Crear tablas
            db.create_all()
            print("✅ Tablas creadas")
            
            # Verificar si ya existe un usuario admin
            admin_exists = Usuario.query.filter_by(username='admin').first()
            if not admin_exists:
                print("🔧 Creando usuario admin...")
                admin = Usuario(
                    username='admin',
                    email='admin@sisagent.com',
                    password_hash=generate_password_hash('admin123'),
                    nombre_completo='Administrador del Sistema',
                    es_admin=True
                )
                db.session.add(admin)
                
                # Crear sucursal por defecto
                sucursal_default = Sucursal(
                    nombre='Sucursal Principal',
                    direccion='Dirección Principal',
                    activa=True
                )
                db.session.add(sucursal_default)
                db.session.flush()
                
                # Crear medios de pago básicos
                medios = ['BCP', 'BBVA', 'BN', 'IBK']
                for i, medio in enumerate(medios):
                    nuevo_medio = MedioPago(
                        nombre_abreviado=medio,
                        nombre_completo=f'Banco {medio}',
                        activo=True,
                        orden=i+1
                    )
                    db.session.add(nuevo_medio)
                
                db.session.commit()
                print("✅ Datos iniciales creados")
            
            print("✅ Base de datos lista")
            
    except Exception as e:
        print(f"⚠️ Error en inicialización: {e}")

# Inicializar la base de datos al importar
print("🚀 Inicializando SISAGENT...")
init_db_on_startup()

# Importar la aplicación
from app import app

# Variable global para la aplicación
application = app

print("✅ SISAGENT listo para Gunicorn") 