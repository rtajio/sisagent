#!/usr/bin/env python3
"""
Script de inicio simple para Railway
"""
import os
import sys
import time

def init_db_simple():
    """Inicialización simple de la base de datos"""
    try:
        print("🔧 Inicializando base de datos...")
        
        # Importar la aplicación
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
            return True
            
    except Exception as e:
        print(f"⚠️ Error en inicialización: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Iniciando SISAGENT...")
    
    # Intentar inicializar la base de datos
    init_db_simple()
    
    # Obtener puerto
    port = os.environ.get('PORT', 5000)
    print(f"🌐 Puerto: {port}")
    
    # Importar y ejecutar la aplicación
    from app import app
    
    print("✅ Aplicación iniciada correctamente")
    app.run(host='0.0.0.0', port=port, debug=False)
