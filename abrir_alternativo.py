#!/usr/bin/env python3
"""
Script para abrir el navegador con el servidor alternativo
"""

import webbrowser
import time
import requests

def abrir_servidor_alternativo():
    """Abrir el servidor alternativo en el navegador"""
    
    print("🌐 ABRIENDO SERVIDOR ALTERNATIVO")
    print("=" * 40)
    
    url = "http://127.0.0.1:8080"
    
    # Esperar un momento para que el servidor se inicie
    print("⏳ Esperando que el servidor se inicie...")
    time.sleep(3)
    
    # Verificar si el servidor está funcionando
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Servidor alternativo funcionando correctamente")
        else:
            print(f"⚠️  Servidor responde con código: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose")
        return
    
    # Abrir navegador
    print(f"🌐 Abriendo navegador en: {url}")
    webbrowser.open(url)
    
    print("\n🎉 ¡Servidor Alternativo Listo!")
    print("📝 Características:")
    print("   - Puerto alternativo 8080")
    print("   - HTML completamente básico")
    print("   - Sin JavaScript")
    print("   - CSS simple")
    print("   - Sin dependencias complejas")
    print("\n👤 Credenciales de prueba:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("\n💡 Si esta página se mantiene visible, el problema era el puerto 5000")

if __name__ == '__main__':
    abrir_servidor_alternativo() 