#!/usr/bin/env python3
"""
Script para hacer backup de la base de datos PostgreSQL en Railway
Usa Railway CLI para conectarse y hacer dump de la base de datos
"""

import os
import subprocess
import sys
from datetime import datetime
import json

def verificar_railway_cli():
    """Verificar si Railway CLI está instalado"""
    try:
        result = subprocess.run(['railway', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            print(f"[OK] Railway CLI encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("[ERROR] Railway CLI no está instalado")
        print("        Instala con: npm install -g @railway/cli")
        return False
    except Exception as e:
        print(f"[ERROR] Error al verificar Railway CLI: {e}")
        return False
    return False

def hacer_backup_railway():
    """Hacer backup de la base de datos PostgreSQL en Railway"""
    
    print("=" * 70)
    print("BACKUP DE BASE DE DATOS EN RAILWAY")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Verificar Railway CLI
    if not verificar_railway_cli():
        print("\n[ERROR] No se puede continuar sin Railway CLI")
        print("\nInstrucciones para instalar:")
        print("1. Instalar Node.js desde: https://nodejs.org/")
        print("2. Ejecutar: npm install -g @railway/cli")
        print("3. Ejecutar: railway login")
        return False
    
    # Verificar si está logueado
    try:
        result = subprocess.run(['railway', 'whoami'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode != 0:
            print("[ERROR] No estás logueado en Railway")
            print("        Ejecuta: railway login")
            return False
        print(f"[OK] Logueado como: {result.stdout.strip()}")
    except Exception as e:
        print(f"[ERROR] Error al verificar login: {e}")
        return False
    
    # Crear directorio de backups si no existe
    backup_dir = "backups_railway"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"[OK] Directorio creado: {backup_dir}")
    
    # Generar nombre del backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"railway_backup_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    print()
    print("Generando backup de PostgreSQL...")
    print("-" * 70)
    
    try:
        # Obtener DATABASE_URL de Railway
        print("[INFO] Obteniendo DATABASE_URL de Railway...")
        result = subprocess.run(
            ['railway', 'variables', '--json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print("[ERROR] No se pudo obtener variables de Railway")
            print(f"        Error: {result.stderr}")
            return False
        
        # Parsear JSON de variables
        try:
            variables = json.loads(result.stdout)
            database_url = None
            
            for var in variables:
                if var.get('name') == 'DATABASE_URL':
                    database_url = var.get('value')
                    break
            
            if not database_url:
                print("[ERROR] DATABASE_URL no encontrada en Railway")
                print("        Asegúrate de que la base de datos PostgreSQL esté configurada")
                return False
            
            print(f"[OK] DATABASE_URL obtenida")
            
            # Hacer backup usando pg_dump a través de Railway
            print("[INFO] Ejecutando pg_dump...")
            
            # Opción 1: Usar railway run para ejecutar pg_dump en el contenedor
            cmd = [
                'railway', 'run', 'pg_dump',
                '--no-owner',
                '--no-acl',
                '--clean',
                '--if-exists'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutos timeout
                env=os.environ.copy()
            )
            
            if result.returncode == 0:
                # Guardar backup
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                
                tamaño = os.path.getsize(backup_path) / (1024 * 1024)  # MB
                print(f"[OK] Backup creado exitosamente")
                print(f"     Archivo: {backup_path}")
                print(f"     Tamaño: {tamaño:.2f} MB")
                
                # Crear archivo de información
                info = {
                    'fecha': datetime.now().isoformat(),
                    'archivo': backup_filename,
                    'tamaño_mb': round(tamaño, 2),
                    'sistema': 'SISAGENT',
                    'plataforma': 'Railway',
                    'tipo_db': 'PostgreSQL'
                }
                
                info_path = os.path.join(backup_dir, f"backup_info_{timestamp}.json")
                with open(info_path, 'w', encoding='utf-8') as f:
                    json.dump(info, f, indent=2, ensure_ascii=False)
                
                print()
                print("=" * 70)
                print("BACKUP COMPLETADO EXITOSAMENTE")
                print("=" * 70)
                print(f"Archivo: {backup_path}")
                print(f"Tamaño: {tamaño:.2f} MB")
                print()
                print("Para restaurar este backup:")
                print(f"  railway run psql < {backup_path}")
                print("=" * 70)
                
                return True
            else:
                print(f"[ERROR] Error al ejecutar pg_dump")
                print(f"        {result.stderr}")
                
                # Opción alternativa: usar método manual
                print()
                print("[INFO] Intentando método alternativo...")
                print("       Puedes hacer backup manualmente desde Railway Dashboard:")
                print("       1. Ve a tu proyecto en Railway")
                print("       2. Abre la base de datos PostgreSQL")
                print("       3. Usa la opción 'Backup' o 'Export'")
                
                return False
                
        except json.JSONDecodeError:
            print("[ERROR] No se pudo parsear las variables de Railway")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Timeout al ejecutar comando (más de 10 minutos)")
        return False
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

def listar_backups_railway():
    """Listar backups disponibles"""
    backup_dir = "backups_railway"
    
    if not os.path.exists(backup_dir):
        print("[INFO] No hay backups disponibles")
        return
    
    backups = []
    for file in os.listdir(backup_dir):
        if file.endswith('.sql'):
            file_path = os.path.join(backup_dir, file)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            file_time = os.path.getmtime(file_path)
            backups.append({
                'name': file,
                'path': file_path,
                'size': file_size,
                'time': file_time
            })
    
    if not backups:
        print("[INFO] No hay backups disponibles")
        return
    
    # Ordenar por fecha (más reciente primero)
    backups.sort(key=lambda x: x['time'], reverse=True)
    
    print("=" * 70)
    print("BACKUPS DISPONIBLES")
    print("=" * 70)
    for i, backup in enumerate(backups, 1):
        date_str = datetime.fromtimestamp(backup['time']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {backup['name']}")
        print(f"   Fecha: {date_str}")
        print(f"   Tamaño: {backup['size']:.2f} MB")
        print("-" * 70)

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == 'list':
        listar_backups_railway()
    else:
        hacer_backup_railway()

if __name__ == "__main__":
    main()

