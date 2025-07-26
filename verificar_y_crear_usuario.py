#!/usr/bin/env python3
"""
Script para verificar usuarios y crear el usuario 73800418
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Usuario

def verificar_y_crear_usuario():
    """Verificar usuarios y crear el usuario 73800418"""
    with app.app_context():
        try:
            print("🔍 VERIFICANDO USUARIOS EN LA BASE DE DATOS")
            print("=" * 60)
            
            # Listar todos los usuarios
            usuarios = Usuario.query.all()
            print(f"👥 Total usuarios: {len(usuarios)}")
            
            for user in usuarios:
                print(f"  - ID: {user.id}, Username: {user.username}, Nombre: {user.nombre_completo}, Admin: {user.es_admin}")
            
            # Buscar usuario 73800418
            usuario_73800418 = Usuario.query.filter_by(username='73800418').first()
            
            if usuario_73800418:
                print(f"\n✅ Usuario 73800418 ya existe:")
                print(f"  - ID: {usuario_73800418.id}")
                print(f"  - Nombre: {usuario_73800418.nombre_completo}")
                print(f"  - Admin: {usuario_73800418.es_admin}")
                print(f"  - Sucursal: {usuario_73800418.sucursal_id}")
            else:
                print(f"\n❌ Usuario 73800418 no existe. Creando...")
                
                # Crear el usuario 73800418
                nuevo_usuario = Usuario(
                    username='73800418',
                    email='73800418@sisagent.pe',
                    password_hash=generate_password_hash('61442159'),
                    nombre_completo='Usuario 73800418',
                    es_admin=False,
                    activo=True
                )
                
                db.session.add(nuevo_usuario)
                db.session.commit()
                
                print(f"✅ Usuario 73800418 creado exitosamente:")
                print(f"  - ID: {nuevo_usuario.id}")
                print(f"  - Username: 73800418")
                print(f"  - Password: 61442159")
                print(f"  - Admin: {nuevo_usuario.es_admin}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    verificar_y_crear_usuario() 