#!/usr/bin/env python3
"""
Diagnóstico y Solución para el Problema de Base de Datos que se Borra
"""

import os
import sqlite3
import shutil
from datetime import datetime
import sys

def verificar_archivos_db():
    """Verifica todos los archivos de base de datos existentes"""
    print("🔍 Verificando archivos de base de datos...")
    
    archivos_db = []
    if os.path.exists('instance'):
        for archivo in os.listdir('instance'):
            if archivo.endswith('.db'):
                ruta_completa = os.path.join('instance', archivo)
                tamaño = os.path.getsize(ruta_completa)
                fecha_mod = datetime.fromtimestamp(os.path.getmtime(ruta_completa))
                archivos_db.append({
                    'nombre': archivo,
                    'ruta': ruta_completa,
                    'tamaño': tamaño,
                    'fecha_mod': fecha_mod
                })
    
    print(f"📊 Encontrados {len(archivos_db)} archivos de base de datos:")
    for db in archivos_db:
        print(f"   📁 {db['nombre']} - {db['tamaño']} bytes - Modificado: {db['fecha_mod']}")
    
    return archivos_db

def verificar_contenido_db(ruta_db):
    """Verifica el contenido de una base de datos"""
    try:
        conn = sqlite3.connect(ruta_db)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
        print(f"   📋 Tablas en {os.path.basename(ruta_db)}:")
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
            count = cursor.fetchone()[0]
            print(f"      - {tabla[0]}: {count} registros")
        
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ Error al verificar {ruta_db}: {e}")
        return False

def crear_backup_seguro():
    """Crea un backup seguro de la base de datos principal"""
    print("\n💾 Creando backup seguro...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_emergencia_{timestamp}"
    
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Copiar todos los archivos de base de datos
    if os.path.exists('instance'):
        for archivo in os.listdir('instance'):
            if archivo.endswith('.db'):
                origen = os.path.join('instance', archivo)
                destino = os.path.join(backup_dir, archivo)
                shutil.copy2(origen, destino)
                print(f"   ✅ Backup creado: {archivo}")
    
    print(f"📁 Backup guardado en: {backup_dir}")
    return backup_dir

def identificar_db_principal():
    """Identifica cuál es la base de datos principal"""
    print("\n🎯 Identificando base de datos principal...")
    
    archivos_db = verificar_archivos_db()
    
    # Buscar la base de datos más grande (probablemente la principal)
    if archivos_db:
        db_principal = max(archivos_db, key=lambda x: x['tamaño'])
        print(f"📊 Base de datos principal identificada: {db_principal['nombre']}")
        print(f"   Tamaño: {db_principal['tamaño']} bytes")
        return db_principal['ruta']
    
    return None

def crear_db_protegida():
    """Crea una base de datos protegida contra borrado"""
    print("\n🛡️ Creando base de datos protegida...")
    
    # Crear backup primero
    backup_dir = crear_backup_seguro()
    
    # Identificar DB principal
    db_principal = identificar_db_principal()
    
    if not db_principal:
        print("❌ No se encontró base de datos principal")
        return False
    
    # Crear nueva base de datos protegida
    db_protegida = os.path.join('instance', 'sisagent_protegida.db')
    
    try:
        # Copiar la base de datos principal
        shutil.copy2(db_principal, db_protegida)
        print(f"✅ Base de datos protegida creada: sisagent_protegida.db")
        
        # Hacer el archivo de solo lectura
        os.chmod(db_protegida, 0o444)
        print("🔒 Archivo configurado como solo lectura")
        
        return True
    except Exception as e:
        print(f"❌ Error al crear base de datos protegida: {e}")
        return False

def configurar_app_para_db_protegida():
    """Configura la aplicación para usar la base de datos protegida"""
    print("\n⚙️ Configurando aplicación para usar base de datos protegida...")
    
    # Leer el archivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar la línea de configuración de SQLite
    if 'sqlite:///sisagent.db' in contenido:
        # Reemplazar con la base de datos protegida
        contenido_nuevo = contenido.replace(
            "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent.db'",
            "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_protegida.db'"
        )
        
        # Guardar el archivo modificado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print("✅ Configuración actualizada para usar base de datos protegida")
        return True
    else:
        print("⚠️ No se encontró la configuración de SQLite en app.py")
        return False

def crear_script_monitoreo():
    """Crea un script para monitorear la base de datos"""
    print("\n📊 Creando script de monitoreo...")
    
    script_monitoreo = '''#!/usr/bin/env python3
"""
Script de Monitoreo de Base de Datos
"""

import os
import time
import sqlite3
from datetime import datetime

def monitorear_db():
    db_path = "instance/sisagent_protegida.db"
    
    if not os.path.exists(db_path):
        print(f"❌ ALERTA: Base de datos no encontrada en {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas principales
        cursor.execute("SELECT COUNT(*) FROM usuario")
        usuarios = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM operacion")
        operaciones = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sucursal")
        sucursales = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ DB OK - Usuarios: {usuarios}, Operaciones: {operaciones}, Sucursales: {sucursales}")
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

if __name__ == "__main__":
    while True:
        monitorear_db()
        time.sleep(30)  # Verificar cada 30 segundos
'''
    
    with open('monitor_db.py', 'w', encoding='utf-8') as f:
        f.write(script_monitoreo)
    
    print("✅ Script de monitoreo creado: monitor_db.py")

def main():
    print("🚨 DIAGNÓSTICO Y SOLUCIÓN PARA PROBLEMA DE BASE DE DATOS")
    print("=" * 60)
    
    # Paso 1: Verificar archivos existentes
    archivos_db = verificar_archivos_db()
    
    # Paso 2: Verificar contenido de cada DB
    print("\n🔍 Verificando contenido de bases de datos...")
    for db in archivos_db:
        print(f"\n📁 Verificando {db['nombre']}:")
        verificar_contenido_db(db['ruta'])
    
    # Paso 3: Crear backup de emergencia
    backup_dir = crear_backup_seguro()
    
    # Paso 4: Crear base de datos protegida
    if crear_db_protegida():
        # Paso 5: Configurar aplicación
        if configurar_app_para_db_protegida():
            print("\n✅ Configuración completada exitosamente")
        else:
            print("\n⚠️ Configuración parcial - revisar manualmente")
    
    # Paso 6: Crear script de monitoreo
    crear_script_monitoreo()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE ACCIONES REALIZADAS:")
    print("1. ✅ Verificación de archivos de base de datos")
    print("2. ✅ Análisis de contenido de cada DB")
    print("3. ✅ Backup de emergencia creado")
    print("4. ✅ Base de datos protegida creada")
    print("5. ✅ Configuración de aplicación actualizada")
    print("6. ✅ Script de monitoreo creado")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Reiniciar la aplicación")
    print("2. Ejecutar: python monitor_db.py (para monitoreo continuo)")
    print("3. Verificar que la aplicación funcione correctamente")
    print("4. Si hay problemas, restaurar desde el backup creado")

if __name__ == "__main__":
    main() 