@echo off
chcp 65001 >nul
echo ============================================================
echo 🔄 RESTAURADOR DE BACKUP - SISAGENT V1
echo ============================================================
echo 📅 Fecha: %date% %time%
echo ============================================================
echo.

echo 🔄 Iniciando restauración automática...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo    Por favor instala Python desde https://python.org
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Ejecutar script de restauración
echo 🚀 Ejecutando script de restauración...
python RESTAURAR_BACKUP.py

echo.
echo ============================================================
echo 📋 RESUMEN DE LA RESTAURACIÓN
echo ============================================================
echo.
echo Si la restauración fue exitosa:
echo 1. Ve al directorio: sisagent_restaurado
echo 2. Instala dependencias: pip install -r requirements.txt
echo 3. Configura variables de entorno
echo 4. Ejecuta: python app.py
echo.
echo Para más información, consulta BACKUP_INFO.md
echo.
pause 