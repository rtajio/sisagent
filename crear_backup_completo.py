#!/usr/bin/env python3
"""
Script para crear backup completo del sistema SISAGENT
Incluye código fuente, base de datos, templates y configuraciones
"""

import os
import shutil
import json
import zipfile
from datetime import datetime
from pathlib import Path

def crear_backup_completo():
    """Crear backup completo del sistema y datos"""
    
    print("=" * 70)
    print("CREANDO BACKUP COMPLETO DEL SISTEMA SISAGENT")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Configuración
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_completo_{timestamp}"
    backup_dir = "backups"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Crear directorio de respaldos si no existe
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Crear directorio del respaldo
    os.makedirs(backup_path, exist_ok=True)
    
    # Lista de archivos importantes a respaldar
    archivos_importantes = [
        "app.py",
        "requirements.txt",
        "Procfile",
        "Procfile_optimizado",
        "railway.toml",
        "railway_optimized.toml",
        "config.env",
        "config.py",
        "README.md",
        "README_OPTIMIZED.md",
        ".gitignore" if os.path.exists(".gitignore") else None,
    ]
    
    # Lista de directorios importantes
    directorios_importantes = [
        "templates",
        "static" if os.path.exists("static") else None,
        "logs" if os.path.exists("logs") else None,
    ]
    
    # Archivos de base de datos
    archivos_db = [
        "sisagent_consolidada.db",
        "sisagent.db",
    ]
    
    archivos_respaldados = []
    directorios_respaldados = []
    bases_datos_respaldadas = []
    
    print("Respaldando archivos del sistema...")
    print("-" * 70)
    
    # Respaldar archivos individuales
    for archivo in archivos_importantes:
        if archivo and os.path.exists(archivo):
            try:
                shutil.copy2(archivo, backup_path)
                archivos_respaldados.append(archivo)
                tamaño = os.path.getsize(archivo) / 1024  # KB
                print(f"[OK] {archivo} ({tamaño:.2f} KB)")
            except Exception as e:
                print(f"[ERROR] Error al respaldar {archivo}: {e}")
    
    print()
    print("Respaldando directorios...")
    print("-" * 70)
    
    # Respaldar directorios
    for directorio in directorios_importantes:
        if directorio and os.path.exists(directorio):
            try:
                dir_backup_path = os.path.join(backup_path, directorio)
                shutil.copytree(directorio, dir_backup_path, dirs_exist_ok=True)
                directorios_respaldados.append(directorio)
                
                # Calcular tamaño del directorio
                tamaño_total = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(directorio)
                    for filename in filenames
                ) / 1024  # KB
                
                print(f"[OK] {directorio}/ ({tamaño_total:.2f} KB)")
            except Exception as e:
                print(f"[ERROR] Error al respaldar {directorio}: {e}")
    
    print()
    print("Respaldando bases de datos...")
    print("-" * 70)
    
    # Respaldar bases de datos
    for db_file in archivos_db:
        if os.path.exists(db_file):
            try:
                db_backup_path = os.path.join(backup_path, db_file)
                shutil.copy2(db_file, db_backup_path)
                bases_datos_respaldadas.append(db_file)
                tamaño = os.path.getsize(db_file) / (1024 * 1024)  # MB
                print(f"[OK] {db_file} ({tamaño:.2f} MB)")
            except Exception as e:
                print(f"[ERROR] Error al respaldar {db_file}: {e}")
    
    if not bases_datos_respaldadas:
        print("[ADVERTENCIA] No se encontraron bases de datos para respaldar")
    
    print()
    print("Creando archivo de informacion del backup...")
    
    # Crear archivo de información del respaldo
    backup_info = {
        "backup_name": backup_name,
        "timestamp": timestamp,
        "fecha_creacion": datetime.now().isoformat(),
        "fecha_legible": datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        "descripcion": "Backup completo del sistema SISAGENT - Código fuente, datos y configuraciones",
        "archivos_respaldados": archivos_respaldados,
        "directorios_respaldados": directorios_respaldados,
        "bases_datos_respaldadas": bases_datos_respaldadas,
        "total_archivos": len(archivos_respaldados),
        "total_directorios": len(directorios_respaldados),
        "total_bases_datos": len(bases_datos_respaldadas),
        "sistema": {
            "nombre": "SISAGENT",
            "version": "Ultra Optimizada",
            "tipo": "Sistema de Gestión de Operaciones Bancarias"
        }
    }
    
    info_file = os.path.join(backup_path, "backup_info.json")
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Información guardada en: backup_info.json")
    
    # Crear archivo ZIP del backup
    print()
    print("📦 Creando archivo ZIP del backup...")
    print("-" * 70)
    
    zip_filename = f"{backup_name}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar todos los archivos del directorio de backup
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
                    print(f"✅ Agregado al ZIP: {arcname}")
        
        zip_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
        print(f"✅ Archivo ZIP creado: {zip_filename} ({zip_size:.2f} MB)")
        
    except Exception as e:
        print(f"⚠️  Error al crear ZIP: {e}")
        zip_path = None
    
    # Resumen final
    print()
    print("=" * 70)
    print("🎉 BACKUP COMPLETO CREADO EXITOSAMENTE")
    print("=" * 70)
    print(f"📁 Nombre del backup: {backup_name}")
    print(f"📂 Ubicación del directorio: {backup_path}")
    if zip_path:
        print(f"📦 Archivo ZIP: {zip_path}")
    print()
    print("📊 Resumen:")
    print(f"   • Archivos respaldados: {len(archivos_respaldados)}")
    print(f"   • Directorios respaldados: {len(directorios_respaldados)}")
    print(f"   • Bases de datos respaldadas: {len(bases_datos_respaldadas)}")
    print()
    print("📋 Contenido del backup:")
    print("   ✅ Código fuente completo (app.py)")
    print("   ✅ Dependencias (requirements.txt)")
    print("   ✅ Configuraciones (Procfile, railway.toml, config.env)")
    print("   ✅ Templates HTML")
    print("   ✅ Base de datos con todos los datos")
    print("   ✅ Documentación")
    print()
    print("💡 Para restaurar este backup:")
    print("   1. Descomprime el archivo ZIP o usa el directorio del backup")
    print("   2. Restaura los archivos en el sistema")
    print("   3. Restaura la base de datos")
    print("=" * 70)
    
    return backup_name, backup_path, zip_path

if __name__ == "__main__":
    try:
        backup_name, backup_path, zip_path = crear_backup_completo()
        print(f"\n✅ Backup completado: {backup_name}")
    except Exception as e:
        print(f"\n❌ Error al crear backup: {e}")
        import traceback
        traceback.print_exc()

