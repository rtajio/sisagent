#!/usr/bin/env python3
"""
Forzar deploy en Railway
"""

import os
import subprocess
import time

def forzar_deploy():
    print("🚀 FORZANDO DEPLOY EN RAILWAY")
    print("=" * 40)
    
    try:
        # Agregar un archivo temporal para forzar cambios
        with open('deploy_trigger.txt', 'w') as f:
            f.write(f"Deploy trigger: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("📋 PASO 1: Agregando todos los cambios...")
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Cambios agregados")
        
        print("\n📋 PASO 2: Haciendo commit...")
        subprocess.run(['git', 'commit', '-m', 'FORZAR DEPLOY - Correcciones finales'], check=True)
        print("✅ Commit realizado")
        
        print("\n📋 PASO 3: Haciendo push forzado...")
        subprocess.run(['git', 'push', '-f', 'origin', 'main'], check=True)
        print("✅ Push forzado completado")
        
        print("\n" + "=" * 50)
        print("✅ DEPLOY FORZADO EXITOSO")
        print("=" * 50)
        print("\n🎯 RESULTADO:")
        print("   ✅ Cambios subidos a GitHub")
        print("   ✅ Railway detectará los cambios")
        print("   ✅ Deploy automático iniciado")
        print("   ⏱️  Deploy en progreso...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    forzar_deploy()
