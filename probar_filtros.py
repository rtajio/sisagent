#!/usr/bin/env python3
"""
Script para probar que los filtros funcionan correctamente
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

def probar_filtros():
    """Probar los filtros de operaciones"""
    
    base_url = "http://localhost:5000"
    peru_tz = pytz.timezone('America/Lima')
    hoy = datetime.now(peru_tz).strftime('%Y-%m-%d')
    
    print("🧪 PROBANDO FILTROS DE OPERACIONES")
    print("=" * 40)
    
    # 1. Hacer login como usuario normal
    print("1. Haciendo login como usuario normal...")
    session = requests.Session()
    
    login_data = {
        'username': 'usuario1',
        'password': 'password123'
    }
    
    response = session.post(f"{base_url}/login", data=login_data)
    if response.status_code == 200:
        print("   ✅ Login exitoso")
    else:
        print("   ❌ Error en login")
        return False
    
    # 2. Probar filtro por medio (NO debería mostrar advertencia)
    print(f"\n2. Probando filtro por medio 'BCP'...")
    response = session.get(f"{base_url}/operaciones?medio=BCP")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar mensajes de advertencia
        warnings = soup.find_all('div', class_='alert-warning')
        warning_texts = [w.get_text().strip() for w in warnings]
        
        if any("Solo los administradores pueden consultar operaciones de otros días" in text for text in warning_texts):
            print("   ❌ ERROR: Se muestra advertencia innecesaria al filtrar por medio")
            return False
        else:
            print("   ✅ Correcto: No se muestra advertencia al filtrar por medio")
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    # 3. Probar filtro por fecha actual (NO debería mostrar advertencia)
    print(f"\n3. Probando filtro por fecha actual ({hoy})...")
    response = session.get(f"{base_url}/operaciones?fecha={hoy}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar mensajes de advertencia
        warnings = soup.find_all('div', class_='alert-warning')
        warning_texts = [w.get_text().strip() for w in warnings]
        
        if any("Solo los administradores pueden consultar operaciones de otros días" in text for text in warning_texts):
            print("   ❌ ERROR: Se muestra advertencia innecesaria al filtrar por fecha actual")
            return False
        else:
            print("   ✅ Correcto: No se muestra advertencia al filtrar por fecha actual")
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    # 4. Probar filtro por fecha anterior (SÍ debería mostrar advertencia)
    print(f"\n4. Probando filtro por fecha anterior (2024-01-01)...")
    response = session.get(f"{base_url}/operaciones?fecha=2024-01-01")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar mensajes de advertencia
        warnings = soup.find_all('div', class_='alert-warning')
        warning_texts = [w.get_text().strip() for w in warnings]
        
        if any("Solo los administradores pueden consultar operaciones de otros días" in text for text in warning_texts):
            print("   ✅ Correcto: Se muestra advertencia al intentar consultar fecha anterior")
        else:
            print("   ❌ ERROR: No se muestra advertencia al intentar consultar fecha anterior")
            return False
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    # 5. Probar filtro por hora (NO debería mostrar advertencia)
    print(f"\n5. Probando filtro por hora...")
    response = session.get(f"{base_url}/operaciones?hora_inicio=08:00&hora_fin=18:00")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar mensajes de advertencia
        warnings = soup.find_all('div', class_='alert-warning')
        warning_texts = [w.get_text().strip() for w in warnings]
        
        if any("Solo los administradores pueden consultar operaciones de otros días" in text for text in warning_texts):
            print("   ❌ ERROR: Se muestra advertencia innecesaria al filtrar por hora")
            return False
        else:
            print("   ✅ Correcto: No se muestra advertencia al filtrar por hora")
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    print(f"\n🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    print("La corrección funciona correctamente.")
    return True

if __name__ == "__main__":
    probar_filtros() 