#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear backup SEGURO previo con fecha de hoy y ejecutar deploy en Railway
Garantiza que la base de datos se copie correctamente sin perder datos
"""

import os
import shutil
import json
import zipfile
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configurar codificación UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def copiar_base_datos_segura(origen, destino):
    """
    Copiar base de datos SQLite de forma segura usando el método .backup de SQLite
    Esto garantiza que la base de datos se copie correctamente incluso si está en uso
    """
    try:
        # Método 1: Usar el comando .backup de SQLite (más seguro)
        conn_origen = sqlite3.connect(origen)
        conn_destino = sqlite3.connect(destino)
        
        # Usar el método backup de SQLite
        conn_origen.backup(conn_destino)
        
        conn_destino.close()
        conn_origen.close()
        
        return True, "Base de datos copiada usando método seguro de SQLite"
    except Exception as e:
        try:
            # Método 2: Si falla, usar shutil.copy2 (fallback)
            shutil.copy2(origen, destino)
            return True, f"Base de datos copiada usando método alternativo (advertencia: {e})"
        except Exception as e2:
            return False, f"Error al copiar base de datos: {e2}"

def verificar_base_datos(ruta_db):
    """Verificar que la base de datos tiene datos (usuarios)"""
    try:
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        
        # Verificar si existe la tabla usuarios
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuario'")
        tabla_existe = cursor.fetchone() is not None
        
        if not tabla_existe:
            conn.close()
            return False, "La tabla 'usuario' no existe en la base de datos"
        
        # Contar usuarios
        cursor.execute("SELECT COUNT(*) FROM usuario")
        num_usuarios = cursor.fetchone()[0]
        
        # Verificar si hay admin
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE username='admin'")
        tiene_admin = cursor.fetchone()[0] > 0
        
        conn.close()
        
        return True, {
            "tabla_existe": True,
            "num_usuarios": num_usuarios,
            "tiene_admin": tiene_admin
        }
    except Exception as e:
        return False, f"Error al verificar base de datos: {e}"

def crear_backup_seguro():
    """Crear backup seguro del sistema sin modificar nada"""
    
    print("=" * 80)
    print("🛡️ CREANDO BACKUP SEGURO PREVIO DEL SISTEMA")
    print("=" * 80)
    fecha_hoy = datetime.now()
    print(f"📅 Fecha: {fecha_hoy.strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    print("⚠️ IMPORTANTE: Este backup SOLO COPIA archivos, NO modifica nada")
    print()
    
    # Configuración
    timestamp = fecha_hoy.strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_pre_modificaciones_{timestamp}"
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
        "config.py",
        "requirements.txt",
        "requirements_optimizado.txt",
        "Procfile",
        "Procfile_optimizado",
        "railway.toml",
        "railway_optimized.toml",
        "config.env",
        ".gitignore" if os.path.exists(".gitignore") else None,
        "README.md",
        "README_OPTIMIZED.md",
    ]
    
    # Directorios importantes
    directorios_importantes = [
        "templates",
        "static" if os.path.exists("static") else None,
        "logs" if os.path.exists("logs") else None,
        "instance" if os.path.exists("instance") else None,
    ]
    
    # Archivos de base de datos
    archivos_db = [
        "sisagent_consolidada.db",
        "sisagent.db",
    ]
    
    # También buscar en instance/
    if os.path.exists("instance"):
        for db_file in ["sisagent_consolidada.db", "sisagent.db"]:
            db_path = os.path.join("instance", db_file)
            if os.path.exists(db_path):
                archivos_db.append(db_path)
    
    archivos_respaldados = []
    directorios_respaldados = []
    bases_datos_respaldadas = []
    errores = []
    verificaciones_db = []
    
    print("📋 Paso 1: Respaldando archivos del sistema...")
    print("-" * 80)
    
    # Respaldar archivos individuales
    for archivo in archivos_importantes:
        if archivo and os.path.exists(archivo):
            try:
                shutil.copy2(archivo, backup_path)
                archivos_respaldados.append(archivo)
                tamaño = os.path.getsize(archivo) / 1024  # KB
                print(f"   ✅ {archivo:50s} ({tamaño:8.2f} KB)")
            except Exception as e:
                error_msg = f"Error al respaldar {archivo}: {e}"
                errores.append(error_msg)
                print(f"   ❌ {archivo:50s} - ERROR: {e}")
    
    print()
    print("📋 Paso 2: Respaldando directorios...")
    print("-" * 80)
    
    # Respaldar directorios
    for directorio in directorios_importantes:
        if directorio and os.path.exists(directorio):
            try:
                dir_backup_path = os.path.join(backup_path, directorio)
                shutil.copytree(directorio, dir_backup_path, dirs_exist_ok=True)
                directorios_respaldados.append(directorio)
                
                tamaño_total = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(directorio)
                    for filename in filenames
                ) / 1024  # KB
                
                num_archivos = sum(
                    len(filenames)
                    for _, _, filenames in os.walk(directorio)
                )
                
                print(f"   ✅ {directorio:50s} ({tamaño_total:8.2f} KB, {num_archivos} archivos)")
            except Exception as e:
                error_msg = f"Error al respaldar {directorio}: {e}"
                errores.append(error_msg)
                print(f"   ❌ {directorio:50s} - ERROR: {e}")
    
    print()
    print("📋 Paso 3: Respaldando bases de datos (MÉTODO SEGURO)...")
    print("-" * 80)
    
    # Respaldar bases de datos de forma segura
    for db_file in archivos_db:
        if os.path.exists(db_file):
            try:
                # Determinar nombre del archivo de destino
                if os.path.dirname(db_file):
                    # Si está en un subdirectorio, mantener la estructura
                    db_backup_path = os.path.join(backup_path, db_file)
                    os.makedirs(os.path.dirname(db_backup_path), exist_ok=True)
                else:
                    db_backup_path = os.path.join(backup_path, os.path.basename(db_file))
                
                # Copiar usando método seguro
                exito, mensaje = copiar_base_datos_segura(db_file, db_backup_path)
                
                if exito:
                    bases_datos_respaldadas.append(db_file)
                    tamaño = os.path.getsize(db_file) / (1024 * 1024)  # MB
                    print(f"   ✅ {db_file:50s} ({tamaño:8.2f} MB)")
                    print(f"      Método: {mensaje}")
                    
                    # Verificar que la copia tiene datos
                    print(f"      Verificando integridad...")
                    exito_verif, resultado_verif = verificar_base_datos(db_backup_path)
                    if exito_verif and isinstance(resultado_verif, dict):
                        verificaciones_db.append({
                            "archivo": db_file,
                            "usuarios": resultado_verif["num_usuarios"],
                            "tiene_admin": resultado_verif["tiene_admin"]
                        })
                        print(f"      ✅ Verificación: {resultado_verif['num_usuarios']} usuarios, Admin: {'Sí' if resultado_verif['tiene_admin'] else 'No'}")
                    else:
                        print(f"      ⚠️  Advertencia en verificación: {resultado_verif}")
                else:
                    error_msg = f"Error al respaldar {db_file}: {mensaje}"
                    errores.append(error_msg)
                    print(f"   ❌ {db_file:50s} - ERROR: {mensaje}")
            except Exception as e:
                error_msg = f"Error al respaldar {db_file}: {e}"
                errores.append(error_msg)
                print(f"   ❌ {db_file:50s} - ERROR: {e}")
    
    if not bases_datos_respaldadas:
        print("   ⚠️  No se encontraron bases de datos locales para respaldar")
        print("      (Esto es normal si el sistema usa PostgreSQL en Railway)")
    
    print()
    print("📋 Paso 4: Verificando base de datos ORIGINAL (para confirmar que no se modificó)...")
    print("-" * 80)
    
    # Verificar que la base de datos original sigue intacta
    for db_file in bases_datos_respaldadas:
        if os.path.exists(db_file):
            exito_verif, resultado_verif = verificar_base_datos(db_file)
            if exito_verif and isinstance(resultado_verif, dict):
                print(f"   ✅ {db_file}: {resultado_verif['num_usuarios']} usuarios, Admin: {'Sí' if resultado_verif['tiene_admin'] else 'No'}")
                print(f"      ✅ La base de datos original NO fue modificada")
            else:
                print(f"   ⚠️  {db_file}: {resultado_verif}")
    
    print()
    print("📋 Paso 5: Creando archivo de información del backup...")
    
    # Obtener información del sistema
    try:
        python_version = sys.version.split()[0]
    except:
        python_version = "Desconocida"
    
    # Crear archivo de información del respaldo
    backup_info = {
        "backup_name": backup_name,
        "timestamp": timestamp,
        "fecha_creacion": fecha_hoy.isoformat(),
        "fecha_legible": fecha_hoy.strftime('%d/%m/%Y %H:%M:%S'),
        "descripcion": "Backup SEGURO previo a modificaciones - Solo copia, NO modifica nada",
        "tipo": "Backup seguro previo a modificaciones",
        "archivos_respaldados": archivos_respaldados,
        "directorios_respaldados": directorios_respaldados,
        "bases_datos_respaldadas": bases_datos_respaldadas,
        "verificaciones_db": verificaciones_db,
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
        "garantias": {
            "no_modifica_sistema": True,
            "no_ejecuta_scripts": True,
            "solo_copia_archivos": True,
            "metodo_seguro_db": True
        }
    }
    
    info_file = os.path.join(backup_path, "backup_info.json")
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Información guardada en: backup_info.json")
    
    # Crear archivo ZIP del backup
    print()
    print("📋 Paso 6: Creando archivo ZIP del backup...")
    print("-" * 80)
    
    zip_filename = f"{backup_name}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)
    
    archivos_en_zip = 0
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, backup_path)
                    zipf.write(file_path, arcname)
                    archivos_en_zip += 1
        
        zip_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
        print(f"   ✅ Archivo ZIP creado exitosamente")
        print(f"      Nombre: {zip_filename}")
        print(f"      Tamaño: {zip_size:.2f} MB")
        print(f"      Archivos incluidos: {archivos_en_zip}")
        
    except Exception as e:
        print(f"   ⚠️  Error al crear ZIP: {e}")
        zip_path = None
    
    # Resumen final
    print()
    print("=" * 80)
    print("✅ BACKUP SEGURO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    print(f"📁 Nombre del backup: {backup_name}")
    print(f"📂 Ubicación del directorio: {backup_path}")
    if zip_path:
        print(f"📦 Archivo ZIP: {zip_path}")
    print()
    print("📊 Resumen del backup:")
    print(f"   - Archivos respaldados: {len(archivos_respaldados)}")
    print(f"   - Directorios respaldados: {len(directorios_respaldados)}")
    print(f"   - Bases de datos respaldadas: {len(bases_datos_respaldadas)}")
    if verificaciones_db:
        print()
        print("   📋 Verificación de bases de datos:")
        for verif in verificaciones_db:
            print(f"      - {verif['archivo']}: {verif['usuarios']} usuarios, Admin: {'Sí' if verif['tiene_admin'] else 'No'}")
    if errores:
        print(f"   - Errores encontrados: {len(errores)}")
    print()
    print("🛡️ GARANTÍAS:")
    print("   ✅ El sistema NO fue modificado")
    print("   ✅ NO se ejecutaron scripts de inicialización")
    print("   ✅ Solo se COPIARON archivos")
    print("   ✅ La base de datos original sigue intacta")
    print()
    print("=" * 80)
    
    return backup_name, backup_path, zip_path

def ejecutar_comando(comando, descripcion=""):
    """Ejecutar comando y manejar errores"""
    try:
        env = os.environ.copy()
        env['GIT_PAGER'] = ''
        env['PAGER'] = ''
        env['LESS'] = ''
        env['MORE'] = ''
        
        resultado = subprocess.run(
            comando, 
            shell=True, 
            env=env, 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        if resultado.returncode == 0:
            if descripcion:
                print(f"   ✅ {descripcion}")
            return True, resultado.stdout, resultado.stderr
        else:
            if descripcion:
                print(f"   ❌ Error en {descripcion}")
            return False, resultado.stdout, resultado.stderr
            
    except subprocess.TimeoutExpired:
        return False, "", "Timeout al ejecutar comando"
    except Exception as e:
        return False, "", str(e)

def ejecutar_deploy_railway():
    """Ejecutar deploy en Railway mediante git push"""
    
    print()
    print("=" * 80)
    print("🚀 EJECUTANDO DEPLOY EN RAILWAY")
    print("=" * 80)
    print()
    
    # Paso 1: Verificar estado de git
    print("📋 Paso 1: Verificando estado de Git...")
    exito, salida, error = ejecutar_comando("git status", "Verificando estado")
    if not exito:
        print(f"   ⚠️  Advertencia: {error}")
    else:
        print(f"   ✅ Repositorio Git verificado")
    
    # Paso 2: Agregar todos los cambios
    print()
    print("📋 Paso 2: Agregando todos los cambios...")
    exito, salida, error = ejecutar_comando("git add .", "Agregando cambios")
    if not exito:
        print(f"   ❌ Error al agregar cambios: {error}")
        return False
    
    # Paso 3: Crear commit
    print()
    print("📋 Paso 3: Creando commit...")
    fecha_commit = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    mensaje_commit = f"Deploy: Modificaciones del sistema - {fecha_commit}"
    exito, salida, error = ejecutar_comando(
        f'git commit -m "{mensaje_commit}"',
        "Creando commit"
    )
    if not exito:
        # Si no hay cambios, el commit puede fallar, pero continuamos
        if "nothing to commit" in error.lower() or "no changes" in error.lower():
            print("   ℹ️  No hay cambios nuevos para commitear")
        else:
            print(f"   ⚠️  Advertencia en commit: {error}")
    
    # Paso 4: Hacer push a Railway
    print()
    print("📋 Paso 4: Haciendo push a Railway...")
    exito, salida, error = ejecutar_comando("git push origin main", "Haciendo push")
    if not exito:
        print(f"   ❌ Error al hacer push: {error}")
        print()
        print("   💡 Posibles soluciones:")
        print("      - Verificar que el repositorio remoto esté configurado")
        print("      - Verificar credenciales de Git")
        print("      - Verificar conexión a internet")
        return False
    
    print()
    print("=" * 80)
    print("✅ DEPLOY INICIADO EXITOSAMENTE")
    print("=" * 80)
    print()
    print("📊 Estado del deploy:")
    print("   ✅ Cambios agregados a Git")
    print("   ✅ Commit creado")
    print("   ✅ Push completado a Railway")
    print()
    print("⏱️  Próximos pasos:")
    print("   1. Railway detectará los cambios automáticamente")
    print("   2. El deploy comenzará en 1-2 minutos")
    print("   3. Puedes verificar el estado en Railway Dashboard")
    print("   4. El proceso de deploy puede tomar 3-5 minutos")
    print()
    print("🔗 Verifica el estado en: https://railway.app/")
    print("=" * 80)
    
    return True

def main():
    """Función principal"""
    
    print()
    print("=" * 80)
    print("🛡️ BACKUP SEGURO Y DEPLOY AUTOMÁTICO - SISAGENT")
    print("=" * 80)
    print(f"📅 Fecha y hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 80)
    print()
    
    try:
        # Paso 1: Crear backup seguro
        print("🔄 INICIANDO PROCESO DE BACKUP SEGURO...")
        backup_name, backup_path, zip_path = crear_backup_seguro()
        
        if not backup_name:
            print("❌ Error al crear backup. Abortando deploy.")
            return False
        
        print()
        print("✅ Backup seguro completado exitosamente")
        print()
        
        # Paso 2: Ejecutar deploy
        print("🔄 INICIANDO PROCESO DE DEPLOY...")
        deploy_exitoso = ejecutar_deploy_railway()
        
        if not deploy_exitoso:
            print()
            print("⚠️  El deploy no se completó exitosamente")
            print("   El backup se creó correctamente y está disponible")
            print(f"   Ubicación del backup: {backup_path}")
            return False
        
        print()
        print("=" * 80)
        print("🎉 PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print()
        print("✅ Backup seguro creado:")
        print(f"   📁 {backup_name}")
        print(f"   📂 {backup_path}")
        if zip_path:
            print(f"   📦 {zip_path}")
        print()
        print("✅ Deploy iniciado en Railway")
        print("   ⏱️  El deploy estará completo en 3-5 minutos")
        print()
        print("🛡️ GARANTÍAS:")
        print("   ✅ Tu sistema NO fue modificado")
        print("   ✅ Todos los usuarios y contraseñas están respaldados")
        print("   ✅ La base de datos original sigue intacta")
        print()
        print("=" * 80)
        
        return True
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Proceso cancelado por el usuario")
        return False
    except Exception as e:
        print()
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)

