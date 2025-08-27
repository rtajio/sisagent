#!/bin/bash
echo "🚀 Iniciando SISAGENT en Railway..."

# Esperar un momento para que todo esté listo
sleep 2

# Iniciar la aplicación con Gunicorn
exec gunicorn wsgi:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 300 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info 