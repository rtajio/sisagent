#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar y solucionar problemas de login en Railway
"""

import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def diagnosticar_y_solucionar():
    """Diagnosticar y solucionar problemas de login"""
    
    print("=" * 80)
    print("🔍 DIAGNÓSTICO Y SOLUCIÓN DE LOGIN EN RAILWAY")
    print("=" * 80)
    print()
    
    nueva_password = '61442159'
    nueva_hash = generate_password_hash(nueva_password)
    
    # Verificar si hay DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("⚠️  No se encontró DATABASE_URL")
        print("   Ejecutando en modo local...")
        print()
    
    try:
        from app import app, db, Usuario
        
        with app.app_context():
            print("📋 Paso 1: Verificando estructura de la tabla Usuario...")
            print("-" * 80)
            
            # Obtener todas las columnas de la tabla
            inspector = db.inspect(db.engine)
            columns = inspector.get_columns('usuario')
            
            print("   Columnas encontradas en la tabla 'usuario':")
            for col in columns:
                print(f"      - {col['name']}: {col['type']}")
            print()
            
            print("📋 Paso 2: Buscando usuario admin...")
            print("-" * 80)
            
            # Buscar admin
            admin = Usuario.query.filter_by(username='admin').first()
            
            if not admin:
                print("   ❌ Usuario admin NO encontrado")
                print("   🔧 Creando usuario admin...")
                
                # Crear admin con todos los campos posibles
                admin_data = {
                    'username': 'admin',
                    'password_hash': nueva_hash,
                    'es_admin': True
                }
                
                # Agregar campos adicionales si existen
                if hasattr(Usuario, 'activo'):
                    admin_data['activo'] = True
                if hasattr(Usuario, 'nombre_completo'):
                    admin_data['nombre_completo'] = 'Administrador'
                if hasattr(Usuario, 'email'):
                    admin_data['email'] = 'admin@sisagent.com'
                if hasattr(Usuario, 'sucursal_id'):
                    # Buscar primera sucursal
                    from app import Sucursal
                    sucursal = Sucursal.query.first()
                    if sucursal:
                        admin_data['sucursal_id'] = sucursal.id
                
                admin = Usuario(**admin_data)
                db.session.add(admin)
                db.session.commit()
                
                print("   ✅ Usuario admin creado")
            else:
                print(f"   ✅ Usuario admin encontrado (ID: {admin.id})")
                print()
                
                print("📋 Paso 3: Verificando estado del admin...")
                print("-" * 80)
                
                # Verificar campos importantes
                print(f"   Username: {admin.username}")
                print(f"   Password hash: {'✅ Existe' if admin.password_hash else '❌ No existe'}")
                print(f"   Es admin: {admin.es_admin if hasattr(admin, 'es_admin') else 'N/A'}")
                
                if hasattr(admin, 'activo'):
                    print(f"   Activo: {admin.activo}")
                    if not admin.activo:
                        print("   ⚠️  El usuario está INACTIVO - esto puede bloquear el login")
                        admin.activo = True
                
                print()
                print("📋 Paso 4: Verificando contraseña actual...")
                print("-" * 80)
                
                if admin.password_hash:
                    # Probar contraseña
                    password_ok = check_password_hash(admin.password_hash, nueva_password)
                    print(f"   Contraseña actual funciona: {'✅ SÍ' if password_ok else '❌ NO'}")
                    
                    if not password_ok:
                        print("   🔧 Actualizando contraseña...")
                        admin.password_hash = nueva_hash
                else:
                    print("   ❌ No hay password_hash - creando uno nuevo...")
                    admin.password_hash = nueva_hash
                
                # Asegurar que sea admin
                if hasattr(admin, 'es_admin'):
                    admin.es_admin = True
                
                # Asegurar que esté activo
                if hasattr(admin, 'activo'):
                    admin.activo = True
                
                db.session.commit()
                print("   ✅ Cambios guardados")
            
            print()
            print("📋 Paso 5: Verificación final...")
            print("-" * 80)
            
            # Recargar admin de la BD
            db.session.refresh(admin)
            
            # Verificar que todo esté correcto
            verificaciones = []
            
            if admin.username == 'admin':
                verificaciones.append("✅ Username correcto")
            else:
                verificaciones.append(f"❌ Username incorrecto: {admin.username}")
            
            if admin.password_hash:
                if check_password_hash(admin.password_hash, nueva_password):
                    verificaciones.append("✅ Contraseña funciona correctamente")
                else:
                    verificaciones.append("❌ Contraseña NO funciona")
            else:
                verificaciones.append("❌ No hay password_hash")
            
            if hasattr(admin, 'es_admin') and admin.es_admin:
                verificaciones.append("✅ Es administrador")
            elif hasattr(admin, 'es_admin'):
                verificaciones.append("❌ NO es administrador")
            
            if hasattr(admin, 'activo'):
                if admin.activo:
                    verificaciones.append("✅ Usuario activo")
                else:
                    verificaciones.append("❌ Usuario INACTIVO")
            
            for verif in verificaciones:
                print(f"   {verif}")
            
            print()
            print("=" * 80)
            print("✅ DIAGNÓSTICO COMPLETADO")
            print("=" * 80)
            print()
            print("📊 RESUMEN:")
            print(f"   Usuario: admin")
            print(f"   Contraseña: {nueva_password}")
            print()
            
            # Verificar si hay problemas
            problemas = [v for v in verificaciones if v.startswith("❌")]
            if problemas:
                print("⚠️  PROBLEMAS ENCONTRADOS:")
                for problema in problemas:
                    print(f"   {problema}")
                print()
                print("💡 Estos problemas pueden estar bloqueando el login")
            else:
                print("✅ Todo está correcto - el login debería funcionar")
            
            print()
            print("=" * 80)
            
            return len(problemas) == 0
            
    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    exito = diagnosticar_y_solucionar()
    print()
    if exito:
        print("✅ El problema debería estar resuelto")
        print("   Intenta ingresar con: admin / 61442159")
    else:
        print("⚠️  Se encontraron problemas")
        print("   Revisa los mensajes arriba para más detalles")
    print()
    sys.exit(0 if exito else 1)

