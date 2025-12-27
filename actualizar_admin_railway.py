#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la contraseña del admin en Railway (PostgreSQL)
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def actualizar_admin_railway():
    """Actualizar contraseña del admin en Railway"""
    
    print("=" * 80)
    print("🔧 ACTUALIZANDO CONTRASEÑA DEL ADMIN EN RAILWAY")
    print("=" * 80)
    print()
    
    nueva_password = '61442159'
    nueva_hash = generate_password_hash(nueva_password)
    
    # Verificar si hay DATABASE_URL (Railway usa PostgreSQL)
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("⚠️  No se encontró DATABASE_URL")
        print("   Esto significa que estás en desarrollo local")
        print("   La contraseña ya fue actualizada en las bases de datos locales")
        print()
        print("💡 Para actualizar en Railway:")
        print("   1. Este script se ejecutará automáticamente cuando se despliegue")
        print("   2. O puedes ejecutarlo manualmente en Railway")
        print()
        return False
    
    print(f"📂 Conectando a base de datos de Railway...")
    print(f"   {database_url[:30]}...")
    print()
    
    try:
        # Importar dependencias necesarias
        from app import app, db, Usuario
        
        with app.app_context():
            # Buscar usuario admin
            admin = Usuario.query.filter_by(username='admin').first()
            
            if admin:
                # Actualizar contraseña
                admin.password_hash = nueva_hash
                db.session.commit()
                print("✅ Contraseña del admin actualizada en Railway")
                print(f"   🔑 Nueva contraseña: {nueva_password}")
            else:
                # Crear admin si no existe
                admin = Usuario(
                    username='admin',
                    password_hash=nueva_hash,
                    es_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuario admin creado en Railway")
                print(f"   🔑 Contraseña: {nueva_password}")
            
            print()
            print("=" * 80)
            print("✅ ACTUALIZACIÓN COMPLETADA")
            print("=" * 80)
            print(f"👤 Usuario: admin")
            print(f"🔑 Contraseña: {nueva_password}")
            print("=" * 80)
            
            return True
            
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    actualizar_admin_railway()
    print()
    print("💡 NOTA: Si estás en desarrollo local, ejecuta este script")
    print("   después de hacer deploy a Railway para actualizar la BD remota")

