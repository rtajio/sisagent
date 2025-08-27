#!/bin/bash
echo "🚀 Iniciando SISAGENT en Railway..."

# Esperar un momento para que todo esté listo
sleep 2

# Inicializar la base de datos
echo "📋 Inicializando base de datos..."
python init_db_railway.py

# Iniciar la aplicación con Gunicorn
echo "🌐 Iniciando aplicación..."
exec gunicorn wsgi:app \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 300 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info 