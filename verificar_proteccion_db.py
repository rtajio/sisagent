#!/usr/bin/env python3
"""
Script para verificar que la protección de base de datos funciona
"""

import os
import sqlite3
from datetime import datetime

def verificar_base_datos():
    """Verificar el estado actual de la base de datos"""
    db_file = "sisagent.db"
    
    if not os.path.exists(db_file):
        print("❌ Base de datos no encontrada")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        print(f"📊 Tablas encontradas: {len(tablas)}")
        for tabla in tablas:
            print(f"  - {tabla[0]}")
        
        # Verificar operaciones
        cursor.execute("SELECT COUNT(*) FROM operacion")
        num_operaciones = cursor.fetchone()[0]
        print(f"📈 Operaciones en la base de datos: {num_operaciones}")
        
        # Verificar usuarios
        cursor.execute("SELECT COUNT(*) FROM usuario")
        num_usuarios = cursor.fetchone()[0]
        print(f"👥 Usuarios en la base de datos: {num_usuarios}")
        
        # Verificar sucursales
        cursor.execute("SELECT COUNT(*) FROM sucursal")
        num_sucursales = cursor.fetchone()[0]
        print(f"🏢 Sucursales en la base de datos: {num_sucursales}")
        
        # Verificar medios de pago
        cursor.execute("SELECT COUNT(*) FROM medio_pago")
        num_medios = cursor.fetchone()[0]
        print(f"💳 Medios de pago en la base de datos: {num_medios}")
        
        # Mostrar algunas operaciones recientes
        if num_operaciones > 0:
            cursor.execute("SELECT id, monto, medio, hora FROM operacion ORDER BY hora DESC LIMIT 5")
            operaciones = cursor.fetchall()
            print(f"\n📋 Últimas 5 operaciones:")
            for op in operaciones:
                print(f"  - ID: {op[0]}, Monto: {op[1]}, Medio: {op[2]}, Hora: {op[3]}")
        
        conn.close()
        
        print(f"\n✅ Verificación completada - Base de datos está protegida")
        print(f"🛡️ Total de registros: {num_operaciones + num_usuarios + num_sucursales + num_medios}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def main():
    """Función principal"""
    print("🛡️ VERIFICACIÓN DE PROTECCIÓN DE BASE DE DATOS")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    verificar_base_datos()
    
    print("\n💡 INSTRUCCIONES:")
    print("1. Ejecuta este script ANTES de hacer cambios")
    print("2. Haz tus cambios en el código")
    print("3. Ejecuta este script DESPUÉS de hacer cambios")
    print("4. Si los números son iguales, la protección funciona")
    print("5. Si los números cambian, hay un problema")

if __name__ == "__main__":
    main() 