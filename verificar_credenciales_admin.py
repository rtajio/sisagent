#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar las credenciales del administrador
"""

import os
import sys
import io

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from werkzeug.security import check_password_hash

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar desde app.py
from app import app, db, Usuario

def verificar_credenciales_admin():
    """Verificar las credenciales del administrador"""
    with app.app_context():
        try:
            # Buscar el usuario admin
            admin = Usuario.query.filter_by(username='admin').first()
            
            if not admin:
                print("❌ ERROR: El usuario 'admin' no existe en la base de datos")
                return False
            
            print("=" * 60)
            print("🔍 VERIFICACIÓN DE CREDENCIALES DE ADMINISTRADOR")
            print("=" * 60)
            print(f"✅ Usuario encontrado: {admin.username}")
            print(f"   ID: {admin.id}")
            print(f"   Es Admin Global: {admin.es_admin}")
            if hasattr(admin, 'es_admin_sucursal'):
                print(f"   Es Admin de Sucursal: {admin.es_admin_sucursal}")
            if hasattr(admin, 'sucursal_id'):
                print(f"   Sucursal ID: {admin.sucursal_id}")
            
            # Contraseñas a verificar
            contraseñas_a_verificar = ['61442159']
            
            print("\n🔐 VERIFICANDO CONTRASEÑAS:")
            print("-" * 60)
            
            contraseña_correcta = None
            for password in contraseñas_a_verificar:
                if admin.password_hash:
                    if check_password_hash(admin.password_hash, password):
                        print(f"✅ CONTRASEÑA CORRECTA: '{password}'")
                        contraseña_correcta = password
                        break
                    else:
                        print(f"❌ Contraseña '{password}' NO es correcta")
                else:
                    print(f"⚠️  El usuario no tiene password_hash configurado")
            
            print("\n" + "=" * 60)
            if contraseña_correcta:
                print("✅ CREDENCIALES VERIFICADAS CORRECTAMENTE")
                print("=" * 60)
                print(f"👤 USUARIO: admin")
                print(f"🔑 CONTRASEÑA: {contraseña_correcta}")
                print("=" * 60)
                return True
            else:
                print("❌ ERROR: No se encontró una contraseña válida")
                print("=" * 60)
                return False
                
        except Exception as e:
            print(f"❌ ERROR al verificar credenciales: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    verificar_credenciales_admin()

