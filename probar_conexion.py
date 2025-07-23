#!/usr/bin/env python3
"""
Script para probar la conexión al servidor
"""

import requests
import time

def probar_conexion():
    """Probar la conexión al servidor"""
    
    print("🔍 PROBANDO CONEXIÓN AL SERVIDOR")
    print("=" * 40)
    
    url = "http://127.0.0.1:5000/login"
    
    try:
        print(f"1. Intentando conectar a: {url}")
        response = requests.get(url, timeout=10)
        
        print(f"   ✅ Conexión exitosa")
        print(f"   📊 Código de estado: {response.status_code}")
        print(f"   📄 Tipo de contenido: {response.headers.get('content-type', 'No especificado')}")
        print(f"   📏 Tamaño de respuesta: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("   🎉 El servidor está funcionando correctamente")
            
            # Verificar si hay contenido HTML
            if 'text/html' in response.headers.get('content-type', ''):
                print("   ✅ Respuesta HTML detectada")
                
                # Verificar contenido básico
                content = response.text
                if '<html' in content.lower():
                    print("   ✅ Etiqueta HTML encontrada")
                if '<title' in content.lower():
                    print("   ✅ Etiqueta title encontrada")
                if 'sisagent' in content.lower():
                    print("   ✅ Contenido SISAGENT encontrado")
                if 'login' in content.lower():
                    print("   ✅ Contenido de login encontrado")
                    
                # Mostrar las primeras líneas
                lines = content.split('\n')[:10]
                print(f"\n   📝 Primeras 10 líneas:")
                for i, line in enumerate(lines, 1):
                    print(f"      {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")
                    
            else:
                print("   ⚠️  La respuesta no es HTML")
                print(f"   📄 Contenido: {response.text[:200]}...")
                
        else:
            print(f"   ❌ Error: Código de estado {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Error de conexión: El servidor no está ejecutándose")
        print("   💡 Asegúrate de ejecutar 'python app.py' primero")
        
    except requests.exceptions.Timeout:
        print("   ❌ Error de timeout: El servidor no responde")
        
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

if __name__ == "__main__":
    probar_conexion() 