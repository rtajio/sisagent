#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar y corregir problemas de login
"""

import os
import sys
import io

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def diagnosticar_login():
    """Diagnosticar el problema de login"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO DE LOGIN")
    print("=" * 60)
    
    try:
        from app import app, db, Usuario, asegurar_admin_existe
        from werkzeug.security import check_password_hash
        
        with app.app_context():
            print("\n1️⃣ Verificando conexión a base de datos...")
            try:
                # Intentar una consulta simple
                count = db.session.query(Usuario).count()
                print(f"   ✅ Conexión OK - {count} usuarios en la base de datos")
            except Exception as e:
                print(f"   ❌ Error de conexión: {e}")
                return False
            
            print("\n2️⃣ Asegurando que admin existe...")
            try:
                asegurar_admin_existe()
                print("   ✅ Función asegurar_admin_existe() ejecutada")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()
                return False
            
            print("\n3️⃣ Buscando usuario admin...")
            try:
                admin = Usuario.query.filter_by(username='admin').first()
                if not admin:
                    print("   ❌ Usuario 'admin' no encontrado")
                    return False
                print(f"   ✅ Usuario encontrado: ID={admin.id}, es_admin={admin.es_admin}")
            except Exception as e:
                print(f"   ❌ Error al buscar usuario: {e}")
                db.session.rollback()
                return False
            
            print("\n4️⃣ Verificando password_hash...")
            if not admin.password_hash:
                print("   ❌ ERROR: El usuario no tiene password_hash")
                print("   🔧 Intentando corregir...")
                try:
                    asegurar_admin_existe()
                    db.session.refresh(admin)
                    if not admin.password_hash:
                        print("   ❌ No se pudo corregir")
                        return False
                    print("   ✅ Corregido")
                except Exception as e:
                    print(f"   ❌ Error al corregir: {e}")
                    return False
            else:
                print(f"   ✅ Password hash existe: {admin.password_hash[:50]}...")
            
            print("\n5️⃣ Probando verificación de contraseña...")
            password = '61442159'
            try:
                password_ok = check_password_hash(admin.password_hash, password)
                if password_ok:
                    print(f"   ✅ Contraseña '{password}' es CORRECTA")
                else:
                    print(f"   ❌ Contraseña '{password}' es INCORRECTA")
                    print("   🔧 Intentando actualizar contraseña...")
                    try:
                        asegurar_admin_existe()
                        db.session.refresh(admin)
                        password_ok = check_password_hash(admin.password_hash, password)
                        if password_ok:
                            print("   ✅ Contraseña actualizada y verificada")
                        else:
                            print("   ❌ No se pudo actualizar la contraseña")
                            return False
                    except Exception as e:
                        print(f"   ❌ Error al actualizar: {e}")
                        return False
            except Exception as e:
                print(f"   ❌ Error al verificar contraseña: {e}")
                return False
            
            print("\n" + "=" * 60)
            print("✅ DIAGNÓSTICO COMPLETADO")
            print("=" * 60)
            print(f"👤 USUARIO: admin")
            print(f"🔑 CONTRASEÑA: {password}")
            print(f"✅ Estado: LISTO PARA LOGIN")
            print("=" * 60)
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    diagnosticar_login()

