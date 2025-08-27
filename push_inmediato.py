#!/usr/bin/env python3
"""
Push inmediato para deploy
"""

import os
import subprocess

def push_inmediato():
    print("🚀 PUSH INMEDIATO PARA DEPLOY")
    print("=" * 40)
    
    try:
        print("📋 PASO 1: Verificando estado git...")
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        print(result.stdout)
        
        print("\n📋 PASO 2: Agregando cambios...")
        result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
        print("✅ Cambios agregados")
        
        print("\n📋 PASO 3: Haciendo commit...")
        result = subprocess.run(['git', 'commit', '-m', 'FIX: Template dashboard corregido'], capture_output=True, text=True)
        print(result.stdout)
        
        print("\n📋 PASO 4: Haciendo push...")
        result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ PUSH EXITOSO - DEPLOY INICIADO")
            print("=" * 50)
            print("\n🎯 RESULTADO:")
            print("   ✅ Cambios subidos a GitHub")
            print("   ✅ Railway detectará los cambios")
            print("   ✅ Deploy automático iniciado")
            return True
        else:
            print(f"❌ Error en push: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    push_inmediato()
