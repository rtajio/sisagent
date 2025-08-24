#!/usr/bin/env python3
"""
Script para corregir el error de los logs y hacer deploy exitoso
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

def corregir_logs():
    """Corregir el error de los logs y hacer deploy"""
    
    print("🔧 CORRIGIENDO ERROR DE LOGS")
    print("=" * 50)
    
    # 1. Verificar configuración actual
    print("📋 Paso 1: Verificando configuración...")
    with open('railway.json', 'r') as f:
        contenido = f.read()
        if '/railway-health' in contenido:
            print("✅ Healthcheck path correcto")
        else:
            print("❌ Healthcheck path incorrecto")
            return False
    
    # 2. Agregar archivo al staging
    print("📋 Paso 2: Agregando archivo...")
    exito, salida, error = ejecutar_sin_pager("git add railway.json")
    if exito:
        print("✅ Archivo agregado")
    else:
        print(f"❌ Error: {error}")
        return False
    
    # 3. Crear commit
    print("📋 Paso 3: Creando commit...")
    exito, salida, error = ejecutar_sin_pager('git commit -m "FIX: Corregir healthcheck para Railway"')
    if exito:
        print("✅ Commit creado")
        print(f"📄 Salida: {salida}")
    else:
        print(f"❌ Error en commit: {error}")
        return False
    
    # 4. Hacer push
    print("📋 Paso 4: Haciendo push...")
    exito, salida, error = ejecutar_sin_pager("git push origin main")
    if exito:
        print("✅ Push exitoso")
        print(f"📄 Salida: {salida}")
    else:
        print(f"❌ Error en push: {error}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ERROR CORREGIDO")
    print("=" * 50)
    print("✅ Healthcheck path corregido")
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
    print("🔄 Iniciando corrección de logs...")
    print("📅 Fecha:", time.strftime('%d/%m/%Y %H:%M:%S'))
    print("-" * 50)
    
    if corregir_logs():
        print("\n✅ Corrección completada exitosamente")
        print("🚀 El sistema de vouchers estará disponible pronto")
    else:
        print("\n❌ Error en la corrección")
        sys.exit(1)
