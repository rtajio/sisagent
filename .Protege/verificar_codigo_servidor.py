#!/usr/bin/env python3
"""
Script para verificar si el servidor está usando el código actualizado
"""

import requests
from bs4 import BeautifulSoup
import time

def verificar_codigo_servidor():
    """Verificar si el servidor está usando el código actualizado"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 VERIFICANDO CÓDIGO DEL SERVIDOR")
    print("=" * 40)
    
    # 1. Hacer login como usuario normal
    print("1. Haciendo login como usuario normal...")
    session = requests.Session()
    
    login_data = {
        'username': '40619883',
        'password': 'password123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("   ✅ Login exitoso")
    else:
        print("   ❌ Error en login")
        return False
    
    # 2. Probar filtro por fecha anterior y verificar el HTML completo
    print(f"\n2. Probando filtro por fecha anterior (2024-01-01)...")
    response = session.get(f"{base_url}/operaciones?fecha=2024-01-01")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar mensajes de advertencia
        warnings = soup.find_all('div', class_='alert-warning')
        warning_texts = [w.get_text().strip() for w in warnings]
        
        print(f"   - Mensajes de advertencia encontrados: {len(warnings)}")
        for i, text in enumerate(warning_texts):
            print(f"     {i+1}. {text}")
        
        # Buscar cualquier mensaje flash
        flash_messages = soup.find_all('div', class_='alert')
        print(f"   - Total mensajes flash encontrados: {len(flash_messages)}")
        for i, msg in enumerate(flash_messages):
            print(f"     {i+1}. Clase: {msg.get('class', [])}")
            print(f"        Texto: {msg.get_text().strip()[:100]}...")
        
        # Verificar si hay algún mensaje sobre administradores
        all_text = soup.get_text()
        if "Solo los administradores pueden consultar operaciones de otros días" in all_text:
            print("   ✅ MENSAJE ENCONTRADO en el HTML completo")
        else:
            print("   ❌ MENSAJE NO ENCONTRADO en el HTML completo")
        
        # Verificar la URL actual
        print(f"   - URL actual: {response.url}")
        
        # Verificar si hay redirección
        if response.history:
            print(f"   - Hubo redirección de: {response.history[0].url}")
        
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    return True

if __name__ == "__main__":
    verificar_codigo_servidor() 