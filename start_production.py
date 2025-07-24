#!/usr/bin/env python3
"""
Script de inicio optimizado para producción
"""
import os
import sys
from app import app, db

def main():
    # Configurar variables de entorno para producción
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada")
    
    # Iniciar aplicación con configuración de producción
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=False,
        threaded=True
    )

if __name__ == '__main__':
    main() 