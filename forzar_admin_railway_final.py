#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para forzar la actualización del admin en Railway
Actualiza la contraseña directamente en la base de datos
"""

import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def forzar_admin_railway():
    """Forzar actualización del admin en Railway"""
    
    print("=" * 80)
    print("🔧 FORZANDO ACTUALIZACIÓN DEL ADMIN EN RAILWAY")
    print("=" * 80)
    print()
    
    nueva_password = '61442159'
    nueva_hash = generate_password_hash(nueva_password)
    
    # Verificar si hay DATABASE_URL (Railway usa PostgreSQL)
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("⚠️  No se encontró DATABASE_URL")
        print("   Esto significa que estás en desarrollo local")
        print()
        print("💡 Para ejecutar en Railway:")
        print("   1. Conecta a Railway CLI")
        print("   2. Ejecuta: railway run python forzar_admin_railway_final.py")
        print()
        return False
    
    print(f"📂 Conectando a base de datos de Railway...")
    print(f"   {database_url[:30]}...")
    print()
    
    try:
        # Importar dependencias necesarias
        from app import app, db, Usuario
        
        with app.app_context():
            print("🔍 Buscando usuario admin...")
            
            # Buscar usuario admin
            admin = Usuario.query.filter_by(username='admin').first()
            
            if admin:
                print(f"   ✅ Usuario admin encontrado (ID: {admin.id})")
                print(f"   🔐 Hash actual: {admin.password_hash[:50] if admin.password_hash else 'None'}...")
                
                # Verificar contraseña actual
                if admin.password_hash:
                    password_actual_ok = check_password_hash(admin.password_hash, nueva_password)
                    print(f"   🔍 Verificación contraseña actual: {'✅ Correcta' if password_actual_ok else '❌ Incorrecta'}")
                
                # FORZAR actualización
                print()
                print("   🔧 Actualizando contraseña...")
                admin.password_hash = nueva_hash
                admin.es_admin = True  # Asegurar que sea admin
                
                # Si hay campo activo, asegurar que esté activo
                if hasattr(admin, 'activo'):
                    admin.activo = True
                
                db.session.commit()
                
                # Verificar que se actualizó correctamente
                admin_verificado = Usuario.query.filter_by(username='admin').first()
                if admin_verificado and check_password_hash(admin_verificado.password_hash, nueva_password):
                    print(f"   ✅ Contraseña actualizada correctamente")
                    print(f"   🔑 Nueva contraseña: {nueva_password}")
                    print(f"   ✅ Verificación exitosa: La contraseña funciona")
                else:
                    print(f"   ❌ Error: La contraseña no se actualizó correctamente")
                    return False
                    
            else:
                print("   ⚠️  Usuario admin no encontrado, creándolo...")
                
                # Crear admin
                admin = Usuario(
                    username='admin',
                    password_hash=nueva_hash,
                    es_admin=True
                )
                
                # Si hay campos adicionales, establecerlos
                if hasattr(Usuario, 'activo'):
                    admin.activo = True
                if hasattr(Usuario, 'nombre_completo'):
                    admin.nombre_completo = 'Administrador'
                if hasattr(Usuario, 'email'):
                    admin.email = 'admin@sisagent.com'
                
                db.session.add(admin)
                db.session.commit()
                
                # Verificar que se creó correctamente
                admin_verificado = Usuario.query.filter_by(username='admin').first()
                if admin_verificado and check_password_hash(admin_verificado.password_hash, nueva_password):
                    print(f"   ✅ Usuario admin creado correctamente")
                    print(f"   🔑 Contraseña: {nueva_password}")
                    print(f"   ✅ Verificación exitosa: La contraseña funciona")
                else:
                    print(f"   ❌ Error: El admin no se creó correctamente")
                    return False
            
            print()
            print("=" * 80)
            print("✅ ACTUALIZACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)
            print(f"👤 Usuario: admin")
            print(f"🔑 Contraseña: {nueva_password}")
            print()
            print("✅ Ya puedes ingresar al sistema con estas credenciales")
            print("=" * 80)
            
            return True
            
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    exito = forzar_admin_railway()
    print()
    if not exito:
        print("💡 Si estás en desarrollo local, ejecuta este script después")
        print("   de hacer deploy a Railway para actualizar la BD remota")
        print()
        print("   Comando en Railway:")
        print("   railway run python forzar_admin_railway_final.py")
    sys.exit(0 if exito else 1)

