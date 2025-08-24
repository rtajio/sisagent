import subprocess
import os

print("🚀 PUSH FINAL - SISTEMA DE VOUCHERS")
print("=" * 40)

# Configurar variables de entorno
os.environ['GIT_PAGER'] = ''
os.environ['PAGER'] = ''

try:
    # Hacer push forzado
    print("📤 Enviando cambios a GitHub...")
    resultado = subprocess.run(
        "git push origin main --force", 
        shell=True, 
        capture_output=True, 
        text=True,
        timeout=60
    )
    
    if resultado.returncode == 0:
        print("✅ ¡PUSH EXITOSO!")
        print("🚀 Railway detectará los cambios")
        print("⏱️ Deploy iniciado automáticamente")
        print("📱 La app se actualizará en 2-3 minutos")
    else:
        print("❌ Error en push:")
        print(resultado.stderr)
        
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 40)
