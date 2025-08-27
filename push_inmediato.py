#!/usr/bin/env python3
import subprocess
import os

print("🚀 PUSH INMEDIATO")
print("=" * 20)

# Configurar para no usar pager
os.environ['GIT_PAGER'] = 'cat'

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "FIX: Columna password - BD compatible"], check=True)
    subprocess.run(["git", "push", "origin", "main"], check=True)
    print("✅ PUSH EXITOSO")
    print("🎯 Railway detectará cambios en 1 minuto")
except Exception as e:
    print(f"❌ Error: {e}")
