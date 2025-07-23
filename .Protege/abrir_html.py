#!/usr/bin/env python3
"""
Script para abrir el archivo HTML estático directamente
"""

import webbrowser
import os

def abrir_html_estatico():
    """Abrir el archivo HTML estático directamente"""
    
    print("🌐 ABRIENDO ARCHIVO HTML ESTÁTICO")
    print("=" * 40)
    
    # Obtener la ruta absoluta del archivo HTML
    current_dir = os.getcwd()
    html_file = os.path.join(current_dir, 'login.html')
    
    # Verificar que el archivo existe
    if not os.path.exists(html_file):
        print(f"❌ Error: No se encuentra el archivo {html_file}")
        return
    
    # Convertir a URL de archivo
    file_url = f"file:///{html_file.replace(os.sep, '/')}"
    
    print(f"📁 Archivo HTML: {html_file}")
    print(f"🌐 URL: {file_url}")
    
    # Abrir navegador
    print("🌐 Abriendo navegador...")
    webbrowser.open(file_url)
    
    print("\n🎉 ¡Archivo HTML Estático Abierto!")
    print("📝 Características:")
    print("   - Archivo HTML completamente estático")
    print("   - Sin servidor web")
    print("   - Sin dependencias externas")
    print("   - JavaScript simple para login")
    print("   - CSS embebido")
    print("\n👤 Credenciales de prueba:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("\n💡 Si esta página se mantiene visible, el problema era el servidor web")

if __name__ == '__main__':
    abrir_html_estatico() 