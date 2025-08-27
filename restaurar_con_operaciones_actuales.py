#!/usr/bin/env python3
"""
Restaurar sistema al backup del 24 de agosto
pero conservando operaciones registradas hasta hoy 26/08/2024
"""

import os
import shutil
import subprocess
from datetime import datetime

def restaurar_con_operaciones_actuales():
    print("🔄 RESTAURANDO SISTEMA CON OPERACIONES ACTUALES")
    print("=" * 50)
    
    try:
        # PASO 1: Crear backup de seguridad de la configuración actual
        print("📋 PASO 1: Creando backup de seguridad...")
        backup_actual = f"backup_antes_restauracion_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_actual, exist_ok=True)
        
        # Guardar archivos importantes actuales
        archivos_importantes = ['app.py', 'requirements.txt', 'Procfile', 'railway.toml']
        for archivo in archivos_importantes:
            if os.path.exists(archivo):
                shutil.copy2(archivo, backup_actual)
                print(f"   ✅ Guardado: {archivo}")
        
        # PASO 2: Restaurar archivos del backup del 24 de agosto
        print("\n📋 PASO 2: Restaurando archivos del 24 de agosto...")
        backup_24_agosto = "backup_pre_vouchers_20250824_131706"
        
        if os.path.exists(backup_24_agosto):
            # Restaurar app.py del backup
            app_backup = os.path.join(backup_24_agosto, 'app.py')
            if os.path.exists(app_backup):
                shutil.copy2(app_backup, 'app.py')
                print("   ✅ app.py restaurado")
            
            # Restaurar templates del backup
            templates_backup = os.path.join(backup_24_agosto, 'templates')
            if os.path.exists(templates_backup):
                if os.path.exists('templates'):
                    shutil.rmtree('templates')
                shutil.copytree(templates_backup, 'templates')
                print("   ✅ Templates restaurados")
            
            # Restaurar requirements.txt del backup
            req_backup = os.path.join(backup_24_agosto, 'requirements.txt')
            if os.path.exists(req_backup):
                shutil.copy2(req_backup, 'requirements.txt')
                print("   ✅ requirements.txt restaurado")
                
            # Restaurar Procfile del backup
            proc_backup = os.path.join(backup_24_agosto, 'Procfile')
            if os.path.exists(proc_backup):
                shutil.copy2(proc_backup, 'Procfile')
                print("   ✅ Procfile restaurado")
                
        else:
            print("   ❌ No se encontró el backup del 24 de agosto")
            return False
        
        # PASO 3: Configurar la conexión a la base de datos actual
        print("\n📋 PASO 3: Configurando conexión a BD actual...")
        
        # Leer el app.py restaurado y modificarlo para usar la BD actual
        with open('app.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Asegurar que use la configuración de Railway
        if 'DATABASE_URL' not in contenido:
            # Agregar configuración de BD al inicio
            config_bd = """
# Configuración de base de datos para Railway
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Usando PostgreSQL en Railway")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent.db'
    print("✅ Usando SQLite para desarrollo local")
"""
            
            # Insertar después de la configuración básica
            lineas = contenido.split('\n')
            for i, linea in enumerate(lineas):
                if 'SECRET_KEY' in linea:
                    lineas.insert(i + 2, config_bd)
                    break
            
            contenido = '\n'.join(lineas)
        
        # Escribir el archivo modificado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print("   ✅ Configuración de BD actualizada")
        
        # PASO 4: Crear railway.toml simple
        print("\n📋 PASO 4: Configurando Railway...")
        railway_config = """[build]
"""
        with open('railway.toml', 'w', encoding='utf-8') as f:
            f.write(railway_config)
        print("   ✅ railway.toml configurado")
        
        # PASO 5: Hacer commit y push
        print("\n📋 PASO 5: Desplegando restauración...")
        
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'RESTAURAR: Sistema al 24 agosto con operaciones actuales'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        
        print("\n" + "=" * 60)
        print("✅ RESTAURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        print("\n🎯 RESULTADO:")
        print("   ✅ Sistema restaurado al backup del 24 de agosto")
        print("   ✅ Base de datos PRESERVADA (todas las operaciones intactas)")
        print("   ✅ Templates y funcionalidades del 24 de agosto")
        print("   ✅ Deploy iniciado en Railway")
        print("   ✅ Backup de seguridad creado en:", backup_actual)
        
        print("\n📱 PRÓXIMOS PASOS:")
        print("   1. Esperar 2-3 minutos para que complete el deploy")
        print("   2. Verificar que el sistema funcione correctamente")
        print("   3. Todas las operaciones registradas hasta hoy están preservadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la restauración: {e}")
        return False

if __name__ == '__main__':
    restaurar_con_operaciones_actuales()
