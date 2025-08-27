#!/usr/bin/env python3
"""
Script para solucionar el crash de Railway
"""

import os
import shutil
from datetime import datetime

def solucionar_crash():
    """Solucionar el crash de Railway"""
    
    print("🔧 SOLUCIONANDO CRASH DE RAILWAY")
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 50)
    
    try:
        print("📋 PASO 1: Creando configuración estable...")
        
        # 1. Crear un Procfile más simple
        procfile_simple = '''web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload'''
        
        with open('Procfile', 'w', encoding='utf-8') as f:
            f.write(procfile_simple)
        print("   ✅ Procfile simplificado")
        
        # 2. Crear railway.toml mínimo
        railway_toml = '''[build]
builder = "nixpacks"

[deploy]
startCommand = "gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120"
'''
        
        with open('railway.toml', 'w', encoding='utf-8') as f:
            f.write(railway_toml)
        print("   ✅ railway.toml simplificado")
        
        # 3. Eliminar wsgi.py para usar app.py directamente
        if os.path.exists('wsgi.py'):
            os.remove('wsgi.py')
            print("   🗑️ wsgi.py eliminado")
        
        # 4. Verificar que app.py tenga la configuración correcta
        print("\n📋 PASO 2: Verificando app.py...")
        
        if os.path.exists('app.py'):
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar que tenga la configuración de Railway
            if 'DATABASE_URL' in content and 'os.environ.get' in content:
                print("   ✅ app.py tiene configuración de Railway")
            else:
                print("   ⚠️ app.py necesita configuración de Railway")
        
        print("\n📋 PASO 3: Limpiando archivos problemáticos...")
        
        # Eliminar archivos que pueden causar problemas
        archivos_a_eliminar = [
            'gunicorn.conf.py',
            'runtime.txt'
        ]
        
        for archivo in archivos_a_eliminar:
            if os.path.exists(archivo):
                os.remove(archivo)
                print(f"   🗑️ {archivo} eliminado")
        
        print("\n" + "=" * 50)
        print("✅ CONFIGURACIÓN ESTABLE CREADA")
        print("=" * 50)
        
        print("\n🎯 CAMBIOS REALIZADOS:")
        print("   ✅ Procfile simplificado - Sin wsgi")
        print("   ✅ railway.toml mínimo - Sin healthcheck")
        print("   ✅ wsgi.py eliminado - Usar app.py directo")
        print("   ✅ Archivos problemáticos eliminados")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Hacer commit y push de los cambios")
        print("   2. Railway detectará los cambios automáticamente")
        print("   3. Deploy estable sin crash")
        print("   4. Sistema funcional con datos preservados")
        
        print("\n🔒 PROTECCIÓN DE DATOS:")
        print("   🔒 Base de datos: NO SE TOCA")
        print("   🔒 Operaciones: TODAS CONSERVADAS")
        print("   🔒 Usuarios: TODOS CONSERVADOS")
        print("   🔒 Sucursales: TODAS CONSERVADAS")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la solución: {e}")
        return False

if __name__ == '__main__':
    solucionar_crash()
