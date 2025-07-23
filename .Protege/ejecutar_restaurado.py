#!/usr/bin/env python3
"""
Script para ejecutar la versión restaurada de SISAGENT
"""

import webbrowser
import time
import subprocess
import sys
import os

def ejecutar_restaurado():
    """Ejecutar la versión restaurada de SISAGENT"""
    
    print("RESTAURANDO SISAGENT - VERSION FUNCIONAL")
    print("=" * 50)
    
    # Verificar que el archivo existe
    app_file = 'app_restaurado.py'
    if not os.path.exists(app_file):
        print(f"Error: No se encuentra el archivo {app_file}")
        return
    
    print(f"Archivo: {app_file}")
    print("Iniciando servidor Flask restaurado...")
    
    try:
        # Iniciar el servidor Flask en segundo plano
        process = subprocess.Popen([sys.executable, app_file], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Esperar un momento para que el servidor se inicie
        print("Esperando que el servidor se inicie...")
        time.sleep(5)
        
        # Verificar si el proceso sigue ejecutándose
        if process.poll() is None:
            print("Servidor Flask restaurado iniciado correctamente")
            
            # Abrir navegador
            print("Abriendo navegador...")
            webbrowser.open('http://127.0.0.1:5000')
            
            print("\nSISAGENT RESTAURADO Y FUNCIONANDO!")
            print("Caracteristicas:")
            print("   - Version restaurada y funcional")
            print("   - Base de datos SQLite")
            print("   - Mejoras en UI mantenidas")
            print("   - Notificaciones funcionando")
            print("   - Boton 'Nueva Operacion' reposicionado")
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
            print("Error al iniciar el servidor Flask restaurado:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    ejecutar_restaurado() 