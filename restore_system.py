#!/usr/bin/env python3
"""
Script de Restauración del Sistema SISAGENT
Permite restaurar el sistema a un punto de restauración anterior
"""

import os
import shutil
import json
from datetime import datetime

def list_restore_points():
    """Listar todos los puntos de restauración disponibles"""
    backup_dir = "backups"
    
    if not os.path.exists(backup_dir):
        print("📁 No hay puntos de restauración disponibles")
        return []
    
    restore_points = []
    
    for item in os.listdir(backup_dir):
        backup_path = os.path.join(backup_dir, item)
        if os.path.isdir(backup_path):
            info_file = os.path.join(backup_path, "backup_info.json")
            if os.path.exists(info_file):
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        restore_points.append(info)
                except:
                    continue
    
    if not restore_points:
        print("📁 No hay puntos de restauración disponibles")
        return []
    
    print("📋 Puntos de restauración disponibles:")
    print("=" * 80)
    for i, point in enumerate(restore_points, 1):
        print(f"{i}. {point['backup_name']}")
        print(f"   📅 Fecha: {point['timestamp']}")
        print(f"   📝 Descripción: {point['description']}")
        if 'status' in point:
            print(f"   🎯 Estado: {point['status']}")
        print("-" * 80)
    
    return restore_points

def restore_system(backup_name):
    """Restaurar el sistema desde un punto de restauración"""
    backup_dir = "backups"
    backup_path = os.path.join(backup_dir, backup_name)
    
    if not os.path.exists(backup_path):
        print(f"❌ Punto de restauración no encontrado: {backup_name}")
        return False
    
    info_file = os.path.join(backup_path, "backup_info.json")
    if not os.path.exists(info_file):
        print(f"❌ Información del punto de restauración no encontrada: {backup_name}")
        return False
    
    # Leer información del respaldo
    with open(info_file, 'r', encoding='utf-8') as f:
        backup_info = json.load(f)
    
    print(f"🔄 Restaurando sistema desde: {backup_name}")
    print(f"📝 Descripción: {backup_info['description']}")
    print(f"📅 Fecha del respaldo: {backup_info['timestamp']}")
    
    # Confirmar restauración
    print("\n⚠️ ADVERTENCIA: Esta acción sobrescribirá los archivos actuales del sistema.")
    confirm = input("¿Estás seguro de que quieres restaurar el sistema? (sí/no): ").lower()
    if confirm not in ['sí', 'si', 'yes', 'y', 's']:
        print("❌ Restauración cancelada")
        return False
    
    try:
        # Crear respaldo del estado actual antes de restaurar
        print("🔄 Creando respaldo del estado actual...")
        current_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup_name = f"pre_restore_backup_{current_timestamp}"
        current_backup_path = os.path.join(backup_dir, current_backup_name)
        os.makedirs(current_backup_path)
        
        # Respaldar archivos actuales importantes
        current_files = ["app.py", "wsgi.py", "init_db.py", "requirements.txt", "Procfile", "railway.toml"]
        for file_name in current_files:
            if os.path.exists(file_name):
                shutil.copy2(file_name, current_backup_path)
        
        # Respaldar directorio templates actual
        if os.path.exists("templates"):
            shutil.copytree("templates", os.path.join(current_backup_path, "templates"))
        
        # Respaldar base de datos actual
        if os.path.exists("sisagent.db"):
            shutil.copy2("sisagent.db", current_backup_path)
        
        print(f"✅ Respaldo del estado actual creado: {current_backup_name}")
        
        # Restaurar archivos
        for file_name in backup_info['files_backed_up']:
            backup_file = os.path.join(backup_path, file_name)
            if os.path.exists(backup_file):
                shutil.copy2(backup_file, file_name)
                print(f"✅ Restaurado: {file_name}")
        
        # Restaurar directorios
        for dir_name in backup_info['directories_backed_up']:
            backup_dir_path = os.path.join(backup_path, dir_name)
            if os.path.exists(backup_dir_path):
                # Eliminar directorio actual si existe
                if os.path.exists(dir_name):
                    shutil.rmtree(dir_name)
                # Restaurar directorio del respaldo
                shutil.copytree(backup_dir_path, dir_name)
                print(f"✅ Restaurado: {dir_name}/")
        
        # Restaurar base de datos
        if backup_info['database_backed_up']:
            backup_db = os.path.join(backup_path, "sisagent.db")
            if os.path.exists(backup_db):
                # Crear respaldo de la base de datos actual
                if os.path.exists("sisagent.db"):
                    current_db_backup = f"sisagent.db.backup_{current_timestamp}"
                    shutil.copy2("sisagent.db", current_db_backup)
                    print(f"📊 Respaldo de BD actual: {current_db_backup}")
                
                # Restaurar base de datos del respaldo
                shutil.copy2(backup_db, "sisagent.db")
                print(f"✅ Restaurado: sisagent.db")
        
        print(f"🎉 Sistema restaurado exitosamente desde: {backup_name}")
        print(f"📁 Respaldo del estado anterior: {current_backup_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al restaurar sistema: {str(e)}")
        return False

def main():
    """Función principal del script"""
    print("🛡️ Sistema de Restauración SISAGENT")
    print("=" * 50)
    
    while True:
        print("\n📋 Opciones disponibles:")
        print("1. Listar puntos de restauración")
        print("2. Restaurar sistema")
        print("3. Salir")
        
        choice = input("\n🔧 Selecciona una opción (1-3): ").strip()
        
        if choice == "1":
            list_restore_points()
            
        elif choice == "2":
            restore_points = list_restore_points()
            if restore_points:
                try:
                    point_index = int(input("🔢 Selecciona el número del punto de restauración: ")) - 1
                    if 0 <= point_index < len(restore_points):
                        backup_name = restore_points[point_index]['backup_name']
                        restore_system(backup_name)
                    else:
                        print("❌ Número de punto de restauración inválido")
                except ValueError:
                    print("❌ Por favor ingresa un número válido")
            
        elif choice == "3":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida. Por favor selecciona 1-3.")

if __name__ == "__main__":
    main()