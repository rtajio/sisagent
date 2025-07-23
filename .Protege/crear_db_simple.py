#!/usr/bin/env python3
"""
Script simple para crear la base de datos y verificar el dropdown
"""

from app import app, db, Sucursal, Usuario
from werkzeug.security import generate_password_hash

def crear_base_datos():
    """Crear la base de datos desde cero"""
    
    with app.app_context():
        print("🗄️  Creando base de datos...")
        
        # Crear todas las tablas
        db.create_all()
        print("✅ Tablas creadas")
        
        # Crear sucursales
        sucursales = [
            "INC TECHNOLOGY",
            "Sucursal Centro", 
            "Sucursal Norte",
            "Sucursal Sur",
            "Sucursal Este",
            "Sucursal Oeste",
            "Sucursal Plaza",
            "Sucursal Universidad",
            "Sucursal Industrial"
        ]
        
        print("🏢 Creando sucursales...")
        for nombre in sucursales:
            sucursal = Sucursal(nombre=nombre, activa=True)
            db.session.add(sucursal)
            print(f"   ✅ {nombre}")
        
        # Crear admin
        print("👤 Creando administrador...")
        admin = Usuario(
            username='admin',
            email='admin@sisagent.com',
            password_hash=generate_password_hash('61442159'),
            nombre_completo='Administrador SISAGENT',
            es_admin=True,
            activo=True
        )
        db.session.add(admin)
        print("   ✅ Administrador creado")
        
        # Guardar todo
        db.session.commit()
        print("✅ Base de datos creada exitosamente")
        
        # Verificar
        total_sucursales = Sucursal.query.count()
        print(f"📊 Total sucursales: {total_sucursales}")
        
        return True

if __name__ == "__main__":
    print("🚀 CREANDO BASE DE DATOS")
    print("=" * 30)
    
    try:
        crear_base_datos()
        print("\n✅ LISTO!")
        print("Ahora ejecuta: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}") 