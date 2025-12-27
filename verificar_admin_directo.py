#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las credenciales del administrador directamente en SQLite
"""

import os
import sys
import sqlite3
import io
from werkzeug.security import check_password_hash

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def verificar_admin_en_db(db_path):
    """Verificar admin en una base de datos SQLite específica"""
    if not os.path.exists(db_path):
        print(f"⚠️  Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si la tabla usuario existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
        if not cursor.fetchone():
            print(f"⚠️  La tabla 'usuario' no existe en {db_path}")
            conn.close()
            return False
        
        # Buscar el usuario admin
        cursor.execute("SELECT id, username, password_hash, es_admin FROM usuario WHERE username = 'admin'")
        admin = cursor.fetchone()
        
        if not admin:
            print(f"❌ El usuario 'admin' no existe en {db_path}")
            conn.close()
            return False
        
        admin_id, username, password_hash, es_admin = admin
        
        print(f"✅ Usuario encontrado en {os.path.basename(db_path)}:")
        print(f"   ID: {admin_id}")
        print(f"   Username: {username}")
        print(f"   Es Admin: {es_admin}")
        print(f"   Password Hash: {password_hash[:50]}..." if password_hash else "   Password Hash: None")
        
        # Verificar contraseña
        contraseñas_a_verificar = ['61442159']
        
        print("\n🔐 VERIFICANDO CONTRASEÑAS:")
        print("-" * 60)
        
        contraseña_correcta = None
        for password in contraseñas_a_verificar:
            if password_hash:
                if check_password_hash(password_hash, password):
                    print(f"✅ CONTRASEÑA CORRECTA: '{password}'")
                    contraseña_correcta = password
                    break
                else:
                    print(f"❌ Contraseña '{password}' NO es correcta")
            else:
                print(f"⚠️  El usuario no tiene password_hash configurado")
        
        conn.close()
        
        if contraseña_correcta:
            return contraseña_correcta
        else:
            return False
            
    except Exception as e:
        print(f"❌ ERROR al verificar {db_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Verificar admin en todas las bases de datos disponibles"""
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CREDENCIALES DE ADMINISTRADOR")
    print("=" * 60)
    print()
    
    # Bases de datos a verificar
    bases_datos = [
        "instance/sisagent_consolidada.db",
        "instance/sisagent.db",
        "sisagent_consolidada.db",
        "sisagent.db"
    ]
    
    credenciales_encontradas = []
    
    for db_path in bases_datos:
        if os.path.exists(db_path):
            print(f"\n📂 Verificando: {db_path}")
            print("-" * 60)
            resultado = verificar_admin_en_db(db_path)
            if resultado:
                credenciales_encontradas.append((db_path, resultado))
    
    print("\n" + "=" * 60)
    if credenciales_encontradas:
        print("✅ CREDENCIALES VERIFICADAS CORRECTAMENTE")
        print("=" * 60)
        print(f"👤 USUARIO: admin")
        print(f"🔑 CONTRASEÑA: {credenciales_encontradas[0][1]}")
        print("=" * 60)
        print(f"\n✅ Verificado en {len(credenciales_encontradas)} base(s) de datos:")
        for db_path, password in credenciales_encontradas:
            print(f"   - {db_path}")
    else:
        print("❌ ERROR: No se encontraron credenciales válidas en ninguna base de datos")
        print("=" * 60)

if __name__ == '__main__':
    main()

