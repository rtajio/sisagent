import subprocess
import os

# Configurar Git para no usar pager
os.environ['GIT_PAGER'] = 'cat'

# Hacer push forzado
print("🚀 Haciendo push forzado...")
resultado = subprocess.run("git push origin main --force", shell=True, capture_output=True, text=True)

if resultado.returncode == 0:
    print("✅ Push exitoso!")
    print("🚀 Railway detectará los cambios automáticamente")
    print("⏱️ Deploy en progreso...")
else:
    print("❌ Error en push:")
    print(resultado.stderr)
