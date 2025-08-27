#!/usr/bin/env python3
"""
Deploy inmediato a Railway
"""

import os
import subprocess

def deploy_ahora():
    print("🚀 DEPLOY INMEDIATO A RAILWAY")
    print("=" * 40)
    
    try:
        # Agregar todos los cambios
        print("📋 Agregando cambios...")
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Cambios agregados")
        
        # Hacer commit
        print("📋 Haciendo commit...")
        subprocess.run(['git', 'commit', '-m', 'FIX: Dashboard corregido'], check=True)
        print("✅ Commit realizado")
        
        # Hacer push
        print("📋 Haciendo push...")
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ Push completado")
        
        print("\n" + "=" * 50)
        print("✅ DEPLOY INICIADO")
        print("=" * 50)
        print("🚀 Railway detectará los cambios automáticamente")
        print("⏱️ La aplicación se actualizará en 2-3 minutos")
        print("📱 Puedes verificar el estado en Railway")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    deploy_ahora()
