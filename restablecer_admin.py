#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restablecer contraseña del admin a 61442159"""

import sqlite3
import sys
import os
from werkzeug.security import generate_password_hash

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def restablecer_password_admin():
    """Restablecer la contraseña del admin a 61442159"""
    
    print("=" * 80)
    print("🔧 RESTABLECIENDO CONTRASEÑA DEL ADMIN")
    print("=" * 80)
    print()
    
    nueva_password = '61442159'
    nueva_hash = generate_password_hash(nueva_password)
    
    # Buscar base de datos
    db_files = [
        "instance/sisagent_consolidada.db",
        "sisagent_consolidada.db",
        "instance/sisagent.db",
        "sisagent.db"
    ]
    
    actualizado = False
    
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
                    
                    if admin_id:
                        # Actualizar contraseña
                        cursor.execute(
                            "UPDATE usuario SET password_hash = ? WHERE username = 'admin'",
                            (nueva_hash,)
                        )
                        conn.commit()
                        print(f"   ✅ Contraseña actualizada para admin")
                        print(f"   🔑 Nueva contraseña: {nueva_password}")
                        actualizado = True
                    else:
                        # Crear admin si no existe
                        cursor.execute(
                            "INSERT INTO usuario (username, password_hash, es_admin) VALUES (?, ?, ?)",
                            ('admin', nueva_hash, 1)
                        )
                        conn.commit()
                        print(f"   ✅ Usuario admin creado")
                        print(f"   🔑 Contraseña: {nueva_password}")
                        actualizado = True
                
                conn.close()
                print()
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print()
    
    print("=" * 80)
    if actualizado:
        print("✅ CONTRASEÑA RESTABLECIDA EXITOSAMENTE")
    else:
        print("⚠️  No se encontraron bases de datos para actualizar")
    print("=" * 80)
    print(f"👤 Usuario: admin")
    print(f"🔑 Contraseña: {nueva_password}")
    print("=" * 80)
    print()
    print("✅ Ya puedes ingresar con estas credenciales")

if __name__ == "__main__":
    restablecer_password_admin()

