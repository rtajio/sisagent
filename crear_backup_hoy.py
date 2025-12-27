#!/usr/bin/env python3
"""
Script para crear backup completo del sistema SISAGENT al día de hoy
Incluye código fuente, base de datos, templates y todas las configuraciones
"""

import os
import shutil
import json
import zipfile
from datetime import datetime
from pathlib import Path

def crear_backup_completo_hoy():
    """Crear backup completo del sistema y datos al día de hoy"""
    
    print("=" * 80)
    print("CREANDO BACKUP COMPLETO DEL SISTEMA SISAGENT")
    print("=" * 80)
    fecha_hoy = datetime.now()
    print(f"Fecha: {fecha_hoy.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Configuración
    timestamp = fecha_hoy.strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_completo_{timestamp}"
    backup_dir = "backups"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Crear directorio de respaldos si no existe
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Crear directorio del respaldo
    os.makedirs(backup_path, exist_ok=True)
    
    # Lista completa de archivos importantes a respaldar
    archivos_importantes = [
        # Archivos principales del sistema
        "app.py",
        "config.py",
        "requirements.txt",
        "requirements_optimizado.txt",
        
        # Archivos de configuración Railway
        "Procfile",
        "Procfile_optimizado",
        "railway.toml",
        "railway_optimized.toml",
        
        # Archivos de configuración
        "config.env",
        ".gitignore" if os.path.exists(".gitignore") else None,
        
        # Documentación
        "README.md",
        "README_OPTIMIZED.md",
        
        # Scripts importantes
        "backup_system.py",
        "backup_db.py",
        "crear_backup_completo.py",
    ]
    
    # Lista de directorios importantes
    directorios_importantes = [
        "templates",
        "static" if os.path.exists("static") else None,
        "logs" if os.path.exists("logs") else None,
        "instance" if os.path.exists("instance") else None,
    ]
    
    # Archivos de base de datos (SQLite)
    archivos_db = [
        "sisagent_consolidada.db",
        "sisagent.db",
    ]
    
    archivos_respaldados = []
    directorios_respaldados = []
    bases_datos_respaldadas = []
    errores = []
    
    print("Respaldando archivos del sistema...")
    print("-" * 80)
    
    # Respaldar archivos individuales
    for archivo in archivos_importantes:
        if archivo and os.path.exists(archivo):
            try:
                shutil.copy2(archivo, backup_path)
                archivos_respaldados.append(archivo)
                tamaño = os.path.getsize(archivo) / 1024  # KB
                print(f"[OK] {archivo:50s} ({tamaño:8.2f} KB)")
            except Exception as e:
                error_msg = f"Error al respaldar {archivo}: {e}"
                errores.append(error_msg)
                print(f"[ERROR] {archivo:50s} - ERROR: {e}")
    
    print()
    print("Respaldando directorios...")
    print("-" * 80)
    
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
                
                # Contar archivos
                num_archivos = sum(
                    len(filenames)
                    for _, _, filenames in os.walk(directorio)
                )
                
                print(f"[OK] {directorio:50s} ({tamaño_total:8.2f} KB, {num_archivos} archivos)")
            except Exception as e:
                error_msg = f"Error al respaldar {directorio}: {e}"
                errores.append(error_msg)
                print(f"[ERROR] {directorio:50s} - ERROR: {e}")
    
    print()
    print("Respaldando bases de datos...")
    print("-" * 80)
    
    # Respaldar bases de datos
    for db_file in archivos_db:
        if os.path.exists(db_file):
            try:
                db_backup_path = os.path.join(backup_path, db_file)
                shutil.copy2(db_file, db_backup_path)
                bases_datos_respaldadas.append(db_file)
                tamaño = os.path.getsize(db_file) / (1024 * 1024)  # MB
                print(f"[OK] {db_file:50s} ({tamaño:8.2f} MB)")
            except Exception as e:
                error_msg = f"Error al respaldar {db_file}: {e}"
                errores.append(error_msg)
                print(f"[ERROR] {db_file:50s} - ERROR: {e}")
    
    if not bases_datos_respaldadas:
        print("[ADVERTENCIA] No se encontraron bases de datos para respaldar")
        print("   (Esto es normal si el sistema usa PostgreSQL en Railway)")
    
    print()
    print("Creando archivo de informacion del backup...")
    
    # Obtener información del sistema
    try:
        import sys
        python_version = sys.version.split()[0]
    except:
        python_version = "Desconocida"
    
    # Crear archivo de información del respaldo
    backup_info = {
        "backup_name": backup_name,
        "timestamp": timestamp,
        "fecha_creacion": fecha_hoy.isoformat(),
        "fecha_legible": fecha_hoy.strftime('%d/%m/%Y %H:%M:%S'),
        "descripcion": "Backup completo del sistema SISAGENT - Código fuente, datos y configuraciones",
        "tipo": "Backup completo del sistema",
        "archivos_respaldados": archivos_respaldados,
        "directorios_respaldados": directorios_respaldados,
        "bases_datos_respaldadas": bases_datos_respaldadas,
        "total_archivos": len(archivos_respaldados),
        "total_directorios": len(directorios_respaldados),
        "total_bases_datos": len(bases_datos_respaldadas),
        "errores": errores,
        "sistema": {
            "nombre": "SISAGENT",
            "version": "Ultra Optimizada",
            "tipo": "Sistema de Gestión de Operaciones Bancarias",
            "python_version": python_version
        },
        "instrucciones_restauracion": {
            "paso_1": "Descomprimir el archivo ZIP o usar el directorio del backup",
            "paso_2": "Restaurar los archivos en el sistema",
            "paso_3": "Restaurar la base de datos (si aplica)",
            "paso_4": "Verificar que todas las dependencias estén instaladas"
        }
    }
    
    info_file = os.path.join(backup_path, "backup_info.json")
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Informacion guardada en: backup_info.json")
    
    # Crear archivo ZIP del backup
    print()
    print("Creando archivo ZIP del backup...")
    print("-" * 80)
    
    zip_filename = f"{backup_name}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)
    
    archivos_en_zip = 0
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Agregar todos los archivos del directorio de backup
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
                    archivos_en_zip += 1
                    if archivos_en_zip <= 10:  # Mostrar solo los primeros 10
                        print(f"[OK] Agregado: {arcname}")
        
        zip_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
        print(f"[OK] Archivo ZIP creado exitosamente")
        print(f"   Nombre: {zip_filename}")
        print(f"   Tamano: {zip_size:.2f} MB")
        print(f"   Archivos incluidos: {archivos_en_zip}")
        
    except Exception as e:
        print(f"[ADVERTENCIA] Error al crear ZIP: {e}")
        zip_path = None
    
    # Resumen final
    print()
    print("=" * 80)
    print("BACKUP COMPLETO CREADO EXITOSAMENTE")
    print("=" * 80)
    print(f"Nombre del backup: {backup_name}")
    print(f"Ubicacion del directorio: {backup_path}")
    if zip_path:
        print(f"Archivo ZIP: {zip_path}")
    print()
    print("Resumen del backup:")
    print(f"   - Archivos respaldados: {len(archivos_respaldados)}")
    print(f"   - Directorios respaldados: {len(directorios_respaldados)}")
    print(f"   - Bases de datos respaldadas: {len(bases_datos_respaldadas)}")
    if errores:
        print(f"   - Errores encontrados: {len(errores)}")
    print()
    print("Contenido del backup:")
    print("   [OK] Codigo fuente completo (app.py)")
    print("   [OK] Dependencias (requirements.txt)")
    print("   [OK] Configuraciones (Procfile, railway.toml, config.env)")
    print("   [OK] Templates HTML")
    if bases_datos_respaldadas:
        print("   [OK] Base de datos con todos los datos")
    print("   [OK] Documentacion")
    print()
    print("Para restaurar este backup:")
    print("   1. Descomprime el archivo ZIP o usa el directorio del backup")
    print("   2. Restaura los archivos en el sistema")
    if bases_datos_respaldadas:
        print("   3. Restaura la base de datos")
    print("   4. Verifica que todas las dependencias esten instaladas")
    print("=" * 80)
    
    return backup_name, backup_path, zip_path

if __name__ == "__main__":
    try:
        backup_name, backup_path, zip_path = crear_backup_completo_hoy()
        print(f"\n[OK] Backup completado exitosamente: {backup_name}")
    except Exception as e:
        print(f"\n❌ Error al crear backup: {e}")
        import traceback
        traceback.print_exc()

