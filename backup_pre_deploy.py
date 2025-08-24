#!/usr/bin/env python3
"""
Script de Backup Completo del Sistema SISAGENT
Antes del deploy del sistema de vouchers
"""

import os
import shutil
import sqlite3
import json
from datetime import datetime
import zipfile
import sys

def crear_backup():
    """Crear backup completo del sistema"""
    
    # Crear directorio de backup con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_pre_vouchers_{timestamp}"
    
    print(f"🔄 Creando backup: {backup_dir}")
    
    try:
        # Crear directorio de backup
        os.makedirs(backup_dir, exist_ok=True)
        
        # 1. Backup de la base de datos
        print("📊 Haciendo backup de la base de datos...")
        if os.path.exists('sisagent.db'):
            shutil.copy2('sisagent.db', f"{backup_dir}/sisagent.db")
            print("✅ Base de datos respaldada")
        else:
            print("⚠️ No se encontró sisagent.db")
        
        # 2. Backup de archivos principales
        print("📁 Haciendo backup de archivos principales...")
        archivos_principales = [
            'app.py',
            'config.py',
            'requirements.txt',
            'Procfile',
            'runtime.txt',
            'railway.json',
            'railway.toml',
            'wsgi.py',
            'gunicorn.conf.py'
        ]
        
        for archivo in archivos_principales:
            if os.path.exists(archivo):
                shutil.copy2(archivo, f"{backup_dir}/{archivo}")
                print(f"✅ {archivo} respaldado")
            else:
                print(f"⚠️ No se encontró {archivo}")
        
        # 3. Backup de templates
        print("🎨 Haciendo backup de templates...")
        if os.path.exists('templates'):
            shutil.copytree('templates', f"{backup_dir}/templates")
            print("✅ Templates respaldados")
        else:
            print("⚠️ No se encontró directorio templates")
        
        # 4. Backup de archivos de configuración
        print("⚙️ Haciendo backup de configuraciones...")
        archivos_config = [
            '.env',
            '.gitignore',
            'README.md',
            'README_OPTIMIZED.md'
        ]
        
        for archivo in archivos_config:
            if os.path.exists(archivo):
                shutil.copy2(archivo, f"{backup_dir}/{archivo}")
                print(f"✅ {archivo} respaldado")
            else:
                print(f"⚠️ No se encontró {archivo}")
        
        # 5. Backup de directorio instance (si existe)
        if os.path.exists('instance'):
            print("🗂️ Haciendo backup de directorio instance...")
            shutil.copytree('instance', f"{backup_dir}/instance")
            print("✅ Directorio instance respaldado")
        
        # 6. Backup de logs (si existe)
        if os.path.exists('logs'):
            print("📝 Haciendo backup de logs...")
            shutil.copytree('logs', f"{backup_dir}/logs")
            print("✅ Logs respaldados")
        
        # 7. Crear archivo de información del backup
        print("📋 Creando archivo de información...")
        info_backup = {
            "fecha_backup": datetime.now().isoformat(),
            "version": "Pre-deploy Vouchers",
            "descripcion": "Backup completo antes de implementar sistema de vouchers",
            "archivos_incluidos": [
                "Base de datos SQLite",
                "Archivos principales de la aplicación",
                "Templates completos",
                "Archivos de configuración",
                "Directorio instance",
                "Logs del sistema"
            ],
            "cambios_implementados": [
                "Sistema de vouchers para ticketeras térmicas",
                "Plantillas 58mm y 80mm",
                "Rutas para generar e imprimir vouchers",
                "Selección de tamaño de voucher",
                "Integración con sistema de operaciones"
            ]
        }
        
        with open(f"{backup_dir}/backup_info.json", 'w', encoding='utf-8') as f:
            json.dump(info_backup, f, indent=2, ensure_ascii=False)
        
        # 8. Crear archivo README del backup
        readme_content = f"""# Backup Pre-Deploy Vouchers - {timestamp}

## 📋 Información del Backup

**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
**Versión:** Pre-deploy Sistema de Vouchers
**Descripción:** Backup completo del sistema antes de implementar el sistema de vouchers

## 📁 Contenido del Backup

- ✅ **Base de datos:** sisagent.db
- ✅ **Archivos principales:** app.py, config.py, requirements.txt, etc.
- ✅ **Templates:** Directorio completo de templates
- ✅ **Configuraciones:** .env, .gitignore, README files
- ✅ **Instance:** Directorio de configuración local
- ✅ **Logs:** Historial de logs del sistema

## 🔄 Cómo Restaurar

1. **Detener el servidor actual**
2. **Restaurar la base de datos:**
   ```bash
   cp sisagent.db.backup sisagent.db
   ```
3. **Restaurar archivos principales:**
   ```bash
   cp app.py.backup app.py
   cp config.py.backup config.py
   # ... otros archivos
   ```
4. **Restaurar templates:**
   ```bash
   rm -rf templates
   cp -r templates.backup templates
   ```
5. **Reiniciar el servidor**

## ⚠️ Notas Importantes

- Este backup fue creado ANTES de implementar el sistema de vouchers
- Si algo sale mal, puedes restaurar completamente el sistema
- Los nuevos archivos de vouchers NO están incluidos en este backup

## 🎯 Cambios Implementados

- Sistema de vouchers para ticketeras térmicas
- Plantillas 58mm y 80mm
- Rutas para generar e imprimir vouchers
- Selección de tamaño de voucher
- Integración con sistema de operaciones

---
**Backup creado automáticamente por el sistema SISAGENT**
"""
        
        with open(f"{backup_dir}/README_BACKUP.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # 9. Crear archivo ZIP del backup
        print("📦 Creando archivo ZIP del backup...")
        zip_filename = f"{backup_dir}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Archivo ZIP creado: {zip_filename}")
        
        # 10. Crear script de restauración
        print("🔄 Creando script de restauración...")
        script_restauracion = f"""#!/usr/bin/env python3
\"\"\"
Script de Restauración del Backup Pre-Deploy Vouchers
\"\"\"

import os
import shutil
import sys
from datetime import datetime

def restaurar_backup():
    \"\"\"Restaurar el sistema desde el backup\"\"\"
    
    print("🔄 Iniciando restauración del sistema...")
    
    # Verificar que existe el backup
    backup_dir = "{backup_dir}"
    if not os.path.exists(backup_dir):
        print("❌ No se encontró el directorio de backup")
        return False
    
    try:
        # 1. Restaurar base de datos
        if os.path.exists(f"{backup_dir}/sisagent.db"):
            shutil.copy2(f"{backup_dir}/sisagent.db", "sisagent.db")
            print("✅ Base de datos restaurada")
        
        # 2. Restaurar archivos principales
        archivos_principales = [
            'app.py', 'config.py', 'requirements.txt', 'Procfile',
            'runtime.txt', 'railway.json', 'railway.toml', 'wsgi.py',
            'gunicorn.conf.py'
        ]
        
        for archivo in archivos_principales:
            if os.path.exists(f"{backup_dir}/{archivo}"):
                shutil.copy2(f"{backup_dir}/{archivo}", archivo)
                print(f"✅ {{archivo}} restaurado")
        
        # 3. Restaurar templates
        if os.path.exists(f"{backup_dir}/templates"):
            if os.path.exists("templates"):
                shutil.rmtree("templates")
            shutil.copytree(f"{backup_dir}/templates", "templates")
            print("✅ Templates restaurados")
        
        # 4. Restaurar archivos de configuración
        archivos_config = ['.env', '.gitignore', 'README.md', 'README_OPTIMIZED.md']
        for archivo in archivos_config:
            if os.path.exists(f"{backup_dir}/{archivo}"):
                shutil.copy2(f"{backup_dir}/{archivo}", archivo)
                print(f"✅ {{archivo}} restaurado")
        
        # 5. Restaurar instance
        if os.path.exists(f"{backup_dir}/instance"):
            if os.path.exists("instance"):
                shutil.rmtree("instance")
            shutil.copytree(f"{backup_dir}/instance", "instance")
            print("✅ Directorio instance restaurado")
        
        # 6. Restaurar logs
        if os.path.exists(f"{backup_dir}/logs"):
            if os.path.exists("logs"):
                shutil.rmtree("logs")
            shutil.copytree(f"{backup_dir}/logs", "logs")
            print("✅ Logs restaurados")
        
        print("✅ Restauración completada exitosamente")
        print("🔄 El sistema ha sido restaurado al estado anterior al deploy de vouchers")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la restauración: {{e}}")
        return False

if __name__ == '__main__':
    restaurar_backup()
"""
        
        with open(f"restaurar_backup_{timestamp}.py", 'w', encoding='utf-8') as f:
            f.write(script_restauracion)
        
        print(f"✅ Script de restauración creado: restaurar_backup_{timestamp}.py")
        
        # 11. Mostrar resumen
        print("\n" + "="*60)
        print("🎉 BACKUP COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"📁 Directorio de backup: {backup_dir}")
        print(f"📦 Archivo ZIP: {zip_filename}")
        print(f"🔄 Script de restauración: restaurar_backup_{timestamp}.py")
        print("\n📋 Archivos incluidos:")
        print("   ✅ Base de datos SQLite")
        print("   ✅ Archivos principales de la aplicación")
        print("   ✅ Templates completos")
        print("   ✅ Archivos de configuración")
        print("   ✅ Directorio instance")
        print("   ✅ Logs del sistema")
        print("\n⚠️ IMPORTANTE:")
        print("   - Guarda estos archivos en un lugar seguro")
        print("   - Si algo sale mal, usa el script de restauración")
        print("   - El backup NO incluye los nuevos archivos de vouchers")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante el backup: {e}")
        return False

if __name__ == '__main__':
    print("🔄 Iniciando backup completo del sistema...")
    print("📅 Fecha:", datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print("🎯 Objetivo: Backup antes del deploy del sistema de vouchers")
    print("-" * 60)
    
    if crear_backup():
        print("\n✅ Backup completado. Puedes proceder con el deploy.")
    else:
        print("\n❌ Error en el backup. Revisa los errores antes de continuar.")
        sys.exit(1)
