#!/usr/bin/env python3
"""
Script para crear sucursales de ejemplo y verificar la funcionalidad del dropdown
"""

from app import app, db, Sucursal

def crear_sucursales_ejemplo():
    """Crear sucursales de ejemplo para probar el dropdown"""
    
    with app.app_context():
        # Lista de sucursales de ejemplo
        sucursales_ejemplo = [
            {"nombre": "Sucursal Centro", "direccion": "Av. Principal 123, Centro"},
            {"nombre": "Sucursal Norte", "direccion": "Calle Norte 456, Zona Norte"},
            {"nombre": "Sucursal Sur", "direccion": "Av. Sur 789, Zona Sur"},
            {"nombre": "Sucursal Este", "direccion": "Calle Este 321, Zona Este"},
            {"nombre": "Sucursal Oeste", "direccion": "Av. Oeste 654, Zona Oeste"},
            {"nombre": "Sucursal Plaza", "direccion": "Plaza Mayor 987, Centro Comercial"},
            {"nombre": "Sucursal Universidad", "direccion": "Campus Universitario, Zona Académica"},
            {"nombre": "Sucursal Industrial", "direccion": "Parque Industrial 147, Zona Industrial"}
        ]
        
        print("🏢 Creando sucursales de ejemplo...")
        
        sucursales_creadas = 0
        for sucursal_data in sucursales_ejemplo:
            # Verificar si la sucursal ya existe
            sucursal_existente = Sucursal.query.filter_by(nombre=sucursal_data["nombre"]).first()
            
            if not sucursal_existente:
                nueva_sucursal = Sucursal(
                    nombre=sucursal_data["nombre"],
                    direccion=sucursal_data["direccion"],
                    activa=True
                )
                db.session.add(nueva_sucursal)
                sucursales_creadas += 1
                print(f"✅ Creada: {sucursal_data['nombre']}")
            else:
                print(f"⚠️  Ya existe: {sucursal_data['nombre']}")
        
        # Confirmar cambios
        if sucursales_creadas > 0:
            db.session.commit()
            print(f"\n🎉 Se crearon {sucursales_creadas} sucursales nuevas")
        else:
            print("\nℹ️  No se crearon sucursales nuevas (ya existían)")
        
        # Mostrar todas las sucursales activas
        print("\n📋 Sucursales disponibles:")
        sucursales_activas = Sucursal.query.filter_by(activa=True).all()
        for i, sucursal in enumerate(sucursales_activas, 1):
            print(f"{i}. {sucursal.nombre} - {sucursal.direccion}")
        
        return len(sucursales_activas)

def verificar_dropdown():
    """Verificar que el dropdown de sucursales funcione correctamente"""
    
    with app.app_context():
        # Obtener sucursales activas
        sucursales = Sucursal.query.filter_by(activa=True).all()
        
        print(f"\n🔍 Verificando dropdown de sucursales...")
        print(f"📊 Total de sucursales activas: {len(sucursales)}")
        
        if len(sucursales) > 0:
            print("✅ El dropdown debería mostrar las siguientes opciones:")
            print("   - Seleccione una sucursal (opción vacía)")
            for sucursal in sucursales:
                print(f"   - {sucursal.nombre}")
            
            print("\n🎯 Para probar:")
            print("1. Accede a http://localhost:5000")
            print("2. Inicia sesión como administrador (admin/61442159)")
            print("3. Ve a 'Operaciones' → 'Nueva Operación'")
            print("4. Verifica que el dropdown de sucursales muestre las opciones")
        else:
            print("❌ No hay sucursales activas para mostrar en el dropdown")
            print("   Ejecuta este script primero para crear sucursales de ejemplo")

if __name__ == "__main__":
    print("🚀 INICIANDO CONFIGURACIÓN DE SUCURSALES")
    print("=" * 50)
    
    # Crear sucursales de ejemplo
    total_sucursales = crear_sucursales_ejemplo()
    
    # Verificar dropdown
    verificar_dropdown()
    
    print("\n" + "=" * 50)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("\n📝 Próximos pasos:")
    print("1. Ejecuta 'python app.py' para iniciar el servidor")
    print("2. Accede a http://localhost:5000")
    print("3. Inicia sesión como administrador")
    print("4. Ve a 'Operaciones' → 'Nueva Operación'")
    print("5. Verifica que el dropdown de sucursales funcione correctamente") 