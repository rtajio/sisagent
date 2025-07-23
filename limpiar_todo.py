#!/usr/bin/env python3
"""
Script para limpiar completamente la base de datos
"""

import os
import sqlite3
from app import app, db, Sucursal, Usuario, Operacion
from werkzeug.security import generate_password_hash
from datetime import datetime
import pytz

def limpiar_todo():
    """Limpiar completamente la base de datos"""
    
    print("🧹 LIMPIANDO TODO")
    print("=" * 20)
    
    # 1. Eliminar TODOS los archivos de base de datos
    print("1. Eliminando TODOS los archivos de base de datos...")
    for file in os.listdir('.'):
        if file.endswith('.db') or file.endswith('.sqlite') or file.endswith('.sqlite3'):
            try:
                os.remove(file)
                print(f"   ✅ Eliminado: {file}")
            except Exception as e:
                print(f"   ⚠️  No se pudo eliminar {file}: {e}")
    
    # 2. Crear nueva base de datos desde cero
    print("\n2. Creando nueva base de datos desde cero...")
    with app.app_context():
        # Eliminar todas las tablas si existen
        db.drop_all()
        print("   ✅ Tablas eliminadas")
        
        # Crear todas las tablas
        db.create_all()
        print("   ✅ Tablas creadas")
        
        # 3. Crear sucursal
        print("\n3. Creando sucursal...")
        sucursal = Sucursal(
            nombre="Sucursal Principal",
            direccion="Dirección Principal",
            activa=True
        )
        db.session.add(sucursal)
        db.session.commit()
        print(f"   ✅ Sucursal creada: {sucursal.id}")
        
        # 4. Crear usuario admin
        print("\n4. Creando usuario admin...")
        admin = Usuario(
            username='admin',
            email='admin@sisagent.com',
            password_hash=generate_password_hash('admin123'),
            nombre_completo='Administrador SISAGENT',
            es_admin=True,
            sucursal_id=sucursal.id,
            activo=True
        )
        db.session.add(admin)
        db.session.commit()
        print("   ✅ Usuario admin creado")
        
        # 5. Crear usuario normal
        print("\n5. Creando usuario normal...")
        usuario = Usuario(
            username='usuario1',
            email='usuario1@sisagent.com',
            password_hash=generate_password_hash('password123'),
            nombre_completo='Usuario Normal',
            es_admin=False,
            sucursal_id=sucursal.id,
            activo=True
        )
        db.session.add(usuario)
        db.session.commit()
        print("   ✅ Usuario normal creado")
        
        # 6. Crear operaciones de prueba
        print("\n6. Creando operaciones de prueba...")
        peru_tz = pytz.timezone('America/Lima')
        hora_actual = datetime.now(peru_tz)
        
        operacion1 = Operacion(
            monto=100.0,
            comision=1.0,
            medio='BCP',
            hora=hora_actual,
            usuario_id=usuario.id,
            sucursal_id=sucursal.id
        )
        db.session.add(operacion1)
        
        operacion2 = Operacion(
            monto=200.0,
            comision=2.0,
            medio='KS',
            hora=hora_actual,
            usuario_id=usuario.id,
            sucursal_id=sucursal.id
        )
        db.session.add(operacion2)
        
        db.session.commit()
        print("   ✅ Operaciones creadas")
        
        # 7. Verificar estado final
        print("\n7. Verificando estado final...")
        usuarios_count = Usuario.query.count()
        sucursales_count = Sucursal.query.count()
        operaciones_count = Operacion.query.count()
        
        print(f"   - Usuarios: {usuarios_count}")
        print(f"   - Sucursales: {sucursales_count}")
        print(f"   - Operaciones: {operaciones_count}")
        
        print("\n🎉 TODO LIMPIO Y LISTO")
        print("Ahora puedes iniciar el servidor con: python app.py")
        return True

if __name__ == "__main__":
    limpiar_todo() 