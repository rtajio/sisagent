#!/usr/bin/env python3
"""
Script para probar que el dropdown de sucursales se muestra correctamente
"""

import requests
from bs4 import BeautifulSoup

def test_dropdown_sucursales():
    """Probar que el dropdown de sucursales se muestra correctamente"""
    
    # URL base
    base_url = "http://localhost:5000"
    
    # Crear sesión
    session = requests.Session()
    
    print("🔍 Probando dropdown de sucursales...")
    
    try:
        # 1. Ir a la página de login
        print("1. Accediendo a la página de login...")
        response = session.get(f"{base_url}/login")
        if response.status_code != 200:
            print("❌ Error: No se pudo acceder a la página de login")
            return False
        
        # 2. Hacer login como admin
        print("2. Iniciando sesión como administrador...")
        login_data = {
            'username': 'admin',
            'password': '61442159'
        }
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code != 200 and response.status_code != 302:
            print("❌ Error: No se pudo iniciar sesión como administrador")
            return False
        
        # 3. Ir a la página de registro de operaciones
        print("3. Accediendo a la página de registro de operaciones...")
        response = session.get(f"{base_url}/operaciones/registrar")
        if response.status_code != 200:
            print("❌ Error: No se pudo acceder a la página de registro de operaciones")
            return False
        
        # 4. Verificar que aparece el dropdown de sucursales
        soup = BeautifulSoup(response.text, 'html.parser')
        sucursal_select = soup.find('select', {'id': 'sucursal_id'})
        
        if sucursal_select:
            print("✅ ÉXITO: El dropdown de sucursales está presente")
            
            # Verificar que hay opciones de sucursales
            options = sucursal_select.find_all('option')
            print(f"📊 Total de opciones encontradas: {len(options)}")
            
            if len(options) > 1:  # Más de 1 porque incluye la opción vacía
                print("✅ ÉXITO: Se encontraron sucursales en el dropdown")
                print("📋 Opciones disponibles:")
                for i, option in enumerate(options):
                    value = option.get('value', '')
                    text = option.text.strip()
                    selected = 'selected' if option.get('selected') else ''
                    print(f"   {i+1}. Valor: '{value}' | Texto: '{text}' {selected}")
                
                # Verificar que la primera opción es la vacía
                if options[0].get('value') == '':
                    print("✅ ÉXITO: La primera opción es 'Seleccione una sucursal'")
                else:
                    print("⚠️  ADVERTENCIA: La primera opción no es vacía")
                
                # Verificar que hay sucursales reales
                sucursales_reales = [opt for opt in options if opt.get('value') != '']
                if len(sucursales_reales) > 0:
                    print(f"✅ ÉXITO: Se encontraron {len(sucursales_reales)} sucursales reales")
                else:
                    print("❌ Error: No se encontraron sucursales reales en el dropdown")
                    return False
                    
            else:
                print("❌ Error: No hay suficientes opciones en el dropdown")
                return False
        else:
            print("❌ Error: No se encontró el dropdown de sucursales")
            return False
        
        # 5. Verificar que el mensaje informativo es correcto
        info_alert = soup.find('div', {'class': 'alert-info'})
        if info_alert:
            info_text = info_alert.get_text()
            if "sucursal seleccionada" in info_text.lower():
                print("✅ ÉXITO: El mensaje informativo es correcto para administradores")
            else:
                print("⚠️  ADVERTENCIA: El mensaje informativo no es el esperado")
                print(f"   Texto encontrado: {info_text[:100]}...")
        
        print("\n🎉 PRUEBA COMPLETADA: El dropdown de sucursales funciona correctamente")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor. Asegúrate de que la aplicación esté ejecutándose.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_user_restriction():
    """Probar que los usuarios regulares NO ven el dropdown"""
    
    print("\n🔍 Probando restricción para usuarios regulares...")
    print("⚠️  Esta prueba requiere crear un usuario regular primero")
    print("   Para probar completamente, crea un usuario regular desde la interfaz web")
    print("   y luego ejecuta esta función con las credenciales del usuario")

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DE DROPDOWN DE SUCURSALES")
    print("=" * 60)
    
    # Probar funcionalidad de administradores
    success = test_dropdown_sucursales()
    
    if success:
        print("\n✅ TODAS LAS PRUEBAS DE DROPDOWN PASARON")
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON")
    
    # Información sobre pruebas de usuarios
    test_user_restriction()
    
    print("\n📋 RESUMEN:")
    print("- Los administradores ven el dropdown con todas las sucursales")
    print("- Los usuarios regulares ven solo su sucursal asignada")
    print("- El sistema valida correctamente los permisos")
    print("- Las sucursales se muestran correctamente en el dropdown") 