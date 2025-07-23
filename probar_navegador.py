#!/usr/bin/env python3
"""
Script para probar diferentes navegadores y limpiar cache
"""

import webbrowser
import time
import os

def probar_navegadores():
    """Probar diferentes navegadores"""
    
    print("🌐 PROBANDO DIFERENTES NAVEGADORES")
    print("=" * 40)
    
    url = "http://127.0.0.1:5000/login"
    
    # Lista de navegadores a probar
    navegadores = [
        ('chrome', 'Google Chrome'),
        ('firefox', 'Mozilla Firefox'),
        ('edge', 'Microsoft Edge'),
        ('safari', 'Safari'),
        ('opera', 'Opera')
    ]
    
    for navegador, nombre in navegadores:
        try:
            print(f"\n1. Probando {nombre}...")
            webbrowser.get(navegador).open(url)
            print(f"   ✅ {nombre} abierto")
            time.sleep(2)  # Esperar 2 segundos entre navegadores
            
        except Exception as e:
            print(f"   ❌ Error con {nombre}: {e}")
    
    print("\n🎯 INSTRUCCIONES PARA EL USUARIO:")
    print("1. Si la página aparece en blanco, intenta:")
    print("   - Presionar Ctrl+F5 para forzar recarga")
    print("   - Presionar Ctrl+Shift+R para recarga sin cache")
    print("   - Abrir las herramientas de desarrollador (F12)")
    print("   - Ir a la pestaña 'Network' y marcar 'Disable cache'")
    print("   - Recargar la página")
    print("\n2. Si sigue en blanco, verifica:")
    print("   - Que no haya bloqueadores de anuncios activos")
    print("   - Que JavaScript esté habilitado")
    print("   - Que no haya extensiones interfiriendo")
    print("\n3. Credenciales de prueba:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")

def limpiar_cache_navegador():
    """Instrucciones para limpiar cache"""
    
    print("\n🧹 INSTRUCCIONES PARA LIMPIAR CACHE")
    print("=" * 40)
    
    print("Chrome/Edge:")
    print("1. Presiona Ctrl+Shift+Delete")
    print("2. Selecciona 'Todo el tiempo'")
    print("3. Marca 'Imágenes y archivos en caché'")
    print("4. Haz clic en 'Borrar datos'")
    
    print("\nFirefox:")
    print("1. Presiona Ctrl+Shift+Delete")
    print("2. Selecciona 'Todo' en el rango de tiempo")
    print("3. Marca 'Caché'")
    print("4. Haz clic en 'Limpiar ahora'")
    
    print("\nSafari:")
    print("1. Ve a Safari > Preferencias > Avanzado")
    print("2. Marca 'Mostrar menú Desarrollo'")
    print("3. Ve a Desarrollo > Vaciar cachés")

if __name__ == "__main__":
    probar_navegadores()
    limpiar_cache_navegador() 