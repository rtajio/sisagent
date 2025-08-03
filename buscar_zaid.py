#!/usr/bin/env python3
"""
Buscar usuario Zaid rápidamente
"""

import sqlite3

def buscar_zaid():
    """Buscar usuario Zaid en la base de datos"""
    
    print("🔍 Buscando usuario Zaid...")
    
    try:
        conn = sqlite3.connect('instance/sisagent_consolidada.db')
        cursor = conn.cursor()
        
        # Buscar por nombre
        cursor.execute("SELECT id, username, nombre_completo, email FROM usuario WHERE nombre_completo LIKE '%Zaid%'")
        usuarios_nombre = cursor.fetchall()
        
        # Buscar por username
        cursor.execute("SELECT id, username, nombre_completo, email FROM usuario WHERE username LIKE '%Zaid%'")
        usuarios_username = cursor.fetchall()
        
        print(f"Usuarios encontrados por nombre: {len(usuarios_nombre)}")
        for u in usuarios_nombre:
            print(f"  - {u[0]}: {u[1]} - {u[2]} - {u[3]}")
        
        print(f"Usuarios encontrados por username: {len(usuarios_username)}")
        for u in usuarios_username:
            print(f"  - {u[0]}: {u[1]} - {u[2]} - {u[3]}")
        
        # Mostrar todos los usuarios para verificar
        cursor.execute("SELECT id, username, nombre_completo FROM usuario ORDER BY id")
        todos = cursor.fetchall()
        print(f"\nTodos los usuarios ({len(todos)}):")
        for u in todos:
            print(f"  {u[0]}: {u[1]} - {u[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    buscar_zaid() 