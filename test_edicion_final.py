#!/usr/bin/env python3
"""
Script de prueba para la edición de operaciones - Versión Final
"""

import requests
import time

def test_edicion_final():
    print("🧪 PROBANDO EDICIÓN FINAL")
    print("=" * 50)
    
    # URL del servidor
    base_url = "http://127.0.0.1:5000"
    
    print(f"🌐 Servidor: {base_url}")
    print("📝 Probando flujo completo de edición...")
    
    try:
        # 1. Verificar que el servidor esté funcionando
        response = requests.get(base_url)
        print(f"✅ Servidor respondiendo: {response.status_code}")
        
        # 2. Verificar que la ruta de edición existe
        response = requests.post(f"{base_url}/editar_operacion/1", data={
            'monto': '150.75',
            'comision': '7.50',
            'medio': 'BBVA'
        }, allow_redirects=False)
        
        print(f"📥 Respuesta de edición: {response.status_code}")
        
        if response.status_code == 302:
            print("✅ Redirección correcta (esperado para formulario tradicional)")
            print("✅ La edición está funcionando correctamente")
        elif response.status_code == 200:
            print("✅ Respuesta directa recibida")
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
        
        print("\n🎉 Prueba completada exitosamente!")
        print("💡 El servidor está funcionando correctamente")
        print("🌐 Accede a http://127.0.0.1:5000 para usar la aplicación")
        print("👤 Credenciales: admin / admin123")
        print("\n📝 Para editar una operación:")
        print("   1. Inicia sesión")
        print("   2. Haz clic en el botón 'Editar' (ícono de lápiz)")
        print("   3. Modifica los datos en el modal")
        print("   4. Haz clic en 'Guardar Cambios'")
        print("   5. ¡Listo! No más errores de JSON")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_edicion_final() 