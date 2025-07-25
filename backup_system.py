#!/usr/bin/env python3
"""
Script de Respaldo y Restauración del Sistema SISAGENT
Permite crear puntos de restauración y restaurar el sistema a un estado anterior
"""

import os
import shutil
import json
import zipfile
from datetime import datetime
import sqlite3

class SystemBackup:
    def __init__(self):
        self.backup_dir = "backups"
        self.current_dir = os.getcwd()
        self.db_file = "sisagent.db"
        self.backup_info_file = "backup_info.json"
        
        # Crear directorio de respaldos si no existe
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self, description="Respaldo automático"):
        """Crear un punto de restauración del sistema"""
        try:
            # Generar nombre del respaldo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            print(f"🔄 Creando respaldo: {backup_name}")
            print(f"📝 Descripción: {description}")
            
            # Crear directorio del respaldo
            os.makedirs(backup_path)
            
            # Lista de archivos y directorios a respaldar
            files_to_backup = [
                "app.py",
                "wsgi.py",
                "init_db.py",
                "requirements.txt",
                "Procfile",
                "railway.toml",
                "config.env"
            ]
            
            directories_to_backup = [
                "templates",
                "static" if os.path.exists("static") else None
            ]
            
            # Respaldar archivos individuales
            for file_name in files_to_backup:
                if os.path.exists(file_name):
                    shutil.copy2(file_name, backup_path)
                    print(f"✅ Respaldo: {file_name}")
            
            # Respaldar directorios
            for dir_name in directories_to_backup:
                if dir_name and os.path.exists(dir_name):
                    dir_backup_path = os.path.join(backup_path, dir_name)
                    shutil.copytree(dir_name, dir_backup_path)
                    print(f"✅ Respaldo: {dir_name}/")
            
            # Respaldar base de datos
            if os.path.exists(self.db_file):
                db_backup_path = os.path.join(backup_path, self.db_file)
                shutil.copy2(self.db_file, db_backup_path)
                print(f"✅ Respaldo: {self.db_file}")
            
            # Crear archivo de información del respaldo
            backup_info = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "description": description,
                "files_backed_up": files_to_backup,
                "directories_backed_up": [d for d in directories_to_backup if d],
                "database_backed_up": os.path.exists(self.db_file),
                "created_at": datetime.now().isoformat()
            }
            
            with open(os.path.join(backup_path, self.backup_info_file), 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, indent=2, ensure_ascii=False)
            
            print(f"🎉 Respaldo creado exitosamente: {backup_name}")
            print(f"📁 Ubicación: {backup_path}")
            
            return backup_name
            
        except Exception as e:
            print(f"❌ Error al crear respaldo: {str(e)}")
            return None
    
    def list_backups(self):
        """Listar todos los respaldos disponibles"""
        try:
            if not os.path.exists(self.backup_dir):
                print("📁 No hay respaldos disponibles")
                return []
            
            backups = []
            for item in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, item)
                if os.path.isdir(backup_path):
                    info_file = os.path.join(backup_path, self.backup_info_file)
                    if os.path.exists(info_file):
                        with open(info_file, 'r', encoding='utf-8') as f:
                            info = json.load(f)
                            backups.append(info)
            
            if not backups:
                print("📁 No hay respaldos disponibles")
                return []
            
            print("📋 Respaldos disponibles:")
            print("=" * 80)
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['backup_name']}")
                print(f"   📅 Fecha: {backup['timestamp']}")
                print(f"   📝 Descripción: {backup['description']}")
                print(f"   📊 Base de datos: {'✅' if backup['database_backed_up'] else '❌'}")
                print("-" * 80)
            
            return backups
            
        except Exception as e:
            print(f"❌ Error al listar respaldos: {str(e)}")
            return []
    
    def restore_backup(self, backup_name):
        """Restaurar el sistema desde un respaldo"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                print(f"❌ Respaldo no encontrado: {backup_name}")
                return False
            
            info_file = os.path.join(backup_path, self.backup_info_file)
            if not os.path.exists(info_file):
                print(f"❌ Información del respaldo no encontrada: {backup_name}")
                return False
            
            # Leer información del respaldo
            with open(info_file, 'r', encoding='utf-8') as f:
                backup_info = json.load(f)
            
            print(f"🔄 Restaurando sistema desde: {backup_name}")
            print(f"📝 Descripción: {backup_info['description']}")
            print(f"📅 Fecha del respaldo: {backup_info['timestamp']}")
            
            # Confirmar restauración
            confirm = input("⚠️ ¿Estás seguro de que quieres restaurar el sistema? (sí/no): ").lower()
            if confirm not in ['sí', 'si', 'yes', 'y', 's']:
                print("❌ Restauración cancelada")
                return False
            
            # Crear respaldo del estado actual antes de restaurar
            print("🔄 Creando respaldo del estado actual...")
            current_backup = self.create_backup("Respaldo automático antes de restauración")
            
            # Restaurar archivos
            for file_name in backup_info['files_backed_up']:
                backup_file = os.path.join(backup_path, file_name)
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, file_name)
                    print(f"✅ Restaurado: {file_name}")
            
            # Restaurar directorios
            for dir_name in backup_info['directories_backed_up']:
                backup_dir = os.path.join(backup_path, dir_name)
                if os.path.exists(backup_dir):
                    # Eliminar directorio actual si existe
                    if os.path.exists(dir_name):
                        shutil.rmtree(dir_name)
                    # Restaurar directorio del respaldo
                    shutil.copytree(backup_dir, dir_name)
                    print(f"✅ Restaurado: {dir_name}/")
            
            # Restaurar base de datos
            if backup_info['database_backed_up']:
                backup_db = os.path.join(backup_path, self.db_file)
                if os.path.exists(backup_db):
                    # Crear respaldo de la base de datos actual
                    if os.path.exists(self.db_file):
                        current_db_backup = f"{self.db_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        shutil.copy2(self.db_file, current_db_backup)
                        print(f"📊 Respaldo de BD actual: {current_db_backup}")
                    
                    # Restaurar base de datos del respaldo
                    shutil.copy2(backup_db, self.db_file)
                    print(f"✅ Restaurado: {self.db_file}")
            
            print(f"🎉 Sistema restaurado exitosamente desde: {backup_name}")
            print(f"📁 Respaldo del estado anterior: {current_backup}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al restaurar respaldo: {str(e)}")
            return False
    
    def delete_backup(self, backup_name):
        """Eliminar un respaldo"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if not os.path.exists(backup_path):
                print(f"❌ Respaldo no encontrado: {backup_name}")
                return False
            
            confirm = input(f"⚠️ ¿Estás seguro de que quieres eliminar el respaldo '{backup_name}'? (sí/no): ").lower()
            if confirm not in ['sí', 'si', 'yes', 'y', 's']:
                print("❌ Eliminación cancelada")
                return False
            
            shutil.rmtree(backup_path)
            print(f"✅ Respaldo eliminado: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error al eliminar respaldo: {str(e)}")
            return False

def main():
    """Función principal del script"""
    backup_system = SystemBackup()
    
    print("🛡️ Sistema de Respaldo y Restauración SISAGENT")
    print("=" * 50)
    
    while True:
        print("\n📋 Opciones disponibles:")
        print("1. Crear respaldo del sistema")
        print("2. Listar respaldos disponibles")
        print("3. Restaurar sistema desde respaldo")
        print("4. Eliminar respaldo")
        print("5. Salir")
        
        choice = input("\n🔧 Selecciona una opción (1-5): ").strip()
        
        if choice == "1":
            description = input("📝 Descripción del respaldo (opcional): ").strip()
            if not description:
                description = "Respaldo manual del sistema"
            backup_system.create_backup(description)
            
        elif choice == "2":
            backup_system.list_backups()
            
        elif choice == "3":
            backups = backup_system.list_backups()
            if backups:
                try:
                    backup_index = int(input("🔢 Selecciona el número del respaldo a restaurar: ")) - 1
                    if 0 <= backup_index < len(backups):
                        backup_name = backups[backup_index]['backup_name']
                        backup_system.restore_backup(backup_name)
                    else:
                        print("❌ Número de respaldo inválido")
                except ValueError:
                    print("❌ Por favor ingresa un número válido")
            
        elif choice == "4":
            backups = backup_system.list_backups()
            if backups:
                try:
                    backup_index = int(input("🔢 Selecciona el número del respaldo a eliminar: ")) - 1
                    if 0 <= backup_index < len(backups):
                        backup_name = backups[backup_index]['backup_name']
                        backup_system.delete_backup(backup_name)
                    else:
                        print("❌ Número de respaldo inválido")
                except ValueError:
                    print("❌ Por favor ingresa un número válido")
            
        elif choice == "5":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida. Por favor selecciona 1-5.")

if __name__ == "__main__":
    main() 