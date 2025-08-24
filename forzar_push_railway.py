#!/usr/bin/env python3
"""
Script para forzar el push a GitHub y activar el deploy en Railway
"""

import subprocess
import sys
import time

def ejecutar_comando(comando):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"🔄 Ejecutando: {comando}")
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if resultado.returncode == 0:
            print(f"✅ Comando exitoso: {comando}")
            if resultado.stdout:
                print(f"📄 Salida: {resultado.stdout}")
        else:
            print(f"❌ Error en comando: {comando}")
            if resultado.stderr:
                print(f"📄 Error: {resultado.stderr}")
        return resultado.returncode == 0
    except Exception as e:
        print(f"❌ Excepción en comando {comando}: {e}")
        return False

def forzar_push_railway():
    """Forzar el push a GitHub para activar Railway"""
    
    print("🚀 Iniciando proceso de push forzado a Railway")
    print("=" * 60)
    
    # 1. Verificar estado actual
    print("📋 Paso 1: Verificando estado actual...")
    if not ejecutar_comando("git status"):
        print("❌ Error al verificar estado de Git")
        return False
    
    # 2. Verificar remotes
    print("\n📋 Paso 2: Verificando remotes...")
    if not ejecutar_comando("git remote -v"):
        print("❌ Error al verificar remotes")
        return False
    
    # 3. Verificar commits pendientes
    print("\n📋 Paso 3: Verificando commits pendientes...")
    if not ejecutar_comando("git log --oneline -3"):
        print("❌ Error al verificar commits")
        return False
    
    # 4. Forzar push
    print("\n📋 Paso 4: Forzando push a GitHub...")
    if not ejecutar_comando("git push origin main --force"):
        print("❌ Error al hacer push forzado")
        return False
    
    # 5. Verificar push exitoso
    print("\n📋 Paso 5: Verificando push exitoso...")
    if not ejecutar_comando("git log --oneline -3"):
        print("❌ Error al verificar commits después del push")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 PUSH FORZADO COMPLETADO")
    print("=" * 60)
    print("✅ Los cambios han sido subidos a GitHub")
    print("🚀 Railway detectará los cambios automáticamente")
    print("⏱️ El deploy comenzará en unos minutos")
    print("\n📋 Próximos pasos:")
    print("   1. Esperar 2-3 minutos para que Railway detecte cambios")
    print("   2. Verificar el dashboard de Railway")
    print("   3. Probar el sistema de vouchers en producción")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    print("🔄 Iniciando script de push forzado...")
    print("📅 Fecha:", time.strftime('%d/%m/%Y %H:%M:%S'))
    print("-" * 60)
    
    if forzar_push_railway():
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ Error en el proceso")
        sys.exit(1)
