#!/usr/bin/env python3
"""
Script para crear el usuario 73800418 en Railway
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Configurar para Railway
os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/sisagent'

try:
    from app import app, db, Usuario
    
    with app.app_context():
        print("🔧 CREANDO USUARIO 73800418 EN RAILWAY")
        print("=" * 50)
        
        # Verificar si el usuario ya existe
        usuario_existente = Usuario.query.filter_by(username='73800418').first()
        
        if usuario_existente:
            print(f"✅ Usuario 73800418 ya existe en Railway:")
            print(f"  - ID: {usuario_existente.id}")
            print(f"  - Nombre: {usuario_existente.nombre_completo}")
            print(f"  - Admin: {usuario_existente.es_admin}")
        else:
            print("❌ Usuario 73800418 no existe en Railway. Creando...")
            
            # Crear el usuario
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
            
            print(f"✅ Usuario 73800418 creado exitosamente en Railway:")
            print(f"  - ID: {nuevo_usuario.id}")
            print(f"  - Username: 73800418")
            print(f"  - Password: 61442159")
            print(f"  - Admin: {nuevo_usuario.es_admin}")
        
        # Listar todos los usuarios
        usuarios = Usuario.query.all()
        print(f"\n👥 Total usuarios en Railway: {len(usuarios)}")
        for user in usuarios:
            print(f"  - ID: {user.id}, Username: {user.username}, Nombre: {user.nombre_completo}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔍 Verificando configuración...")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'No configurada')}") 