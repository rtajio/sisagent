#!/usr/bin/env python3
"""
Script para verificar la base de datos de Railway
"""

import os
import sys

# Configurar para Railway
os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/sisagent'

try:
    from app import app, db, Operacion, Usuario
    
    with app.app_context():
        print("🔍 VERIFICANDO BASE DE DATOS RAILWAY")
        print("=" * 50)
        
        # Verificar conexión
        with db.engine.connect() as conn:
            # Contar operaciones totales
            result = conn.execute(db.text("SELECT COUNT(*) FROM operacion"))
            total_operaciones = result.fetchone()[0]
            print(f"📊 Total operaciones: {total_operaciones}")
            
            # Buscar usuario 73800418
            result = conn.execute(db.text("SELECT id, username, nombre FROM usuario WHERE username = '73800418'"))
            usuario = result.fetchone()
            if usuario:
                print(f"✅ Usuario 73800418 encontrado: ID={usuario[0]}, Nombre={usuario[2]}")
                
                # Operaciones del usuario
                result = conn.execute(db.text(f"SELECT COUNT(*) FROM operacion WHERE usuario_id = {usuario[0]}"))
                operaciones_usuario = result.fetchone()[0]
                print(f"📊 Operaciones del usuario 73800418: {operaciones_usuario}")
                
                # Últimas operaciones del usuario
                result = conn.execute(db.text(f"""
                    SELECT id, monto, comision, hora 
                    FROM operacion 
                    WHERE usuario_id = {usuario[0]} 
                    ORDER BY hora DESC 
                    LIMIT 10
                """))
                operaciones = result.fetchall()
                
                print(f"\n🕐 Últimas operaciones del usuario 73800418:")
                for op in operaciones:
                    print(f"  - ID: {op[0]}, Monto: {op[1]}, Comisión: {op[2]}, Hora: {op[3]}")
            else:
                print("❌ Usuario 73800418 no encontrado")
            
            # Verificar usuarios totales
            result = conn.execute(db.text("SELECT COUNT(*) FROM usuario"))
            total_usuarios = result.fetchone()[0]
            print(f"\n👥 Total usuarios: {total_usuarios}")
            
            # Listar usuarios
            result = conn.execute(db.text("SELECT id, username, nombre FROM usuario"))
            usuarios = result.fetchall()
            print(f"\n👥 Usuarios en el sistema:")
            for user in usuarios:
                print(f"  - ID: {user[0]}, Username: {user[1]}, Nombre: {user[2]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("🔍 Verificando configuración...")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'No configurada')}") 