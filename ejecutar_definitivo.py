#!/usr/bin/env python3
"""
Script para ejecutar el servidor SISAGENT definitivo
Solución completa para el sistema de operaciones bancarias
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 INICIANDO SERVIDOR SISAGENT DEFINITIVO")
    print("=" * 50)
    
    # Verificar que el archivo del servidor existe
    if not os.path.exists('servidor_definitivo.py'):
        print("❌ Error: No se encontró el archivo servidor_definitivo.py")
        return
    
    # Verificar que las plantillas existen
    if not os.path.exists('templates/operaciones.html'):
        print("❌ Error: No se encontró el archivo templates/operaciones.html")
        return
    
    print("✅ Archivos verificados correctamente")
    print("🌐 Iniciando servidor en http://127.0.0.1:5002")
    print("👤 Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("📝 Características:")
    print("   - API de actualización de operaciones funcional")
    print("   - CORS configurado correctamente")
    print("   - Base de datos SQLite limpia")
    print("   - Logging detallado para debugging")
    print("   - Edición inline de operaciones habilitada")
    print("")
    print("💡 Para probar la edición inline:")
    print("   1. Inicia sesión con admin / admin123")
    print("   2. Ve a la página de operaciones")
    print("   3. Haz clic en 'Editar' en cualquier operación")
    print("   4. Modifica los campos y haz clic en 'Guardar'")
    print("   5. La operación se actualizará sin errores")
    print("")
    
    try:
        # Ejecutar el servidor
        subprocess.run([sys.executable, 'servidor_definitivo.py'])
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al ejecutar el servidor: {str(e)}")

if __name__ == "__main__":
    main() 