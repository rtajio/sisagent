#!/usr/bin/env python3
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
