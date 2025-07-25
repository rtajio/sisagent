#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para restaurar el backup de la versión 1 de SISAGENT
"""

import os
import shutil
import sys
from datetime import datetime

def print_header():
    print("=" * 60)
    print("🔄 RESTAURADOR DE BACKUP - SISAGENT V1")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)

def check_destination():
    """Verifica si el directorio de destino existe"""
    if os.path.exists("sisagent_restaurado"):
        print("⚠️  ADVERTENCIA: El directorio 'sisagent_restaurado' ya existe")
        response = input("¿Deseas sobrescribirlo? (s/n): ").lower()
        if response != 's':
            print("❌ Restauración cancelada")
            return False
        shutil.rmtree("sisagent_restaurado")
    return True

def restore_backup():
    """Restaura el backup"""
    try:
        print("📁 Creando directorio de destino...")
        os.makedirs("sisagent_restaurado", exist_ok=True)
        
        print("📋 Copiando archivos principales...")
        files_to_copy = [
            "app.py",
            "requirements.txt", 
            "Procfile",
            "config.env",
            "README.md"
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                shutil.copy2(file, f"sisagent_restaurado/{file}")
                print(f"   ✅ {file}")
            else:
                print(f"   ⚠️  {file} no encontrado")
        
        print("📁 Copiando carpeta templates...")
        if os.path.exists("templates"):
            shutil.copytree("templates", "sisagent_restaurado/templates")
            print("   ✅ templates/")
        else:
            print("   ⚠️  templates/ no encontrado")
        
        print("📄 Copiando archivos de documentación...")
        for file in os.listdir("."):
            if file.endswith(".md") and file != "BACKUP_INFO.md":
                shutil.copy2(file, f"sisagent_restaurado/{file}")
                print(f"   ✅ {file}")
        
        print("📋 Copiando información del backup...")
        shutil.copy2("BACKUP_INFO.md", "sisagent_restaurado/BACKUP_INFO.md")
        
        print("\n" + "=" * 60)
        print("✅ RESTAURACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("📁 Directorio restaurado: sisagent_restaurado/")
        print("📋 Archivos restaurados:")
        
        # Listar archivos restaurados
        for root, dirs, files in os.walk("sisagent_restaurado"):
            level = root.replace("sisagent_restaurado", "").count(os.sep)
            indent = " " * 2 * level
            print(f"{indent}📁 {os.path.basename(root)}/")
            subindent = " " * 2 * (level + 1)
            for file in files:
                print(f"{subindent}📄 {file}")
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. cd sisagent_restaurado")
        print("2. pip install -r requirements.txt")
        print("3. Configurar variables de entorno (DATABASE_URL, SECRET_KEY)")
        print("4. python app.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la restauración: {str(e)}")
        return False

def main():
    print_header()
    
    if not check_destination():
        return
    
    print("🔄 Iniciando restauración...")
    if restore_backup():
        print("\n🎉 ¡Backup restaurado exitosamente!")
    else:
        print("\n💥 Error en la restauración")

if __name__ == "__main__":
    main() 