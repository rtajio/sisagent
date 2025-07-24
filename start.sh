#!/bin/bash

echo "🚀 Iniciando SISAGENT en Railway..."

# Activar entorno virtual si existe
if [ -d "/opt/venv" ]; then
    echo "📦 Activando entorno virtual..."
    source /opt/venv/bin/activate
fi

# Diagnóstico de variables de entorno
echo "🔍 Ejecutando diagnóstico de variables de entorno..."
python debug_env.py

# Inicializar base de datos
echo "🔧 Inicializando base de datos..."
python init_db.py

# Verificar que la inicialización fue exitosa
if [ $? -eq 0 ]; then
    echo "✅ Base de datos inicializada correctamente"
else
    echo "❌ Error al inicializar la base de datos"
    exit 1
fi

# Obtener el puerto desde la variable de entorno
PORT=${PORT:-5000}
echo "🌐 Iniciando servidor en puerto $PORT"

# Iniciar Gunicorn
echo "🚀 Iniciando Gunicorn..."
exec gunicorn wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info 