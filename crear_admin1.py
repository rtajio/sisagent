#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear el usuario admin1 con privilegios de administrador
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

from app import app, db, Usuario
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def crear_admin1():
    """Crear usuario admin1 con privilegios de administrador"""
    with app.app_context():
        try:
            username = 'admin1'
            password = 'admin1'
            password_hash = generate_password_hash(password)
            email = f'{username}@sisagent.com'
            
            # Verificar si el usuario ya existe
            usuario_existente = Usuario.query.filter_by(username=username).first()
            
            if usuario_existente:
                print(f"⚠️  El usuario '{username}' ya existe")
                print(f"   Actualizando contraseña y privilegios...")
                
                # Actualizar usando SQL directo para asegurar que todos los campos se actualicen
                db.session.execute(
                    text("""
                        UPDATE usuario 
                        SET password_hash = :password_hash,
                            es_admin = 1,
                            es_admin_sucursal = 0
                        WHERE username = :username
                    """),
                    {'password_hash': password_hash, 'username': username}
                )
                db.session.commit()
                print(f"✅ Usuario '{username}' actualizado exitosamente")
                print(f"   Contraseña: {password}")
                print(f"   Es Admin Global: Sí")
            else:
                print(f"🔧 Creando usuario '{username}'...")
                
                # Crear usando SQL directo con todos los campos requeridos
                db.session.execute(
                    text("""
                        INSERT INTO usuario (username, password_hash, email, nombre_completo, es_admin, es_admin_sucursal, activo)
                        VALUES (:username, :password_hash, :email, :nombre_completo, 1, 0, 1)
                    """),
                    {
                        'username': username,
                        'password_hash': password_hash,
                        'email': email,
                        'nombre_completo': 'Administrador 1'
                    }
                )
                db.session.commit()
                print(f"✅ Usuario '{username}' creado exitosamente")
                print(f"   Contraseña: {password}")
                print(f"   Es Admin Global: Sí")
            
            # Verificar que se creó correctamente
            usuario_verificado = Usuario.query.filter_by(username=username).first()
            if usuario_verificado:
                print(f"\n✅ Verificación exitosa:")
                print(f"   ID: {usuario_verificado.id}")
                print(f"   Username: {usuario_verificado.username}")
                print(f"   Es Admin: {usuario_verificado.es_admin}")
                if hasattr(usuario_verificado, 'es_admin_sucursal'):
                    print(f"   Es Admin de Sucursal: {usuario_verificado.es_admin_sucursal}")
                print(f"\n📋 Credenciales:")
                print(f"   Usuario: {username}")
                print(f"   Contraseña: {password}")
                return True
            else:
                print(f"❌ Error: No se pudo verificar el usuario")
                return False
                
        except Exception as e:
            print(f"❌ ERROR al crear usuario: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔧 CREAR USUARIO ADMIN1")
    print("=" * 60)
    print()
    
    if crear_admin1():
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ PROCESO FALLIDO")
        print("=" * 60)

