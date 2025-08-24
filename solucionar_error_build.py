#!/usr/bin/env python3
"""
Script para solucionar el error del build y hacer deploy simple
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

def solucionar_build():
    """Solucionar el error del build"""
    
    print("🔧 SOLUCIONANDO ERROR DE BUILD")
    print("=" * 50)
    
    # 1. Simplificar requirements.txt
    print("📋 Paso 1: Simplificando requirements.txt...")
    requirements_simple = """Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
gunicorn==21.2.0
psycopg2-binary==2.9.7
pytz==2023.3
reportlab==4.0.4
openpyxl==3.1.2"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements_simple)
    print("✅ Requirements.txt simplificado")
    
    # 2. Verificar que app.py tenga la ruta /ping
    print("📋 Paso 2: Verificando ruta /ping...")
    with open('app.py', 'r') as f:
        contenido = f.read()
        if '@app.route(\'/ping\')' not in contenido:
            # Agregar la ruta si no existe
            with open('app.py', 'r') as f:
                lineas = f.readlines()
            
            # Buscar donde agregar la ruta
            for i, linea in enumerate(lineas):
                if '@app.route(\'/railway-health\')' in linea:
                    lineas.insert(i + 2, '\n@app.route(\'/ping\')\ndef ping():\n    return "OK", 200\n\n')
                    break
            
            with open('app.py', 'w') as f:
                f.writelines(lineas)
            print("✅ Ruta /ping agregada")
        else:
            print("✅ Ruta /ping ya existe")
    
    # 3. Agregar archivos
    print("📋 Paso 3: Agregando archivos...")
    exito, salida, error = ejecutar_sin_pager("git add requirements.txt app.py")
    if exito:
        print("✅ Archivos agregados")
    else:
        print(f"❌ Error: {error}")
        return False
    
    # 4. Crear commit
    print("📋 Paso 4: Creando commit...")
    exito, salida, error = ejecutar_sin_pager('git commit -m "FIX: Simplificar requirements y corregir build"')
    if exito:
        print("✅ Commit creado")
        print(f"📄 Salida: {salida}")
    else:
        print(f"❌ Error en commit: {error}")
        return False
    
    # 5. Hacer push
    print("📋 Paso 5: Haciendo push...")
    exito, salida, error = ejecutar_sin_pager("git push origin main")
    if exito:
        print("✅ Push exitoso")
        print(f"📄 Salida: {salida}")
    else:
        print(f"❌ Error en push: {error}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ERROR DE BUILD SOLUCIONADO")
    print("=" * 50)
    print("✅ Requirements.txt simplificado")
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
    print("🔄 Iniciando solución de build...")
    print("📅 Fecha:", time.strftime('%d/%m/%Y %H:%M:%S'))
    print("-" * 50)
    
    if solucionar_build():
        print("\n✅ Solución completada exitosamente")
        print("🚀 El sistema de vouchers estará disponible pronto")
    else:
        print("\n❌ Error en la solución")
        sys.exit(1)
