#!/usr/bin/env python3
"""
Script para limpiar completamente y recrear la base de datos
"""

import os
from app import app, db, Sucursal, Usuario
from werkzeug.security import generate_password_hash

def limpiar_y_recrear():
    """Limpiar completamente y recrear la base de datos"""
    
    print("🧹 LIMPIANDO Y RECREANDO BASE DE DATOS")
    print("=" * 40)
    
    # 1. Eliminar archivos de base de datos existentes
    print("1. Eliminando archivos de base de datos...")
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    for db_file in db_files:
        try:
            os.remove(db_file)
            print(f"   ✅ Eliminado: {db_file}")
        except Exception as e:
            print(f"   ⚠️  No se pudo eliminar {db_file}: {e}")
    
    # 2. Crear nueva base de datos
    print("\n2. Creando nueva base de datos...")
    with app.app_context():
        db.create_all()
        print("   ✅ Tablas creadas")
        
        # 3. Crear sucursales
        print("\n3. Creando sucursales...")
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
            print(f"   ✅ Creada: {nombre}")
        
        # 4. Crear usuario administrador
        print("\n4. Creando usuario administrador...")
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
        
        # 5. Guardar todo
        db.session.commit()
        print("\n✅ Base de datos recreada exitosamente")
        
        # 6. Verificar
        total_sucursales = Sucursal.query.filter_by(activa=True).count()
        total_usuarios = Usuario.query.count()
        
        print(f"\n📊 Verificación final:")
        print(f"   - Sucursales activas: {total_sucursales}")
        print(f"   - Usuarios totales: {total_usuarios}")
        
        # Mostrar sucursales
        print(f"\n🏢 Sucursales disponibles:")
        sucursales = Sucursal.query.filter_by(activa=True).all()
        for i, sucursal in enumerate(sucursales, 1):
            print(f"   {i}. {sucursal.nombre}")
        
        return total_sucursales >= 9 and total_usuarios >= 1

if __name__ == "__main__":
    try:
        success = limpiar_y_recrear()
        
        if success:
            print(f"\n🎉 RECREACIÓN EXITOSA")
            print(f"   La base de datos está lista para usar")
            print(f"\n🎯 Próximos pasos:")
            print(f"1. Ejecuta 'python app.py'")
            print(f"2. Ve a http://localhost:5000")
            print(f"3. Inicia sesión con admin/61442159")
            print(f"4. Ve a 'Operaciones' → 'Nueva Operación'")
            print(f"5. Verifica que el dropdown muestre las 9 sucursales")
        else:
            print(f"\n❌ ERROR EN LA RECREACIÓN")
            print(f"   Revisa los errores anteriores")
            
    except Exception as e:
        print(f"\n❌ Error durante la recreación: {e}") 