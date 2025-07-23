#!/usr/bin/env python3
"""
Script para diagnosticar el problema del servidor web en tiempo real
"""

import requests
from bs4 import BeautifulSoup
import json

def diagnosticar_servidor():
    """Diagnosticar el problema del servidor web"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 DIAGNÓSTICO DEL SERVIDOR WEB")
    print("=" * 40)
    
    try:
        # 1. Verificar si el servidor está funcionando
        print("1. Verificando si el servidor está funcionando...")
        response = requests.get(f"{base_url}/login", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está funcionando")
        else:
            print(f"❌ Servidor responde con código: {response.status_code}")
            return False
        
        # 2. Hacer login como admin
        print("2. Iniciando sesión como administrador...")
        session = requests.Session()
        
        login_data = {
            'username': 'admin',
            'password': '61442159'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        if response.status_code in [200, 302]:
            print("✅ Login exitoso")
        else:
            print(f"❌ Error en login: {response.status_code}")
            return False
        
        # 3. Acceder a la página de registro de operaciones
        print("3. Accediendo a la página de registro de operaciones...")
        response = session.get(f"{base_url}/operaciones/registrar")
        
        if response.status_code == 200:
            print("✅ Página de registro accesible")
        else:
            print(f"❌ Error accediendo a la página: {response.status_code}")
            return False
        
        # 4. Analizar el HTML de la página
        print("4. Analizando el HTML de la página...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar el dropdown de sucursales
        sucursal_select = soup.find('select', {'id': 'sucursal_id'})
        
        if sucursal_select:
            print("✅ Dropdown de sucursales encontrado")
            
            # Analizar las opciones
            options = sucursal_select.find_all('option')
            print(f"📊 Total de opciones encontradas: {len(options)}")
            
            print("📋 Opciones en el dropdown:")
            for i, option in enumerate(options):
                value = option.get('value', '')
                text = option.text.strip()
                print(f"   {i+1}. Valor: '{value}' | Texto: '{text}'")
            
            # Verificar si hay sucursales reales
            sucursales_reales = [opt for opt in options if opt.get('value') != '']
            
            if len(sucursales_reales) > 0:
                print(f"✅ Se encontraron {len(sucursales_reales)} sucursales reales")
                return True
            else:
                print("❌ PROBLEMA: No hay sucursales reales en el dropdown")
                
                # Buscar información adicional en la página
                print("\n🔍 Buscando información adicional...")
                
                # Verificar si hay mensajes de error
                error_messages = soup.find_all(class_='alert')
                if error_messages:
                    print("⚠️  Mensajes de error encontrados:")
                    for msg in error_messages:
                        print(f"   - {msg.text.strip()}")
                
                # Verificar si el usuario es reconocido como admin
                admin_indicators = soup.find_all(text=lambda text: 'admin' in text.lower() if text else False)
                if admin_indicators:
                    print("ℹ️  Indicadores de admin encontrados:")
                    for indicator in admin_indicators[:3]:  # Solo los primeros 3
                        print(f"   - {indicator.strip()}")
                
                return False
        else:
            print("❌ Dropdown de sucursales NO encontrado")
            
            # Buscar otros elementos relacionados
            sucursal_inputs = soup.find_all('input', {'name': 'sucursal_id'})
            if sucursal_inputs:
                print(f"⚠️  Se encontraron {len(sucursal_inputs)} inputs de sucursal")
            
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor")
        print("   Asegúrate de que la aplicación esté ejecutándose en http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def verificar_template():
    """Verificar si el template está correcto"""
    
    print("\n🔍 VERIFICANDO TEMPLATE")
    print("=" * 30)
    
    try:
        with open('templates/registrar_operacion.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar el dropdown en el template
        if 'sucursal_id' in content:
            print("✅ Campo sucursal_id encontrado en el template")
        else:
            print("❌ Campo sucursal_id NO encontrado en el template")
        
        # Buscar el bucle de sucursales
        if 'for sucursal in sucursales' in content:
            print("✅ Bucle de sucursales encontrado en el template")
        else:
            print("❌ Bucle de sucursales NO encontrado en el template")
        
        # Buscar la condición de admin
        if 'current_user.es_admin' in content:
            print("✅ Condición de admin encontrada en el template")
        else:
            print("❌ Condición de admin NO encontrada en el template")
        
    except FileNotFoundError:
        print("❌ Archivo de template no encontrado")
    except Exception as e:
        print(f"❌ Error leyendo template: {e}")

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO COMPLETO")
    print("=" * 40)
    
    # Diagnosticar servidor
    servidor_ok = diagnosticar_servidor()
    
    # Verificar template
    verificar_template()
    
    if servidor_ok:
        print("\n✅ DIAGNÓSTICO COMPLETADO")
        print("   El servidor funciona correctamente")
        print("   El problema podría estar en el navegador o caché")
    else:
        print("\n❌ PROBLEMA IDENTIFICADO")
        print("   El servidor no está funcionando correctamente")
        print("   Revisa los logs del servidor") 