#!/usr/bin/env python3
"""
Script simple para verificar que las sucursales están disponibles
"""

from app import app, db, Sucursal

def verificar_sucursales():
    """Verificar que las sucursales están disponibles en la base de datos"""
    
    with app.app_context():
        print("🔍 Verificando sucursales en la base de datos...")
        
        # Obtener todas las sucursales activas
        sucursales = Sucursal.query.filter_by(activa=True).all()
        
        print(f"📊 Total de sucursales activas: {len(sucursales)}")
        
        if len(sucursales) > 0:
            print("✅ Sucursales disponibles:")
            for i, sucursal in enumerate(sucursales, 1):
                print(f"   {i}. ID: {sucursal.id} | Nombre: {sucursal.nombre} | Dirección: {sucursal.direccion}")
            
            print(f"\n🎯 Para probar el dropdown:")
            print("1. Accede a http://localhost:5000")
            print("2. Inicia sesión como administrador (admin/61442159)")
            print("3. Ve a 'Operaciones' → 'Nueva Operación'")
            print("4. Verifica que el dropdown de sucursales muestre las opciones")
            
            return True
        else:
            print("❌ No hay sucursales activas en la base de datos")
            print("   Ejecuta 'python crear_sucursales.py' para crear sucursales de ejemplo")
            return False

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DE SUCURSALES")
    print("=" * 40)
    
    success = verificar_sucursales()
    
    if success:
        print("\n✅ VERIFICACIÓN COMPLETADA")
        print("   Las sucursales están disponibles para el dropdown")
    else:
        print("\n❌ VERIFICACIÓN FALLÓ")
        print("   No hay sucursales disponibles") 