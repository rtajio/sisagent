#!/usr/bin/env python3
"""
Forzar deploy en Railway
"""

import os
import subprocess
import time

def forzar_deploy():
    print("🚀 FORZANDO DEPLOY EN RAILWAY")
    print("=" * 60)
    
    try:
        # Cambiar al directorio correcto
        os.chdir(r'C:\Users\LENOVO\sisagent')
        print(f"📁 Directorio: {os.getcwd()}")
        
        # Verificar estado actual
        print("\n📋 Verificando estado actual...")
        resultado = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
        print(resultado.stdout)
        
        # Agregar un archivo temporal para forzar cambios
        with open('deploy_trigger.txt', 'w', encoding='utf-8') as f:
            f.write(f"Deploy trigger: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("Cambios: Agregar ruta API /api/operaciones/<id> PUT\n")
        print("✅ Archivo trigger creado")
        
        print("\n📋 PASO 1: Agregando todos los cambios...")
        resultado = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        if resultado.returncode == 0:
            print("✅ Cambios agregados")
        else:
            print(f"⚠️  Advertencia: {resultado.stderr}")
        
        print("\n📋 PASO 2: Haciendo commit...")
        resultado = subprocess.run(
            ['git', 'commit', '-m', 'FIX: agregar ruta API /api/operaciones/<id> PUT para edición de operaciones'],
            capture_output=True,
            text=True
        )
        if resultado.returncode == 0:
            print("✅ Commit realizado")
            print(resultado.stdout)
        else:
            print(f"⚠️  No hay cambios para commitear o ya están commiteados: {resultado.stderr}")
        
        print("\n📋 PASO 3: Haciendo push a GitHub...")
        resultado = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        if resultado.returncode == 0:
            print("✅ Push completado exitosamente")
            print(resultado.stdout)
        else:
            print(f"❌ Error en push: {resultado.stderr}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ DEPLOY INICIADO")
        print("=" * 60)
        print("\n🎯 RESULTADO:")
        print("   ✅ Cambios subidos a GitHub")
        print("   ✅ Railway detectará los cambios automáticamente")
        print("   ✅ Deploy automático debería iniciarse en Railway")
        print("   ⏱️  Verifica el dashboard de Railway en 1-2 minutos")
        print("\n📊 Verifica en Railway:")
        print("   1. Ve al dashboard de Railway")
        print("   2. Revisa la pestaña 'Deployments'")
        print("   3. Deberías ver un nuevo deploy iniciándose")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    forzar_deploy()
