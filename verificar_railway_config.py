#!/usr/bin/env python3
"""
Verificar configuración para Railway
"""

import os

def verificar_configuracion():
    """Verificar configuración para Railway"""
    
    print("🔍 VERIFICANDO CONFIGURACIÓN PARA RAILWAY")
    print("=" * 50)
    
    # Verificar archivos críticos
    archivos_criticos = [
        'app.py',
        'wsgi.py',
        'requirements.txt',
        'Procfile',
        'railway.toml',
        'init_db.py'
    ]
    
    print("📁 Archivos críticos:")
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} - FALTANTE")
    
    # Verificar variables de entorno
    print(f"\n🔧 Variables de entorno:")
    variables = ['DATABASE_URL', 'SECRET_KEY', 'PORT']
    for var in variables:
        valor = os.environ.get(var)
        if valor:
            if var == 'DATABASE_URL':
                print(f"   ✅ {var}: postgresql://***")
            elif var == 'SECRET_KEY':
                print(f"   ✅ {var}: {'*' * len(valor)}")
            else:
                print(f"   ✅ {var}: {valor}")
        else:
            print(f"   ❌ {var}: NO CONFIGURADA")
    
    # Verificar si estamos en Railway
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print(f"\n🚂 Entorno Railway detectado:")
        print(f"   Entorno: {os.environ.get('RAILWAY_ENVIRONMENT')}")
        print(f"   Proyecto ID: {os.environ.get('RAILWAY_PROJECT_ID', 'N/A')}")
    else:
        print(f"\n💻 Entorno local detectado")
    
    print(f"\n🎯 RECOMENDACIONES PARA SOLUCIONAR ERROR 502:")
    print("1. Verificar logs en Railway Dashboard")
    print("2. Asegurar que SECRET_KEY esté configurada")
    print("3. Verificar que DATABASE_URL esté configurada")
    print("4. Revisar que todos los archivos críticos estén presentes")
    print("5. Reiniciar la aplicación en Railway")

if __name__ == "__main__":
    verificar_configuracion() 