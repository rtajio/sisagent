#!/usr/bin/env python3
"""
Script para debuggear la función registrar_operacion en tiempo real
"""

from app import app, db, Sucursal, Usuario
from flask_login import login_user
from werkzeug.security import generate_password_hash

def debug_funcion_registrar():
    """Debuggear la función registrar_operacion"""
    
    with app.app_context():
        print("🔍 DEBUGGEANDO FUNCIÓN REGISTRAR_OPERACION")
        print("=" * 50)
        
        # 1. Verificar usuario admin
        print("1. Verificando usuario admin...")
        admin = Usuario.query.filter_by(username='admin').first()
        
        if admin:
            print(f"✅ Usuario admin encontrado: {admin.username}")
            print(f"   - Es admin: {admin.es_admin}")
            print(f"   - Activo: {admin.activo}")
        else:
            print("❌ Usuario admin no encontrado")
            return False
        
        # 2. Simular la consulta exacta de la función
        print("\n2. Simulando consulta de sucursales...")
        
        if admin.es_admin:
            sucursales = Sucursal.query.filter_by(activa=True).all()
            print(f"✅ Consulta exitosa: {len(sucursales)} sucursales encontradas")
            
            print("📋 Sucursales encontradas:")
            for sucursal in sucursales:
                print(f"   - ID: {sucursal.id} | Nombre: {sucursal.nombre} | Activa: {sucursal.activa}")
            
            return len(sucursales) > 0
        else:
            print("❌ Usuario no es administrador")
            return False

def simular_template_render():
    """Simular el renderizado del template"""
    
    with app.app_context():
        print("\n3. Simulando renderizado del template...")
        
        # Obtener sucursales como lo hace la función
        admin = Usuario.query.filter_by(username='admin').first()
        sucursales = Sucursal.query.filter_by(activa=True).all() if admin and admin.es_admin else None
        
        print(f"📊 Variables para el template:")
        print(f"   - sucursales: {sucursales}")
        print(f"   - Tipo de sucursales: {type(sucursales)}")
        
        if sucursales:
            print(f"   - Cantidad de sucursales: {len(sucursales)}")
            print(f"   - Primera sucursal: {sucursales[0].nombre if sucursales else 'N/A'}")
        else:
            print("   - sucursales es None")
        
        return sucursales is not None and len(sucursales) > 0

def verificar_base_datos_servidor():
    """Verificar si el servidor está usando la misma base de datos"""
    
    with app.app_context():
        print("\n4. Verificando base de datos del servidor...")
        
        # Verificar archivo de base de datos
        import os
        db_files = [f for f in os.listdir('.') if f.endswith('.db')]
        print(f"📁 Archivos de base de datos encontrados: {db_files}")
        
        # Verificar configuración de la base de datos
        from app import app
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        print(f"🔗 URI de la base de datos: {db_uri}")
        
        # Verificar conexión
        try:
            db.engine.connect()
            print("✅ Conexión a la base de datos exitosa")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
        
        return True

if __name__ == "__main__":
    print("🚀 DEBUG COMPLETO")
    print("=" * 50)
    
    try:
        # Debuggear función
        funcion_ok = debug_funcion_registrar()
        
        # Simular template
        template_ok = simular_template_render()
        
        # Verificar base de datos
        db_ok = verificar_base_datos_servidor()
        
        print("\n📊 RESUMEN DEL DEBUG:")
        print(f"   - Función registrar_operacion: {'✅ OK' if funcion_ok else '❌ ERROR'}")
        print(f"   - Template render: {'✅ OK' if template_ok else '❌ ERROR'}")
        print(f"   - Base de datos: {'✅ OK' if db_ok else '❌ ERROR'}")
        
        if funcion_ok and template_ok and db_ok:
            print("\n✅ TODO ESTÁ CORRECTO EN EL BACKEND")
            print("   El problema podría estar en:")
            print("   1. Caché del navegador")
            print("   2. Sesión del usuario")
            print("   3. Problema de JavaScript en el frontend")
        else:
            print("\n❌ PROBLEMA IDENTIFICADO EN EL BACKEND")
            print("   Revisa los errores anteriores")
            
    except Exception as e:
        print(f"\n❌ Error durante el debug: {e}") 