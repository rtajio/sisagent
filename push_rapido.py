#!/usr/bin/env python3
import os
import subprocess

def push_rapido():
    print("🚀 PUSH RÁPIDO A RAILWAY")
    print("=" * 30)
    
    try:
        # Git add
        print("📦 Agregando archivos...")
        subprocess.run(["git", "add", "."], check=True)
        
        # Git commit
        print("💾 Haciendo commit...")
        subprocess.run(["git", "commit", "-m", "FIX: Internal Server Error solucionado"], check=True)
        
        # Git push
        print("🚀 Haciendo push a Railway...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("✅ PUSH COMPLETADO")
        print("🎯 Railway detectará los cambios en 1-2 minutos")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    push_rapido()
