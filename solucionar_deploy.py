#!/usr/bin/env python3
"""
Script para solucionar el problema del healthcheck y hacer deploy automático
"""

import subprocess
import os
import sys
import time

def ejecutar_comando(comando):
    """Ejecutar comando sin pager"""
    env = os.environ.copy()
    env['GIT_PAGER'] = ''
    env['PAGER'] = ''
    
    try:
        resultado = subprocess.run(comando, shell=True, env=env, capture_output=True, text=True, timeout=30)
        return resultado.returncode == 0, resultado.stdout, resultado.stderr
    except Exception as e:
        return False, "", str(e)

def solucionar_deploy():
    """Solucionar el problema del healthcheck y hacer deploy"""
    
    print("🔧 SOLUCIONANDO PROBLEMA DE DEPLOY")
    print("=" * 50)
    
    # 1. Verificar que railway.json esté corregido
    print("📋 Paso 1: Verificando configuración de Railway...")
    with open('railway.json', 'r') as f:
        contenido = f.read()
        if '/railway-health' in contenido:
            print("✅ Configuración de healthcheck correcta")
        else:
            print("❌ Configuración incorrecta")
            return False
    
    # 2. Agregar archivos al staging
    print("📋 Paso 2: Preparando commit...")
    exito, salida, error = ejecutar_comando("git add railway.json")
    if exito:
        print("✅ Archivos agregados")
    else:
        print(f"❌ Error: {error}")
        return False
    
    # 3. Crear commit
    print("📋 Paso 3: Creando commit...")
    exito, salida, error = ejecutar_comando('git commit -m "FIX: Corregir healthcheck path para Railway"')
    if exito:
        print("✅ Commit creado")
    else:
        print(f"❌ Error: {error}")
        return False
    
    # 4. Hacer push
    print("📋 Paso 4: Haciendo push...")
    exito, salida, error = ejecutar_comando("git push origin main")
    if exito:
        print("✅ Push exitoso")
    else:
        print(f"❌ Error en push: {error}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 PROBLEMA SOLUCIONADO")
    print("=" * 50)
    print("✅ Healthcheck corregido")
    print("✅ Commit creado y subido")
    print("🚀 Railway detectará los cambios")
    print("⏱️ Deploy automático iniciado")
    print("\n📋 Próximos pasos:")
    print("   1. Espera 2-3 minutos")
    print("   2. Verifica Railway dashboard")
    print("   3. El healthcheck debería pasar ahora")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    print("🔄 Iniciando solución automática...")
    print("📅 Fecha:", time.strftime('%d/%m/%Y %H:%M:%S'))
    print("-" * 50)
    
    if solucionar_deploy():
        print("\n✅ Proceso completado exitosamente")
        print("🚀 El sistema de vouchers estará disponible pronto")
    else:
        print("\n❌ Error en el proceso")
        sys.exit(1)
