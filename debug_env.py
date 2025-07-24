#!/usr/bin/env python3
"""
Script de diagnóstico para verificar variables de entorno en Railway
"""
import os

def debug_environment():
    """Mostrar información de diagnóstico del entorno"""
    print("🔍 DIAGNÓSTICO DE VARIABLES DE ENTORNO")
    print("=" * 50)
    
    # Variables importantes
    important_vars = [
        'DATABASE_URL',
        'PORT',
        'FLASK_ENV',
        'SECRET_KEY',
        'RAILWAY_ENVIRONMENT',
        'RAILWAY_PROJECT_ID'
    ]
    
    for var in important_vars:
        value = os.environ.get(var)
        if value:
            # Ocultar información sensible
            if 'SECRET' in var or 'KEY' in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            elif 'DATABASE_URL' in var:
                # Mostrar solo el tipo de base de datos
                if 'postgres' in value.lower():
                    display_value = "postgresql://[oculto]"
                elif 'mysql' in value.lower():
                    display_value = "mysql://[oculto]"
                else:
                    display_value = "[otro tipo]"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: NO DEFINIDA")
    
    print("\n🔍 TODAS LAS VARIABLES DE ENTORNO:")
    print("=" * 50)
    for key, value in os.environ.items():
        if 'SECRET' in key or 'KEY' in key or 'PASSWORD' in key:
            print(f"{key}: [OCULTO]")
        elif 'DATABASE_URL' in key:
            if 'postgres' in value.lower():
                print(f"{key}: postgresql://[oculto]")
            elif 'mysql' in value.lower():
                print(f"{key}: mysql://[oculto]")
            else:
                print(f"{key}: [otro tipo]")
        else:
            print(f"{key}: {value}")

if __name__ == "__main__":
    debug_environment() 