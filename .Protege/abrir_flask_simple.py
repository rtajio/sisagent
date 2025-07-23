#!/usr/bin/env python3
"""
Script para abrir el servidor Flask simple
"""

import webbrowser
import time
import subprocess
import sys
import os

def abrir_flask_simple():
    """Abrir el servidor Flask simple"""
    
    print("ABRIENDO SERVIDOR FLASK SIMPLE")
    print("=" * 40)
    
    # Verificar que el archivo existe
    flask_file = 'servidor_flask_simple.py'
    if not os.path.exists(flask_file):
        print(f"Error: No se encuentra el archivo {flask_file}")
        return
    
    print(f"Archivo Flask: {flask_file}")
    print("Iniciando servidor Flask...")
    
    try:
        # Iniciar el servidor Flask en segundo plano
        process = subprocess.Popen([sys.executable, flask_file], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Esperar un momento para que el servidor se inicie
        print("Esperando que el servidor se inicie...")
        time.sleep(3)
        
        # Verificar si el proceso sigue ejecutándose
        if process.poll() is None:
            print("Servidor Flask iniciado correctamente")
            
            # Abrir navegador
            print("Abriendo navegador...")
            webbrowser.open('http://127.0.0.1:5000')
            
            print("\nServidor Flask Simple Abierto!")
            print("Caracteristicas:")
            print("   - Servidor Flask funcional")
            print("   - HTML embebido en Python")
            print("   - Base de datos SQLite")
            print("   - Sin dependencias externas de templates")
            print("   - Login funcional con base de datos")
            print("   - Dashboard con estadisticas")
            print("\nCredenciales de prueba:")
            print("   - Admin: admin / admin123")
            print("   - Usuario: usuario1 / password123")
            print("\nSi esta pagina se mantiene visible, el problema esta resuelto")
            print("Presiona Ctrl+C en la terminal para detener el servidor")
            
            # Mantener el proceso ejecutándose
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\nDeteniendo servidor...")
                process.terminate()
                process.wait()
                print("Servidor detenido")
                
        else:
            # El proceso terminó prematuramente
            stdout, stderr = process.communicate()
            print("Error al iniciar el servidor Flask:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    abrir_flask_simple() 