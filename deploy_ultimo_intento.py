#!/usr/bin/env python3
"""
Script para deploy final con configuración mínima
"""

import subprocess
import os
import sys
import time

def ejecutar_sin_pager(comando):
    """Ejecutar comando sin pager"""
    env = os.environ.copy()
    env['GIT_PAGER'] = ''
    env['PAGER'] = ''
    env['LESS'] = ''
    env['MORE'] = ''
    
    try:
        resultado = subprocess.run(comando, shell=True, env=env, capture_output=True, text=True, timeout=60)
        return resultado.returncode == 0, resultado.stdout, resultado.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def deploy_ultimo_intento():
    """Deploy final con configuración mínima"""
    
    print("🚀 DEPLOY ÚLTIMO INTENTO")
    print("=" * 50)
    
    # 1. Crear requirements.txt mínimo
    print("📋 Paso 1: Creando requirements mínimo...")
    requirements_minimo = """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
gunicorn==21.2.0
psycopg2-binary==2.9.7"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_minimo)
    print("✅ Requirements mínimo creado")
    
    # 2. Crear Procfile simple
    print("📋 Paso 2: Creando Procfile simple...")
    procfile_simple = """web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120"""
    
    with open('Procfile', 'w') as f:
        f.write(procfile_simple)
    print("✅ Procfile simple creado")
    
    # 3. Verificar ruta /ping
    print("📋 Paso 3: Verificando ruta /ping...")
    with open('app.py', 'r') as f:
        contenido = f.read()
        if '@app.route(\'/ping\')' not in contenido:
            # Agregar la ruta al final del archivo
            with open('app.py', 'a') as f:
                f.write('\n@app.route(\'/ping\')\ndef ping():\n    return "OK", 200\n')
            print("✅ Ruta /ping agregada")
        else:
            print("✅ Ruta /ping ya existe")
    
    # 4. Agregar archivos
    print("📋 Paso 4: Agregando archivos...")
    exito, salida, error = ejecutar_sin_pager("git add requirements.txt Procfile app.py")
    if exito:
        print("✅ Archivos agregados")
    else:
        print(f"❌ Error: {error}")
        return False
    
    # 5. Crear commit
    print("📋 Paso 5: Creando commit...")
    exito, salida, error = ejecutar_sin_pager('git commit -m "FIX: Configuración mínima para deploy"')
    if exito:
        print("✅ Commit creado")
        print(f"📄 Salida: {salida}")
    else:
        print(f"❌ Error en commit: {error}")
        return False
    
    # 6. Hacer push
    print("📋 Paso 6: Haciendo push...")
    exito, salida, error = ejecutar_sin_pager("git push origin main")
    if exito:
        print("✅ Push exitoso")
        print(f"📄 Salida: {salida}")
    else:
        print(f"❌ Error en push: {error}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 DEPLOY ÚLTIMO INTENTO COMPLETADO")
    print("=" * 50)
    print("✅ Requirements mínimo creado")
    print("✅ Procfile simple creado")
    print("✅ Ruta /ping verificada")
    print("✅ Commit creado exitosamente")
    print("✅ Push completado")
    print("🚀 Railway detectará cambios automáticamente")
    print("⏱️ Deploy iniciado")
    print("\n📋 Próximos pasos:")
    print("   1. Espera 2-3 minutos")
    print("   2. Verifica Railway dashboard")
    print("   3. El build debería completarse ahora")
    print("   4. Sistema de vouchers disponible")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    print("🔄 Iniciando deploy último intento...")
    print("📅 Fecha:", time.strftime('%d/%m/%Y %H:%M:%S'))
    print("-" * 50)
    
    if deploy_ultimo_intento():
        print("\n✅ Deploy último intento completado")
        print("🚀 El sistema de vouchers estará disponible pronto")
    else:
        print("\n❌ Error en el deploy")
        sys.exit(1)
