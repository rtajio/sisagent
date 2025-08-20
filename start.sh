#!/bin/bash

echo "🚀 Iniciando SISAGENT con Gunicorn..."

# Obtener el puerto desde la variable de entorno
PORT=${PORT:-5000}
echo "🌐 Puerto: $PORT"

# Iniciar Gunicorn directamente
exec gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --preload 