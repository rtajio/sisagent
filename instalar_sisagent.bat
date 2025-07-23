@echo off
echo ========================================
echo    INSTALADOR SISAGENT
echo ========================================
echo.

echo Verificando si Python esta instalado...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo Python encontrado!
    goto :instalar_dependencias
)

echo Python no encontrado. Instalando Python...
echo.

echo Descargando Python 3.11...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile 'python-installer.exe'"

echo Instalando Python...
python-installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

echo Esperando que termine la instalacion...
timeout /t 30 /nobreak >nul

echo Limpiando archivo de instalacion...
del python-installer.exe

echo Refreshing PATH...
call refreshenv

:instalar_dependencias
echo.
echo Instalando dependencias de SISAGENT...
pip install -r requirements.txt

echo.
echo Configurando base de datos...
echo.
echo IMPORTANTE: Antes de continuar, asegurate de:
echo 1. Tener MySQL instalado y ejecutandose
echo 2. Crear una base de datos llamada 'sisagent'
echo 3. Configurar las credenciales en el archivo .env
echo.
echo Ejemplo de comandos MySQL:
echo CREATE DATABASE sisagent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
echo CREATE USER 'sisagent_user'@'localhost' IDENTIFIED BY 'tu_password';
echo GRANT ALL PRIVILEGES ON sisagent.* TO 'sisagent_user'@'localhost';
echo FLUSH PRIVILEGES;
echo.

pause

echo.
echo Iniciando SISAGENT...
echo.
echo El sistema estara disponible en: http://localhost:5000
echo Usuario por defecto: admin
echo Contraseña por defecto: 61442159
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python app.py

pause 