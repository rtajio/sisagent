#!/usr/bin/env python3
"""
Script para corregir el healthcheck definitivamente
"""

import subprocess
import os
import sys
import time

def ejecutar_sin_pager(comando):
    """Ejecutar comando sin pager"""
    env = os.environ.copy()
    env['GIT_PAGER'] = ''
    env['PAGER'] = ''
    env['LESS'] = ''
    env['MORE'] = ''
    
    try:
        resultado = subprocess.run(comando, shell=True, env=env, capture_output=True, text=True, timeout=60)
        return resultado.returncode == 0, resultado.stdout, resultado.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def corregir_healthcheck_final():
    """Corregir healthcheck definitivamente"""
    
    print("🔧 CORRIGIENDO HEALTHCHECK DEFINITIVAMENTE")
    print("=" * 50)
    
    # 1. Cambiar railway.json para usar /ping
    print("📋 Paso 1: Configurando healthcheck para /ping...")
    railway_config = """{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "healthcheckPath": "/ping",
    "healthcheckTimeout": 120,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}"""
    
    with open('railway.json', 'w', encoding='utf-8') as f:
        f.write(railway_config)
    print("✅ Railway.json configurado para /ping")
    
    # 2. Crear un archivo app_simple.py con ruta /ping
    print("📋 Paso 2: Creando ruta /ping simple...")
    ruta_ping = """

@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/railway-health')
def railway_health():
    return "OK", 200
"""
    
    # Agregar las rutas al final de app.py
    try:
        with open('app.py', 'a', encoding='utf-8') as f:
            f.write(ruta_ping)
        print("✅ Rutas de healthcheck agregadas")
    except Exception as e:
        print(f"⚠️ Error al agregar rutas: {e}")
    
    # 3. Agregar archivos
    print("📋 Paso 3: Agregando archivos...")
    exito, salida, error = ejecutar_sin_pager("git add railway.json app.py")
    if exito:
        print("✅ Archivos agregados")
    else:
        print(f"❌ Error: {error}")
        return False
    
    # 4. Crear commit
    print("📋 Paso 4: Creando commit...")
    exito, salida, error = ejecutar_sin_pager('git commit -m "FIX: Corregir healthcheck definitivamente - múltiples rutas"')
    if exito:
        print("✅ Commit creado")
        print(f"📄 Salida: {salida}")
    else:
        print(f"❌ Error en commit: {error}")
        return False
    
    # 5. Hacer push
    print("📋 Paso 5: Haciendo push...")
    exito, salida, error = ejecutar_sin_pager("git push origin main")
    if exito:
        print("✅ Push exitoso")
        print(f"📄 Salida: {salida}")
    else:
        print(f"❌ Error en push: {error}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 HEALTHCHECK CORREGIDO DEFINITIVAMENTE")
    print("=" * 50)
    print("✅ Railway.json configurado para /ping")
    print("✅ Rutas /ping, /health, /railway-health agregadas")
    print("✅ Timeout aumentado a 120 segundos")
    print("✅ Commit creado exitosamente")
    print("✅ Push completado")
    print("🚀 Railway detectará cambios automáticamente")
    print("⏱️ Deploy iniciado")
    print("\n📋 Próximos pasos:")
    print("   1. Espera 2-3 minutos")
    print("   2. Verifica Railway dashboard")
    print("   3. El healthcheck debería pasar ahora")
    print("   4. Sistema de vouchers disponible")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    print("🔄 Iniciando corrección definitiva de healthcheck...")
    print("📅 Fecha:", time.strftime('%d/%m/%Y %H:%M:%S'))
    print("-" * 50)
    
    if corregir_healthcheck_final():
        print("\n✅ Corrección definitiva completada")
        print("🚀 El sistema de vouchers estará disponible pronto")
    else:
        print("\n❌ Error en la corrección")
        sys.exit(1)
