#!/usr/bin/env python3
"""
Script para ejecutar el servidor SISAGENT Simple
Solución definitiva para edición de operaciones
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 INICIANDO SERVIDOR SISAGENT SIMPLE")
    print("=" * 50)
    
    # Verificar que el archivo del servidor existe
    if not os.path.exists('servidor_simple.py'):
        print("❌ Error: No se encontró el archivo servidor_simple.py")
        return
    
    # Verificar que las plantillas existen
    if not os.path.exists('templates/operaciones.html'):
        print("❌ Error: No se encontró el archivo templates/operaciones.html")
        return
    
    print("✅ Archivos verificados correctamente")
    print("🌐 Iniciando servidor en http://127.0.0.1:5000")
    print("👤 Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("\n📝 Características de esta versión:")
    print("   ✅ Edición por formulario tradicional (sin API REST)")
    print("   ✅ Modal de Bootstrap para editar operaciones")
    print("   ✅ Sin JavaScript complejo")
    print("   ✅ Sin errores de JSON")
    print("   ✅ Base de datos SQLite limpia")
    print("\n💡 Instrucciones:")
    print("   1. Abre http://127.0.0.1:5000 en tu navegador")
    print("   2. Inicia sesión con las credenciales")
    print("   3. Haz clic en el botón 'Editar' de cualquier operación")
    print("   4. Modifica los datos en el modal")
    print("   5. Haz clic en 'Guardar Cambios'")
    print("   6. ¡Listo! No más errores de JSON")
    
    try:
        # Ejecutar el servidor
        subprocess.run([sys.executable, 'servidor_simple.py'])
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error al ejecutar el servidor: {e}")

if __name__ == "__main__":
    main() 