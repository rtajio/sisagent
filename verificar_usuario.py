#!/usr/bin/env python3
"""
Script para verificar el estado del usuario actual
"""

from app import app, db, Usuario, Sucursal

def verificar_usuario_admin():
    """Verificar el estado del usuario administrador"""
    
    with app.app_context():
        print("🔍 Verificando usuario administrador...")
        
        # Buscar el usuario admin
        admin = Usuario.query.filter_by(username='admin').first()
        
        if admin:
            print(f"✅ Usuario encontrado: {admin.username}")
            print(f"   - Email: {admin.email}")
            print(f"   - Nombre: {admin.nombre_completo}")
            print(f"   - Es admin: {admin.es_admin}")
            print(f"   - Activo: {admin.activo}")
            print(f"   - Sucursal ID: {admin.sucursal_id}")
            
            # Verificar sucursales
            sucursales = Sucursal.query.filter_by(activa=True).all()
            print(f"\n📊 Sucursales activas: {len(sucursales)}")
            for sucursal in sucursales:
                print(f"   - ID: {sucursal.id} | Nombre: {sucursal.nombre}")
            
            return admin.es_admin and len(sucursales) > 0
        else:
            print("❌ Usuario admin no encontrado")
            return False

def simular_consulta_sucursales():
    """Simular la consulta que hace la función registrar_operacion"""
    
    with app.app_context():
        print("\n🧪 Simulando consulta de sucursales...")
        
        # Buscar el usuario admin
        admin = Usuario.query.filter_by(username='admin').first()
        
        if admin:
            print(f"Usuario: {admin.username}")
            print(f"Es admin: {admin.es_admin}")
            
            if admin.es_admin:
                sucursales = Sucursal.query.filter_by(activa=True).all()
                print(f"Sucursales encontradas: {len(sucursales)}")
                
                for sucursal in sucursales:
                    print(f"   - {sucursal.id}: {sucursal.nombre}")
                
                return len(sucursales)
            else:
                print("❌ El usuario no es administrador")
                return 0
        else:
            print("❌ Usuario no encontrado")
            return 0

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN DE USUARIO")
    print("=" * 30)
    
    try:
        # Verificar usuario admin
        admin_ok = verificar_usuario_admin()
        
        if admin_ok:
            # Simular consulta
            total_sucursales = simular_consulta_sucursales()
            
            if total_sucursales > 0:
                print(f"\n✅ TODO CORRECTO")
                print(f"   - Usuario admin: OK")
                print(f"   - Sucursales disponibles: {total_sucursales}")
                print(f"\n🎯 El dropdown debería mostrar {total_sucursales + 1} opciones")
                print("   (1 opción vacía + {total_sucursales} sucursales)")
            else:
                print(f"\n❌ PROBLEMA: No hay sucursales disponibles")
        else:
            print(f"\n❌ PROBLEMA: Usuario admin no está configurado correctamente")
            
    except Exception as e:
        print(f"\n❌ Error: {e}") 