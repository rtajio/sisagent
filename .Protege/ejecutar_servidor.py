#!/usr/bin/env python3
"""
Script para ejecutar el servidor SISAGENT con la funcionalidad de edición inline corregida.
"""

import os
import sys
import subprocess
import time

def main():
    print("🚀 INICIANDO SERVIDOR SISAGENT")
    print("=" * 50)
    
    # Verificar que el archivo del servidor existe
    if not os.path.exists('servidor_final.py'):
        print("❌ Error: No se encontró el archivo servidor_final.py")
        return
    
    # Verificar que las plantillas existen
    if not os.path.exists('templates/operaciones.html'):
        print("❌ Error: No se encontró el archivo templates/operaciones.html")
        return
    
    print("✅ Archivos verificados correctamente")
    print("🌐 Iniciando servidor en http://127.0.0.1:5001")
    print("👤 Credenciales: admin / admin123")
    print("📝 Características:")
    print("   - Edición inline de operaciones funcionando")
    print("   - API REST para actualizar operaciones")
    print("   - Base de datos SQLite")
    print("   - CORS configurado correctamente")
    print("=" * 50)
    
    try:
        # Ejecutar el servidor
        subprocess.run([sys.executable, 'servidor_final.py'])
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error al ejecutar el servidor: {e}")

if __name__ == "__main__":
    main() 