#!/usr/bin/env python3
"""
Script para deploy final con correcciones del healthcheck
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

def deploy_final():
    """Deploy final con correcciones"""
    
    print("🚀 DEPLOY FINAL - SISTEMA DE VOUCHERS")
    print("=" * 50)
    
    # 1. Verificar cambios
    print("📋 Paso 1: Verificando cambios...")
    with open('railway.json', 'r') as f:
        contenido = f.read()
        if '/ping' in contenido:
            print("✅ Healthcheck configurado para /ping")
        else:
            print("❌ Healthcheck no configurado")
            return False
    
    with open('app.py', 'r') as f:
        contenido = f.read()
        if '@app.route(\'/ping\')' in contenido:
            print("✅ Ruta /ping agregada")
        else:
            print("❌ Ruta /ping no encontrada")
            return False
    
    # 2. Agregar archivos
    print("📋 Paso 2: Agregando archivos...")
    exito, salida, error = ejecutar_sin_pager("git add railway.json app.py")
    if exito:
        print("✅ Archivos agregados")
    else:
        print(f"❌ Error: {error}")
        return False
    
    # 3. Crear commit
    print("📋 Paso 3: Creando commit...")
    exito, salida, error = ejecutar_sin_pager('git commit -m "FIX: Agregar ruta /ping y corregir healthcheck"')
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
    print("🎉 DEPLOY FINAL COMPLETADO")
    print("=" * 50)
    print("✅ Ruta /ping agregada")
    print("✅ Healthcheck configurado")
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
    print("🔄 Iniciando deploy final...")
    print("📅 Fecha:", time.strftime('%d/%m/%Y %H:%M:%S'))
    print("-" * 50)
    
    if deploy_final():
        print("\n✅ Deploy final completado exitosamente")
        print("🚀 El sistema de vouchers estará disponible pronto")
    else:
        print("\n❌ Error en el deploy")
        sys.exit(1)
