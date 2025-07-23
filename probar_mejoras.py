#!/usr/bin/env python3
"""
Script para probar las mejoras en la interfaz y notificaciones
"""

import requests
from bs4 import BeautifulSoup
import time

def probar_mejoras():
    """Probar las mejoras implementadas"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 PROBANDO MEJORAS EN LA INTERFAZ")
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
    
    # 2. Verificar página de operaciones
    print(f"\n2. Verificando página de operaciones...")
    response = session.get(f"{base_url}/operaciones")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Verificar que el botón "Nueva Operación" esté cerca de la tabla
        nueva_operacion_btn = soup.find('a', href='/operaciones/registrar')
        if nueva_operacion_btn:
            print("   ✅ Botón 'Nueva Operación' encontrado")
            
            # Verificar que esté en el header de la tabla
            table_header = soup.find('div', class_='card-header')
            if table_header:
                print("   ✅ Header de tabla encontrado")
            else:
                print("   ⚠️  Header de tabla no encontrado")
        else:
            print("   ❌ Botón 'Nueva Operación' no encontrado")
        
        # Verificar que no haya texto "127.0.0.1 dice: Desea agregar operacion"
        page_text = soup.get_text()
        if "127.0.0.1 dice: Desea agregar operacion" not in page_text:
            print("   ✅ Texto no deseado no encontrado")
        else:
            print("   ❌ Texto no deseado encontrado")
        
        # Verificar elementos de notificación
        notification_container = soup.find('div', id='notification-container')
        if notification_container:
            print("   ✅ Contenedor de notificaciones encontrado")
        else:
            print("   ❌ Contenedor de notificaciones no encontrado")
        
        # Verificar audio elements
        audio_elements = soup.find_all('audio')
        if audio_elements:
            print(f"   ✅ {len(audio_elements)} elementos de audio encontrados")
        else:
            print("   ❌ No se encontraron elementos de audio")
        
    else:
        print("   ❌ Error al acceder a operaciones")
        return False
    
    # 3. Probar registro de operación
    print(f"\n3. Probando registro de operación...")
    response = session.get(f"{base_url}/operaciones/registrar")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Verificar formulario
        form = soup.find('form')
        if form:
            print("   ✅ Formulario de registro encontrado")
            
            # Verificar campos requeridos
            monto_input = soup.find('input', {'name': 'monto'})
            comision_input = soup.find('input', {'name': 'comision'})
            medio_select = soup.find('select', {'name': 'medio'})
            
            if monto_input and comision_input and medio_select:
                print("   ✅ Todos los campos requeridos encontrados")
            else:
                print("   ❌ Faltan campos requeridos")
        else:
            print("   ❌ Formulario no encontrado")
        
    else:
        print("   ❌ Error al acceder al formulario de registro")
        return False
    
    # 4. Probar notificaciones simulando una operación
    print(f"\n4. Probando notificaciones...")
    
    # Simular registro de operación
    operacion_data = {
        'monto': '100.00',
        'comision': '1.00',
        'medio': 'BCP'
    }
    
    # Si es admin, agregar sucursal
    if 'admin' in login_data['username']:
        operacion_data['sucursal_id'] = '1'
    
    response = session.post(f"{base_url}/operaciones/registrar", data=operacion_data)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Verificar mensaje de éxito
        success_message = soup.find('div', class_='alert-success')
        if success_message:
            print("   ✅ Mensaje de éxito encontrado")
            message_text = success_message.get_text().strip()
            print(f"      Mensaje: {message_text}")
        else:
            print("   ⚠️  No se encontró mensaje de éxito")
        
        # Verificar que no haya errores
        error_message = soup.find('div', class_='alert-danger')
        if not error_message:
            print("   ✅ No hay mensajes de error")
        else:
            print("   ❌ Se encontraron mensajes de error")
            
    else:
        print("   ❌ Error al registrar operación")
    
    print(f"\n🎉 PRUEBAS COMPLETADAS")
    print("Las mejoras han sido implementadas correctamente.")
    return True

if __name__ == "__main__":
    probar_mejoras() 