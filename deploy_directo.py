import subprocess
import os
import sys

def ejecutar_sin_pager(comando):
    """Ejecutar comando sin pager"""
    env = os.environ.copy()
    env['GIT_PAGER'] = ''
    env['PAGER'] = ''
    
    try:
        resultado = subprocess.run(comando, shell=True, env=env, capture_output=True, text=True, timeout=30)
        return resultado.returncode == 0, resultado.stdout, resultado.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

print("🚀 DEPLOY DIRECTO - SISTEMA DE VOUCHERS")
print("=" * 50)

# 1. Verificar estado
print("📋 Verificando estado...")
exito, salida, error = ejecutar_sin_pager("git status")
if exito:
    print("✅ Estado OK")
else:
    print(f"❌ Error: {error}")

# 2. Hacer push forzado
print("🚀 Haciendo push forzado...")
exito, salida, error = ejecutar_sin_pager("git push origin main --force")
if exito:
    print("✅ Push exitoso!")
    print("🚀 Railway detectará cambios automáticamente")
    print("⏱️ Deploy en progreso...")
else:
    print(f"❌ Error en push: {error}")

print("=" * 50)
print("🎯 RESULTADO:")
if exito:
    print("✅ DEPLOY INICIADO")
    print("📱 Railway actualizará la app automáticamente")
    print("⏰ Espera 2-3 minutos para que esté disponible")
else:
    print("❌ ERROR EN DEPLOY")
    print("🔧 Revisa los errores arriba")
