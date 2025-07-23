#!/usr/bin/env python3
"""
Script para verificar el estado actual del servidor
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def verificar_servidor():
    """Verificar el estado del servidor"""
    
    base_url = "http://localhost:5000"
    peru_tz = pytz.timezone('America/Lima')
    hoy = datetime.now(peru_tz).strftime('%Y-%m-%d')
    
    print("🔍 VERIFICANDO ESTADO DEL SERVIDOR")
    print("=" * 40)
    
    # 1. Verificar si el servidor está funcionando
    try:
        response = requests.get(f"{base_url}/login", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está funcionando")
        else:
            print(f"❌ Servidor responde con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al servidor: {e}")
        return False
    
    # 2. Hacer login como usuario normal
    print("\n2. Haciendo login como usuario normal...")
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
    
    # 3. Verificar página de operaciones sin filtros
    print(f"\n3. Verificando página de operaciones sin filtros...")
    response = session.get(f"{base_url}/operaciones")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar mensajes de advertencia
        warnings = soup.find_all('div', class_='alert-warning')
        warning_texts = [w.get_text().strip() for w in warnings]
        
        print(f"   - Mensajes de advertencia encontrados: {len(warnings)}")
        for i, text in enumerate(warning_texts):
            print(f"     {i+1}. {text[:100]}...")
        
        if any("Solo los administradores pueden consultar operaciones de otros días" in text for text in warning_texts):
            print("   ❌ ERROR: Se muestra advertencia innecesaria")
        else:
            print("   ✅ Correcto: No se muestra advertencia innecesaria")
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    # 4. Verificar filtro por medio
    print(f"\n4. Verificando filtro por medio 'BCP'...")
    response = session.get(f"{base_url}/operaciones?medio=BCP")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar mensajes de advertencia
        warnings = soup.find_all('div', class_='alert-warning')
        warning_texts = [w.get_text().strip() for w in warnings]
        
        print(f"   - Mensajes de advertencia encontrados: {len(warnings)}")
        for i, text in enumerate(warning_texts):
            print(f"     {i+1}. {text[:100]}...")
        
        if any("Solo los administradores pueden consultar operaciones de otros días" in text for text in warning_texts):
            print("   ❌ ERROR: Se muestra advertencia innecesaria al filtrar por medio")
        else:
            print("   ✅ Correcto: No se muestra advertencia al filtrar por medio")
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    # 5. Verificar filtro por fecha anterior
    print(f"\n5. Verificando filtro por fecha anterior (2024-01-01)...")
    response = session.get(f"{base_url}/operaciones?fecha=2024-01-01")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar mensajes de advertencia
        warnings = soup.find_all('div', class_='alert-warning')
        warning_texts = [w.get_text().strip() for w in warnings]
        
        print(f"   - Mensajes de advertencia encontrados: {len(warnings)}")
        for i, text in enumerate(warning_texts):
            print(f"     {i+1}. {text[:100]}...")
        
        if any("Solo los administradores pueden consultar operaciones de otros días" in text for text in warning_texts):
            print("   ✅ Correcto: Se muestra advertencia al intentar consultar fecha anterior")
        else:
            print("   ❌ ERROR: No se muestra advertencia al intentar consultar fecha anterior")
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    return True

if __name__ == "__main__":
    verificar_servidor() 