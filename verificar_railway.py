#!/usr/bin/env python3
"""
Script para verificar el estado de Railway
"""

import os
import sys
import requests
from datetime import datetime
import pytz

def verificar_variables_entorno():
    """Verificar que las variables de entorno estén configuradas"""
    
    print("=== VERIFICACIÓN DE VARIABLES DE ENTORNO ===\n")
    
    # Variables requeridas para Railway
    variables_requeridas = [
        'DATABASE_URL',
        'SECRET_KEY',
        'PORT'
    ]
    
    variables_opcionales = [
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID',
        'RAILWAY_SERVICE_ID'
    ]
    
    print("🔍 Variables requeridas:")
    for var in variables_requeridas:
        valor = os.environ.get(var)
        if valor:
            if var == 'DATABASE_URL':
                # Ocultar parte de la URL por seguridad
                if 'postgresql://' in valor:
                    print(f"   ✅ {var}: postgresql://***:***@***")
                else:
                    print(f"   ✅ {var}: {valor[:20]}...")
            elif var == 'SECRET_KEY':
                print(f"   ✅ {var}: {'*' * len(valor)}")
            else:
                print(f"   ✅ {var}: {valor}")
        else:
            print(f"   ❌ {var}: NO CONFIGURADA")
    
    print("\n🔍 Variables opcionales de Railway:")
    for var in variables_opcionales:
        valor = os.environ.get(var)
        if valor:
            print(f"   ✅ {var}: {valor}")
        else:
            print(f"   ⚠️  {var}: No configurada (opcional)")
    
    # Verificar si estamos en Railway
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        print("\n🚂 Detectado entorno Railway")
        print(f"   Entorno: {os.environ.get('RAILWAY_ENVIRONMENT')}")
        print(f"   Proyecto ID: {os.environ.get('RAILWAY_PROJECT_ID', 'N/A')}")
        print(f"   Servicio ID: {os.environ.get('RAILWAY_SERVICE_ID', 'N/A')}")
    else:
        print("\n💻 Entorno local detectado")

def verificar_configuracion_app():
    """Verificar la configuración de la aplicación"""
    
    print("\n=== VERIFICACIÓN DE CONFIGURACIÓN DE APP ===\n")
    
    # Verificar archivos de configuración
    archivos_config = [
        'railway.toml',
        'Procfile',
        'wsgi.py',
        'requirements.txt',
        'init_db.py'
    ]
    
    print("📁 Archivos de configuración:")
    for archivo in archivos_config:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}: Existe")
        else:
            print(f"   ❌ {archivo}: NO EXISTE")
    
    # Verificar contenido de railway.toml
    if os.path.exists('railway.toml'):
        print("\n📋 Contenido de railway.toml:")
        try:
            with open('railway.toml', 'r') as f:
                contenido = f.read()
                print("   " + contenido.replace('\n', '\n   '))
        except Exception as e:
            print(f"   ❌ Error al leer railway.toml: {e}")
    
    # Verificar contenido de Procfile
    if os.path.exists('Procfile'):
        print("\n📋 Contenido de Procfile:")
        try:
            with open('Procfile', 'r') as f:
                contenido = f.read()
                print("   " + contenido.replace('\n', '\n   '))
        except Exception as e:
            print(f"   ❌ Error al leer Procfile: {e}")

def verificar_rutas_health():
    """Verificar que las rutas de health check estén disponibles"""
    
    print("\n=== VERIFICACIÓN DE RUTAS DE HEALTH CHECK ===\n")
    
    # URLs de health check
    health_urls = [
        '/health',
        '/railway-health',
        '/api/health'
    ]
    
    # Obtener la URL base
    port = os.environ.get('PORT', '5000')
    base_url = f"http://localhost:{port}"
    
    print(f"🌐 URL base: {base_url}")
    
    for url in health_urls:
        full_url = base_url + url
        try:
            response = requests.get(full_url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {url}: OK (200)")
            else:
                print(f"   ⚠️  {url}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ {url}: Error - {e}")

def verificar_base_datos():
    """Verificar la configuración de base de datos"""
    
    print("\n=== VERIFICACIÓN DE BASE DE DATOS ===\n")
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL no configurada")
        return
    
    if database_url.startswith('postgresql://'):
        print("✅ Base de datos PostgreSQL configurada")
        print("   Tipo: PostgreSQL (Railway)")
    elif database_url.startswith('sqlite://'):
        print("✅ Base de datos SQLite configurada")
        print("   Tipo: SQLite (Local)")
    else:
        print(f"⚠️  Tipo de base de datos desconocido: {database_url[:20]}...")
    
    # Verificar si podemos importar la app
    try:
        from app import app, db
        print("✅ Aplicación Flask importada correctamente")
        
        # Verificar conexión a base de datos
        with app.app_context():
            try:
                db.engine.execute("SELECT 1")
                print("✅ Conexión a base de datos exitosa")
            except Exception as e:
                print(f"❌ Error de conexión a base de datos: {e}")
                
    except ImportError as e:
        print(f"❌ Error al importar la aplicación: {e}")

def generar_comandos_railway():
    """Generar comandos útiles para Railway"""
    
    print("\n=== COMANDOS ÚTILES PARA RAILWAY ===\n")
    
    print("🚀 Para desplegar en Railway:")
    print("   1. railway login")
    print("   2. railway link")
    print("   3. railway up")
    
    print("\n🔍 Para verificar el estado:")
    print("   railway status")
    print("   railway logs")
    
    print("\n⚙️  Para configurar variables de entorno:")
    print("   railway variables set SECRET_KEY=tu-clave-secreta")
    print("   railway variables set DATABASE_URL=tu-url-postgresql")
    
    print("\n🌐 Para obtener la URL del proyecto:")
    print("   railway domain")

def main():
    """Función principal"""
    
    print("🚂 VERIFICACIÓN DE CONFIGURACIÓN RAILWAY")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now(pytz.timezone('America/Lima')).strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    verificar_variables_entorno()
    verificar_configuracion_app()
    verificar_base_datos()
    generar_comandos_railway()
    
    print("\n" + "=" * 50)
    print("✅ Verificación completada")
    
    # Resumen final
    print("\n📊 RESUMEN:")
    print("   - Si todas las variables están configuradas: ✅ Listo para Railway")
    print("   - Si faltan variables: ⚠️  Configurar variables de entorno")
    print("   - Si hay errores de archivos: ❌ Revisar configuración")

if __name__ == "__main__":
    main() 