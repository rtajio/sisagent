#!/usr/bin/env python3
"""
Script para crear las sucursales faltantes
"""

from app import app, db, Sucursal

def crear_sucursales_faltantes():
    """Crear las sucursales que faltan"""
    
    with app.app_context():
        print("🏢 Creando sucursales faltantes...")
        
        # Lista de sucursales que deberían existir
        sucursales_esperadas = [
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
        
        # Verificar cuáles ya existen
        sucursales_existentes = Sucursal.query.all()
        nombres_existentes = [s.nombre for s in sucursales_existentes]
        
        print(f"📊 Sucursales existentes: {len(sucursales_existentes)}")
        for sucursal in sucursales_existentes:
            print(f"   - {sucursal.nombre}")
        
        # Crear las que faltan
        sucursales_creadas = 0
        for nombre in sucursales_esperadas:
            if nombre not in nombres_existentes:
                nueva_sucursal = Sucursal(nombre=nombre, activa=True)
                db.session.add(nueva_sucursal)
                print(f"   ✅ Creada: {nombre}")
                sucursales_creadas += 1
            else:
                print(f"   ⚠️  Ya existe: {nombre}")
        
        # Guardar cambios
        if sucursales_creadas > 0:
            db.session.commit()
            print(f"\n✅ Se crearon {sucursales_creadas} sucursales nuevas")
        else:
            print("\nℹ️  No se crearon sucursales nuevas")
        
        # Verificar estado final
        total_sucursales = Sucursal.query.filter_by(activa=True).count()
        print(f"\n📊 Estado final:")
        print(f"   - Total sucursales activas: {total_sucursales}")
        
        # Mostrar todas las sucursales
        print(f"\n🏢 Lista completa de sucursales:")
        sucursales = Sucursal.query.filter_by(activa=True).all()
        for i, sucursal in enumerate(sucursales, 1):
            print(f"   {i}. {sucursal.nombre}")
        
        return total_sucursales

if __name__ == "__main__":
    print("🚀 CREANDO SUCURSALES FALTANTES")
    print("=" * 35)
    
    try:
        total = crear_sucursales_faltantes()
        
        if total >= 9:
            print(f"\n✅ PROBLEMA RESUELTO")
            print(f"   Ahora hay {total} sucursales activas")
            print(f"   El dropdown debería mostrar {total + 1} opciones")
            print(f"\n🎯 Próximos pasos:")
            print(f"1. Recarga la página del navegador")
            print(f"2. Ve a 'Operaciones' → 'Nueva Operación'")
            print(f"3. Verifica que el dropdown muestre todas las opciones")
        else:
            print(f"\n❌ PROBLEMA PERSISTE")
            print(f"   Solo hay {total} sucursales activas")
            
    except Exception as e:
        print(f"\n❌ Error: {e}") 