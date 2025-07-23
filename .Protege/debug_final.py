#!/usr/bin/env python3
"""
Debug final para encontrar el problema
"""

from app import app, db, Sucursal, Usuario
from flask_login import login_user

def debug_final():
    """Debug final del problema"""
    
    print("🔍 DEBUG FINAL")
    print("=" * 20)
    
    with app.app_context():
        # 1. Verificar usuario admin
        admin = Usuario.query.filter_by(username='admin').first()
        print(f"1. Usuario admin: {admin.username if admin else 'No encontrado'}")
        print(f"   - Es admin: {admin.es_admin if admin else 'N/A'}")
        print(f"   - Activo: {admin.activo if admin else 'N/A'}")
        
        # 2. Verificar sucursales
        sucursales = Sucursal.query.filter_by(activa=True).all()
        print(f"\n2. Sucursales activas: {len(sucursales)}")
        
        # 3. Simular la función exacta
        print(f"\n3. Simulando función registrar_operacion:")
        if admin and admin.es_admin:
            sucursales_funcion = Sucursal.query.filter_by(activa=True).all()
            print(f"   - Resultado: {len(sucursales_funcion)} sucursales")
            print(f"   - Tipo: {type(sucursales_funcion)}")
            
            if sucursales_funcion:
                print(f"   - Primera sucursal: {sucursales_funcion[0].nombre}")
                print(f"   - Última sucursal: {sucursales_funcion[-1].nombre}")
            else:
                print(f"   - Lista vacía")
        else:
            print(f"   - Usuario no es admin")
        
        # 4. Verificar template
        print(f"\n4. Verificando template...")
        try:
            with open('templates/registrar_operacion.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'sucursales' in content:
                print(f"   ✅ Variable 'sucursales' encontrada en template")
            else:
                print(f"   ❌ Variable 'sucursales' NO encontrada en template")
            
            if 'for sucursal in sucursales' in content:
                print(f"   ✅ Bucle 'for sucursal in sucursales' encontrado")
            else:
                print(f"   ❌ Bucle 'for sucursal in sucursales' NO encontrado")
                
        except Exception as e:
            print(f"   ❌ Error leyendo template: {e}")
        
        return len(sucursales) > 0 and admin and admin.es_admin

if __name__ == "__main__":
    try:
        success = debug_final()
        
        if success:
            print(f"\n✅ DEBUG COMPLETADO")
            print(f"   Todo parece estar correcto")
            print(f"   El problema podría estar en el navegador")
        else:
            print(f"\n❌ PROBLEMA IDENTIFICADO")
            
    except Exception as e:
        print(f"\n❌ Error en debug: {e}") 