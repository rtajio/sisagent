#!/usr/bin/env python3
"""
Script para verificar el estado real de la base de datos
"""

from app import app, db, Sucursal, Usuario

def verificar_estado_real():
    """Verificar el estado real de la base de datos"""
    
    with app.app_context():
        print("🔍 VERIFICACIÓN EN TIEMPO REAL")
        print("=" * 35)
        
        # Verificar sucursales
        total_sucursales = Sucursal.query.count()
        sucursales_activas = Sucursal.query.filter_by(activa=True).count()
        
        print(f"📊 Sucursales:")
        print(f"   - Total: {total_sucursales}")
        print(f"   - Activas: {sucursales_activas}")
        
        # Mostrar todas las sucursales
        print(f"\n🏢 Lista de sucursales:")
        sucursales = Sucursal.query.all()
        for sucursal in sucursales:
            estado = "✅ ACTIVA" if sucursal.activa else "❌ INACTIVA"
            print(f"   - ID: {sucursal.id} | {sucursal.nombre} | {estado}")
        
        # Verificar usuarios
        total_usuarios = Usuario.query.count()
        admin = Usuario.query.filter_by(username='admin').first()
        
        print(f"\n👥 Usuarios:")
        print(f"   - Total: {total_usuarios}")
        if admin:
            print(f"   - Admin: {admin.username} (es_admin: {admin.es_admin})")
        
        # Simular la consulta exacta que hace la función registrar_operacion:
        print(f"\n🧪 Simulando consulta de la función registrar_operacion:")
        if admin and admin.es_admin:
            sucursales_para_dropdown = Sucursal.query.filter_by(activa=True).all()
            print(f"   - Usuario es admin: ✅")
            print(f"   - Sucursales para dropdown: {len(sucursales_para_dropdown)}")
            
            for sucursal in sucursales_para_dropdown:
                print(f"     * {sucursal.id}: {sucursal.nombre}")
        else:
            print(f"   - Usuario NO es admin: ❌")
        
        return sucursales_activas

if __name__ == "__main__":
    try:
        total = verificar_estado_real()
        
        if total >= 9:
            print(f"\n✅ BASE DE DATOS CORRECTA")
            print(f"   Hay {total} sucursales activas")
            print(f"   El problema podría estar en el servidor web")
            print(f"\n🎯 Prueba manual:")
            print(f"1. Ve a http://localhost:5000")
            print(f"2. Inicia sesión como admin")
            print(f"3. Ve a 'Operaciones' → 'Nueva Operación'")
            print(f"4. Verifica el dropdown de sucursales")
        else:
            print(f"\n❌ PROBLEMA EN BASE DE DATOS")
            print(f"   Solo hay {total} sucursales activas")
            
    except Exception as e:
        print(f"\n❌ Error: {e}") 