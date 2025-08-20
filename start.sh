#!/bin/bash

echo "�� Iniciando SISAGENT..."

# Intentar inicializar la base de datos, pero no fallar si hay errores
echo "🔧 Inicializando base de datos..."
python init_db.py || echo "⚠️ Advertencia: La inicialización de la base de datos falló, pero continuando..."

# Iniciar la aplicación
echo "🌐 Iniciando aplicación..."
exec gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload 