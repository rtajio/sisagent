#!/usr/bin/env python3
"""
Script para abrir el navegador con el servidor estático
"""

import webbrowser
import time
import requests

def abrir_servidor_estatico():
    """Abrir el servidor estático en el navegador"""
    
    print("🌐 ABRIENDO SERVIDOR ESTÁTICO")
    print("=" * 40)
    
    url = "http://127.0.0.1:5000"
    
    # Esperar un momento para que el servidor se inicie
    print("⏳ Esperando que el servidor se inicie...")
    time.sleep(3)
    
    # Verificar si el servidor está funcionando
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ Servidor estático funcionando correctamente")
        else:
            print(f"⚠️  Servidor responde con código: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando al servidor: {e}")
        print("💡 Asegúrate de que el servidor esté ejecutándose")
        return
    
    # Abrir navegador
    print(f"🌐 Abriendo navegador en: {url}")
    webbrowser.open(url)
    
    print("\n🎉 ¡Servidor Estático Listo!")
    print("📝 Características:")
    print("   - Sin JavaScript (no causa problemas de carga)")
    print("   - CSS simple y directo")
    print("   - HTML completamente estático")
    print("   - No hay animaciones que puedan fallar")
    print("\n👤 Credenciales de prueba:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("\n💡 Si la página se mantiene visible, el problema era JavaScript")

if __name__ == '__main__':
    abrir_servidor_estatico() 