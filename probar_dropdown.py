#!/usr/bin/env python3
"""
Script para probar que el dropdown de sucursales funciona correctamente
"""

import requests
from bs4 import BeautifulSoup
import time

def probar_dropdown():
    """Probar que el dropdown de sucursales funciona"""
    
    base_url = "http://localhost:5000"
    session = requests.Session()
    
    print("🧪 PROBANDO DROPDOWN DE SUCURSALES")
    print("=" * 40)
    
    try:
        # 1. Ir a la página de login
        print("1. Accediendo a la página de login...")
        response = session.get(f"{base_url}/login")
        if response.status_code != 200:
            print("❌ Error: No se pudo acceder al login")
            return False
        
        # 2. Hacer login como admin
        print("2. Iniciando sesión como administrador...")
        login_data = {
            'username': 'admin',
            'password': '61442159'
        }
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code not in [200, 302]:
            print("❌ Error: No se pudo iniciar sesión")
            return False
        
        # 3. Ir a la página de registro de operaciones
        print("3. Accediendo a la página de registro de operaciones...")
        response = session.get(f"{base_url}/operaciones/registrar")
        if response.status_code != 200:
            print("❌ Error: No se pudo acceder a la página de registro")
            return False
        
        # 4. Verificar que aparece el dropdown
        soup = BeautifulSoup(response.text, 'html.parser')
        sucursal_select = soup.find('select', {'id': 'sucursal_id'})
        
        if sucursal_select:
            print("✅ ÉXITO: El dropdown de sucursales está presente")
            
            # Verificar opciones
            options = sucursal_select.find_all('option')
            print(f"📊 Total de opciones: {len(options)}")
            
            if len(options) > 1:
                print("✅ ÉXITO: Se encontraron opciones en el dropdown")
                print("📋 Opciones disponibles:")
                
                for i, option in enumerate(options):
                    value = option.get('value', '')
                    text = option.text.strip()
                    print(f"   {i+1}. Valor: '{value}' | Texto: '{text}'")
                
                # Verificar que la primera opción es vacía
                if options[0].get('value') == '':
                    print("✅ ÉXITO: La primera opción es 'Seleccione una sucursal'")
                else:
                    print("⚠️  ADVERTENCIA: La primera opción no es vacía")
                
                # Verificar que hay sucursales reales
                sucursales_reales = [opt for opt in options if opt.get('value') != '']
                if len(sucursales_reales) > 0:
                    print(f"✅ ÉXITO: Se encontraron {len(sucursales_reales)} sucursales reales")
                    return True
                else:
                    print("❌ Error: No se encontraron sucursales reales")
                    return False
            else:
                print("❌ Error: No hay suficientes opciones en el dropdown")
                return False
        else:
            print("❌ Error: No se encontró el dropdown de sucursales")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que la aplicación esté ejecutándose en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def mostrar_instrucciones():
    """Mostrar instrucciones para probar manualmente"""
    
    print("\n📋 INSTRUCCIONES PARA PRUEBA MANUAL:")
    print("=" * 40)
    print("1. Abre tu navegador web")
    print("2. Ve a: http://localhost:5000")
    print("3. Inicia sesión con:")
    print("   - Usuario: admin")
    print("   - Contraseña: 61442159")
    print("4. Ve a 'Operaciones' → 'Nueva Operación'")
    print("5. Busca el campo 'Sucursal'")
    print("6. Haz clic en el dropdown")
    print("7. Verifica que aparezcan las opciones:")
    print("   - Seleccione una sucursal")
    print("   - INC TECHNOLOGY")
    print("   - Sucursal Centro")
    print("   - Sucursal Norte")
    print("   - Sucursal Sur")
    print("   - Sucursal Este")
    print("   - Sucursal Oeste")
    print("   - Sucursal Plaza")
    print("   - Sucursal Universidad")
    print("   - Sucursal Industrial")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBA DEL DROPDOWN")
    print("=" * 40)
    
    # Esperar un momento para que el servidor esté listo
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(2)
    
    # Probar el dropdown
    success = probar_dropdown()
    
    if success:
        print("\n🎉 ¡PRUEBA EXITOSA!")
        print("El dropdown de sucursales funciona correctamente")
    else:
        print("\n❌ PRUEBA FALLIDA")
        print("El dropdown no funciona correctamente")
    
    # Mostrar instrucciones manuales
    mostrar_instrucciones() 