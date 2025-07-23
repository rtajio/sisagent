#!/usr/bin/env python3
"""
Script para verificar y crear datos sin conflictos
"""

from app import app, db, Sucursal, Usuario
from werkzeug.security import generate_password_hash

def verificar_y_crear():
    """Verificar datos existentes y crear los que faltan"""
    
    with app.app_context():
        print("🔍 Verificando datos existentes...")
        
        # Verificar si ya hay sucursales
        sucursales_existentes = Sucursal.query.count()
        print(f"📊 Sucursales existentes: {sucursales_existentes}")
        
        # Verificar si ya hay usuarios
        usuarios_existentes = Usuario.query.count()
        print(f"👥 Usuarios existentes: {usuarios_existentes}")
        
        # Crear sucursales si no existen
        if sucursales_existentes == 0:
            print("🏢 Creando sucursales...")
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
            
            for nombre in sucursales:
                sucursal = Sucursal(nombre=nombre, activa=True)
                db.session.add(sucursal)
                print(f"   ✅ {nombre}")
            
            db.session.commit()
            print("✅ Sucursales creadas")
        else:
            print("✅ Las sucursales ya existen")
        
        # Verificar si existe el admin
        admin_existente = Usuario.query.filter_by(username='admin').first()
        if not admin_existente:
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
            db.session.commit()
            print("✅ Administrador creado")
        else:
            print("✅ El administrador ya existe")
        
        # Verificar datos finales
        total_sucursales = Sucursal.query.filter_by(activa=True).count()
        total_usuarios = Usuario.query.count()
        
        print(f"\n📊 Estado final:")
        print(f"   - Sucursales activas: {total_sucursales}")
        print(f"   - Usuarios totales: {total_usuarios}")
        
        # Mostrar sucursales disponibles
        print(f"\n🏢 Sucursales disponibles:")
        sucursales = Sucursal.query.filter_by(activa=True).all()
        for i, sucursal in enumerate(sucursales, 1):
            print(f"   {i}. {sucursal.nombre}")
        
        return total_sucursales > 0

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN Y CREACIÓN DE DATOS")
    print("=" * 40)
    
    try:
        success = verificar_y_crear()
        
        if success:
            print("\n✅ VERIFICACIÓN COMPLETADA")
            print("\n🎯 Próximos pasos:")
            print("1. Ejecuta 'python app.py'")
            print("2. Accede a http://localhost:5000")
            print("3. Inicia sesión con admin/61442159")
            print("4. Ve a 'Operaciones' → 'Nueva Operación'")
            print("5. Verifica que el dropdown de sucursales funcione")
        else:
            print("\n❌ Error: No se pudieron crear los datos")
            
    except Exception as e:
        print(f"\n❌ Error: {e}") 