#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y restablecer la contraseña del admin
"""

import sqlite3
import sys
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def verificar_admin():
    """Verificar información del usuario admin"""
    
    print("=" * 80)
    print("🔍 VERIFICANDO USUARIO ADMIN")
    print("=" * 80)
    print()
    
    # Buscar base de datos
    db_files = [
        "instance/sisagent_consolidada.db",
        "sisagent_consolidada.db",
        "instance/sisagent.db",
        "sisagent.db"
    ]
    
    admin_encontrado = False
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                print(f"📂 Verificando: {db_file}")
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Verificar si existe la tabla usuario
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
                if cursor.fetchone():
                    # Buscar admin
                    cursor.execute("SELECT username, password_hash, es_admin FROM usuario WHERE username='admin'")
                    admin = cursor.fetchone()
                    
                    if admin:
                        admin_encontrado = True
                        username, password_hash, es_admin = admin
                        
                        print(f"   ✅ Usuario admin encontrado")
                        print(f"   📝 Username: {username}")
                        print(f"   🔑 Es admin: {'Sí' if es_admin else 'No'}")
                        print(f"   🔐 Password hash: {password_hash[:50]}...")
                        print()
                        
                        # Probar contraseñas comunes
                        print("   🔍 Probando contraseñas comunes:")
                        contraseñas = ['61442159', 'admin123', 'admin', 'password', '123456']
                        
                        for pwd in contraseñas:
                            if password_hash and check_password_hash(password_hash, pwd):
                                print(f"      ✅ La contraseña es: {pwd}")
                                print()
                                print("=" * 80)
                                print("✅ CREDENCIALES ENCONTRADAS")
                                print("=" * 80)
                                print(f"👤 Usuario: admin")
                                print(f"🔑 Contraseña: {pwd}")
                                print("=" * 80)
                                conn.close()
                                return pwd
                            else:
                                print(f"      ❌ No es: {pwd}")
                        
                        print()
                        print("   ⚠️  Ninguna de las contraseñas comunes coincide")
                        print("   💡 Necesitas restablecer la contraseña")
                        
                conn.close()
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
    
    if not admin_encontrado:
        print("❌ No se encontró el usuario admin en ninguna base de datos")
        print()
        print("💡 Opciones:")
        print("   1. El usuario admin no existe")
        print("   2. Necesitas crear el usuario admin")
    
    return None

def restablecer_password_admin(nueva_password='61442159'):
    """Restablecer la contraseña del admin"""
    
    print("=" * 80)
    print("🔧 RESTABLECIENDO CONTRASEÑA DEL ADMIN")
    print("=" * 80)
    print()
    
    # Buscar base de datos
    db_files = [
        "instance/sisagent_consolidada.db",
        "sisagent_consolidada.db",
        "instance/sisagent.db",
        "sisagent.db"
    ]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            try:
                print(f"📂 Procesando: {db_file}")
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Verificar si existe la tabla usuario
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
                if cursor.fetchone():
                    # Verificar si existe admin
                    cursor.execute("SELECT id FROM usuario WHERE username='admin'")
                    admin_id = cursor.fetchone()
                    
                    nueva_hash = generate_password_hash(nueva_password)
                    
                    if admin_id:
                        # Actualizar contraseña
                        cursor.execute(
                            "UPDATE usuario SET password_hash = ? WHERE username = 'admin'",
                            (nueva_hash,)
                        )
                        conn.commit()
                        print(f"   ✅ Contraseña actualizada para admin")
                        print(f"   🔑 Nueva contraseña: {nueva_password}")
                    else:
                        # Crear admin si no existe
                        cursor.execute(
                            "INSERT INTO usuario (username, password_hash, es_admin) VALUES (?, ?, ?)",
                            ('admin', nueva_hash, 1)
                        )
                        conn.commit()
                        print(f"   ✅ Usuario admin creado")
                        print(f"   🔑 Contraseña: {nueva_password}")
                
                conn.close()
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
    
    print("=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)
    print(f"👤 Usuario: admin")
    print(f"🔑 Contraseña: {nueva_password}")
    print("=" * 80)

if __name__ == "__main__":
    print()
    
    # Primero verificar
    password = verificar_admin()
    
    if not password:
        print()
        respuesta = input("¿Deseas restablecer la contraseña del admin? (s/n): ").lower()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            nueva_pwd = input("Ingresa la nueva contraseña (Enter para usar '61442159'): ").strip()
            if not nueva_pwd:
                nueva_pwd = '61442159'
            restablecer_password_admin(nueva_pwd)
        else:
            print("Operación cancelada")

