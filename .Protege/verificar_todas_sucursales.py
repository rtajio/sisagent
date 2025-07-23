#!/usr/bin/env python3
"""
Script para verificar todas las sucursales en la base de datos
"""

from app import app, db, Sucursal

def verificar_todas_sucursales():
    """Verificar todas las sucursales en la base de datos"""
    
    with app.app_context():
        print("🔍 Verificando todas las sucursales...")
        
        # Obtener todas las sucursales
        todas_sucursales = Sucursal.query.all()
        print(f"📊 Total de sucursales en la base de datos: {len(todas_sucursales)}")
        
        print("\n📋 Lista completa de sucursales:")
        for sucursal in todas_sucursales:
            estado = "✅ ACTIVA" if sucursal.activa else "❌ INACTIVA"
            print(f"   - ID: {sucursal.id} | {sucursal.nombre} | {estado}")
        
        # Obtener solo las activas
        sucursales_activas = Sucursal.query.filter_by(activa=True).all()
        print(f"\n✅ Sucursales activas: {len(sucursales_activas)}")
        
        # Obtener solo las inactivas
        sucursales_inactivas = Sucursal.query.filter_by(activa=False).all()
        print(f"❌ Sucursales inactivas: {len(sucursales_inactivas)}")
        
        return len(sucursales_activas)

def activar_todas_sucursales():
    """Activar todas las sucursales"""
    
    with app.app_context():
        print("\n🔄 Activando todas las sucursales...")
        
        # Obtener todas las sucursales
        todas_sucursales = Sucursal.query.all()
        
        for sucursal in todas_sucursales:
            if not sucursal.activa:
                sucursal.activa = True
                print(f"   ✅ Activada: {sucursal.nombre}")
        
        # Guardar cambios
        db.session.commit()
        print("✅ Todas las sucursales han sido activadas")

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN COMPLETA DE SUCURSALES")
    print("=" * 40)
    
    try:
        # Verificar estado actual
        total_activas = verificar_todas_sucursales()
        
        if total_activas < 9:
            print(f"\n⚠️  PROBLEMA: Solo hay {total_activas} sucursales activas")
            print("   Se necesitan 9 sucursales activas para el dropdown")
            
            # Preguntar si activar todas
            print("\n🔄 ¿Activar todas las sucursales? (s/n)")
            respuesta = input("Respuesta: ").lower().strip()
            
            if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
                activar_todas_sucursales()
                
                # Verificar estado final
                print("\n🔍 Verificando estado final...")
                total_final = verificar_todas_sucursales()
                
                if total_final >= 9:
                    print(f"\n✅ PROBLEMA RESUELTO")
                    print(f"   Ahora hay {total_final} sucursales activas")
                    print(f"   El dropdown debería mostrar {total_final + 1} opciones")
                else:
                    print(f"\n❌ PROBLEMA PERSISTE")
                    print(f"   Solo hay {total_final} sucursales activas")
            else:
                print("\n❌ No se activaron las sucursales")
        else:
            print(f"\n✅ TODO CORRECTO")
            print(f"   Hay {total_activas} sucursales activas")
            print(f"   El dropdown debería mostrar {total_activas + 1} opciones")
            
    except Exception as e:
        print(f"\n❌ Error: {e}") 