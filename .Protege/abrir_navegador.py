#!/usr/bin/env python3
"""
Script para abrir el navegador con el servidor simple
"""

import webbrowser
import time
import subprocess
import sys
import os

def abrir_servidor_simple():
    """Abrir el servidor simple en el navegador"""
    
    print("🚀 INICIANDO SERVIDOR SIMPLE")
    print("=" * 40)
    
    # Verificar si el servidor simple está ejecutándose
    try:
        import requests
        response = requests.get("http://127.0.0.1:5000", timeout=2)
        if response.status_code == 200:
            print("✅ Servidor ya está ejecutándose")
        else:
            print("⚠️  Servidor no responde correctamente")
            return False
    except:
        print("❌ Servidor no está ejecutándose")
        print("💡 Ejecutando servidor simple...")
        
        # Ejecutar el servidor simple en segundo plano
        try:
            subprocess.Popen([sys.executable, "login_directo.py"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            print("✅ Servidor iniciado")
            time.sleep(3)  # Esperar a que inicie
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
            return False
    
    # Abrir navegador
    url = "http://127.0.0.1:5000/login"
    print(f"\n🌐 Abriendo navegador en: {url}")
    
    try:
        webbrowser.open(url)
        print("✅ Navegador abierto")
    except Exception as e:
        print(f"❌ Error abriendo navegador: {e}")
        print(f"💡 Abre manualmente: {url}")
    
    print("\n🎯 INSTRUCCIONES:")
    print("1. Si la página aparece en blanco:")
    print("   - Presiona Ctrl+F5 para forzar recarga")
    print("   - Presiona Ctrl+Shift+R para recarga sin cache")
    print("   - Usa modo incógnito/privado")
    
    print("\n2. Credenciales de prueba:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    
    print("\n3. Si sigue en blanco:")
    print("   - Verifica que no haya bloqueadores de anuncios")
    print("   - Asegúrate de que JavaScript esté habilitado")
    print("   - Desactiva temporalmente las extensiones")
    
    return True

if __name__ == "__main__":
    abrir_servidor_simple() 