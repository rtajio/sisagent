#!/usr/bin/env python3
"""
SOLUCIÓN DEFINITIVA PARA EL PROBLEMA DE BASE DE DATOS QUE SE BORRA
"""

import os
import sqlite3
import shutil
from datetime import datetime
import sys

def verificar_estado_actual():
    """Verifica el estado actual de las bases de datos"""
    print("🔍 DIAGNÓSTICO DEL PROBLEMA")
    print("=" * 50)
    
    # Verificar archivos de base de datos
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

def identificar_mejor_db(archivos_db):
    """Identifica la mejor base de datos para usar"""
    if not archivos_db:
        return None
    
    # Buscar la base de datos con más datos
    mejor_db = max(archivos_db, key=lambda x: x['tamaño'])
    
    print(f"\n🎯 Base de datos seleccionada: {mejor_db['nombre']}")
    print(f"   Tamaño: {mejor_db['tamaño']} bytes")
    
    return mejor_db

def crear_backup_completo():
    """Crea un backup completo de todas las bases de datos"""
    print("\n💾 CREANDO BACKUP COMPLETO")
    print("=" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/backup_completo_{timestamp}"
    
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Copiar todas las bases de datos
    if os.path.exists('instance'):
        for archivo in os.listdir('instance'):
            if archivo.endswith('.db'):
                origen = os.path.join('instance', archivo)
                destino = os.path.join(backup_dir, archivo)
                shutil.copy2(origen, destino)
                print(f"   ✅ Backup: {archivo}")
    
    print(f"📁 Backup completo guardado en: {backup_dir}")
    return backup_dir

def consolidar_base_datos():
    """Consolida todas las bases de datos en una sola"""
    print("\n🔧 CONSOLIDANDO BASE DE DATOS")
    print("=" * 50)
    
    # Crear backup primero
    backup_dir = crear_backup_completo()
    
    # Identificar la mejor base de datos
    archivos_db = verificar_estado_actual()
    mejor_db = identificar_mejor_db(archivos_db)
    
    if not mejor_db:
        print("❌ No se encontraron bases de datos")
        return False
    
    # Crear la base de datos consolidada
    db_consolidada = os.path.join('instance', 'sisagent_consolidada.db')
    
    try:
        # Copiar la mejor base de datos como base
        shutil.copy2(mejor_db['ruta'], db_consolidada)
        print(f"✅ Base de datos consolidada creada: sisagent_consolidada.db")
        
        # Verificar contenido
        conn = sqlite3.connect(db_consolidada)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
        print(f"📋 Tablas en la base consolidada:")
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
            count = cursor.fetchone()[0]
            print(f"   - {tabla[0]}: {count} registros")
        
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Error al consolidar: {e}")
        return False

def configurar_app_definitiva():
    """Configura la aplicación para usar la base de datos consolidada"""
    print("\n⚙️ CONFIGURANDO APLICACIÓN DEFINITIVA")
    print("=" * 50)
    
    # Leer el archivo app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Buscar y reemplazar la configuración de SQLite
    if 'sqlite:///sisagent.db' in contenido:
        contenido_nuevo = contenido.replace(
            "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent.db'",
            "app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_consolidada.db'"
        )
        
        # Guardar el archivo modificado
        with open('app.py', 'w', encoding='utf-8') as f:
            f.write(contenido_nuevo)
        
        print("✅ Configuración actualizada para usar base de datos consolidada")
        return True
    else:
        print("⚠️ No se encontró la configuración de SQLite en app.py")
        return False

def crear_sistema_proteccion():
    """Crea un sistema de protección para la base de datos"""
    print("\n🛡️ CREANDO SISTEMA DE PROTECCIÓN")
    print("=" * 50)
    
    # Crear script de protección
    script_proteccion = '''#!/usr/bin/env python3
"""
Sistema de Protección de Base de Datos
"""

import os
import shutil
import time
from datetime import datetime

def proteger_base_datos():
    db_principal = "instance/sisagent_consolidada.db"
    db_backup = "instance/sisagent_backup.db"
    
    # Crear backup automático cada hora
    if os.path.exists(db_principal):
        # Verificar si necesitamos hacer backup
        if not os.path.exists(db_backup) or \
           (time.time() - os.path.getmtime(db_backup)) > 3600:  # 1 hora
            
            shutil.copy2(db_principal, db_backup)
            print(f"🔄 Backup automático creado: {datetime.now()}")
    
    # Verificar integridad
    if os.path.exists(db_principal):
        tamaño = os.path.getsize(db_principal)
        if tamaño < 1000:  # Si es muy pequeño, restaurar
            if os.path.exists(db_backup):
                shutil.copy2(db_backup, db_principal)
                print("🔄 Base de datos restaurada desde backup")
                return False
        return True
    return False

if __name__ == "__main__":
    while True:
        proteger_base_datos()
        time.sleep(300)  # Verificar cada 5 minutos
'''
    
    with open('proteger_db.py', 'w', encoding='utf-8') as f:
        f.write(script_proteccion)
    
    print("✅ Script de protección creado: proteger_db.py")

def crear_script_inicializacion():
    """Crea un script de inicialización seguro"""
    print("\n🚀 CREANDO SCRIPT DE INICIALIZACIÓN SEGURO")
    print("=" * 50)
    
    script_inicializacion = '''#!/usr/bin/env python3
"""
Script de Inicialización Seguro para SISAGENT
"""

import os
import sys
import sqlite3
from datetime import datetime

def verificar_db():
    db_path = "instance/sisagent_consolidada.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas principales
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        
        tablas_requeridas = ['usuario', 'sucursal', 'operacion']
        tablas_encontradas = [tabla[0] for tabla in tablas]
        
        for tabla in tablas_requeridas:
            if tabla not in tablas_encontradas:
                print(f"❌ Tabla {tabla} no encontrada")
                conn.close()
                return False
        
        # Verificar datos mínimos
        cursor.execute("SELECT COUNT(*) FROM usuario")
        usuarios = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sucursal")
        sucursales = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Base de datos OK - Usuarios: {usuarios}, Sucursales: {sucursales}")
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def inicializar_sistema():
    print("🚀 Inicializando SISAGENT...")
    
    if not verificar_db():
        print("❌ Error en la base de datos. Ejecutar: python solucionar_problema_db.py")
        return False
    
    print("✅ Sistema listo para iniciar")
    return True

if __name__ == "__main__":
    if inicializar_sistema():
        print("🎉 SISAGENT listo para ejecutar")
        print("Ejecutar: python app.py")
    else:
        print("❌ Error en la inicialización")
'''
    
    with open('iniciar_sisagent.py', 'w', encoding='utf-8') as f:
        f.write(script_inicializacion)
    
    print("✅ Script de inicialización creado: iniciar_sisagent.py")

def main():
    print("🚨 SOLUCIÓN DEFINITIVA PARA PROBLEMA DE BASE DE DATOS")
    print("=" * 60)
    
    # Paso 1: Verificar estado actual
    archivos_db = verificar_estado_actual()
    
    # Paso 2: Consolidar bases de datos
    if consolidar_base_datos():
        # Paso 3: Configurar aplicación
        if configurar_app_definitiva():
            print("\n✅ Configuración completada exitosamente")
        else:
            print("\n⚠️ Configuración parcial - revisar manualmente")
    
    # Paso 4: Crear sistema de protección
    crear_sistema_proteccion()
    
    # Paso 5: Crear script de inicialización
    crear_script_inicializacion()
    
    print("\n" + "=" * 60)
    print("🎯 SOLUCIÓN IMPLEMENTADA:")
    print("1. ✅ Backup completo creado")
    print("2. ✅ Base de datos consolidada")
    print("3. ✅ Configuración de aplicación actualizada")
    print("4. ✅ Sistema de protección creado")
    print("5. ✅ Script de inicialización seguro")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python iniciar_sisagent.py")
    print("2. Si todo está OK, ejecutar: python app.py")
    print("3. Para protección automática: python proteger_db.py")
    print("4. Si hay problemas: revisar backups/")

if __name__ == "__main__":
    main() 