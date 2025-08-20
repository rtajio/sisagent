#!/usr/bin/env python3
"""
WSGI entry point para Railway
"""
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

# Importar la aplicación
from app import app

# Variable global para la aplicación
application = app

print("✅ SISAGENT listo para Gunicorn") 