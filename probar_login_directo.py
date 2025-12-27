#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para probar el login directamente
"""

import os
import sys
import sqlite3
import io
from werkzeug.security import check_password_hash, generate_password_hash

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def probar_login(db_path, username, password):
    """Probar el login directamente"""
    if not os.path.exists(db_path):
        print(f"⚠️  Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Buscar el usuario
        cursor.execute("SELECT id, username, password_hash, es_admin FROM usuario WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Usuario '{username}' no encontrado")
            conn.close()
            return False
        
        user_id, db_username, password_hash, es_admin = user
        
        print(f"✅ Usuario encontrado:")
        print(f"   ID: {user_id}")
        print(f"   Username: {db_username}")
        print(f"   Es Admin: {es_admin}")
        print(f"   Password Hash: {password_hash[:60]}..." if password_hash else "   Password Hash: None")
        
        # Verificar contraseña
        if not password_hash:
            print("❌ ERROR: El usuario no tiene password_hash")
            conn.close()
            return False
        
        # Probar la verificación
        print(f"\n🔐 Probando contraseña: '{password}'")
        print("-" * 60)
        
        password_ok = check_password_hash(password_hash, password)
        
        if password_ok:
            print("✅ CONTRASEÑA CORRECTA - Login debería funcionar")
        else:
            print("❌ CONTRASEÑA INCORRECTA - Login fallará")
            print("\n🔧 Intentando generar nuevo hash...")
            nuevo_hash = generate_password_hash(password)
            print(f"   Nuevo hash: {nuevo_hash[:60]}...")
            print(f"   Verificando nuevo hash: {check_password_hash(nuevo_hash, password)}")
            
            # Comparar hashes
            print(f"\n📊 Comparación de hashes:")
            print(f"   Hash actual: {password_hash}")
            print(f"   Hash nuevo:  {nuevo_hash}")
            print(f"   ¿Son iguales? {password_hash == nuevo_hash}")
        
        conn.close()
        return password_ok
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Probar login con diferentes credenciales"""
    print("=" * 60)
    print("🔍 PRUEBA DE LOGIN DIRECTO")
    print("=" * 60)
    
    # Bases de datos a verificar
    bases_datos = [
        "instance/sisagent_consolidada.db",
        "instance/sisagent.db"
    ]
    
    username = "admin"
    passwords = ["61442159", "admin123", "admin"]
    
    for db_path in bases_datos:
        if os.path.exists(db_path):
            print(f"\n📂 Probando en: {db_path}")
            print("=" * 60)
            
            for password in passwords:
                print(f"\n🔐 Probando: usuario='{username}', password='{password}'")
                print("-" * 60)
                resultado = probar_login(db_path, username, password)
                if resultado:
                    print(f"\n✅ LOGIN EXITOSO con:")
                    print(f"   Usuario: {username}")
                    print(f"   Contraseña: {password}")
                    print(f"   Base de datos: {db_path}")
                    return
                print()

if __name__ == '__main__':
    main()

