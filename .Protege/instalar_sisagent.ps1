# Script de instalación de SISAGENT
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    INSTALADOR SISAGENT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
Write-Host "Verificando si Python está instalado..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python encontrado: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python no encontrado"
    }
} catch {
    Write-Host "Python no encontrado. Instalando Python..." -ForegroundColor Red
    
    # Descargar Python
    $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"
    
    Write-Host "Descargando Python 3.11..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath
    
    Write-Host "Instalando Python..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0" -Wait
    
    Write-Host "Esperando que termine la instalación..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Limpiar archivo de instalación
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    
    # Refrescar variables de entorno
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "Python instalado correctamente" -ForegroundColor Green
}

# Instalar dependencias
Write-Host ""
Write-Host "Instalando dependencias de SISAGENT..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Configurando base de datos..." -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANTE: Antes de continuar, asegúrate de:" -ForegroundColor Red
Write-Host "1. Tener MySQL instalado y ejecutándose" -ForegroundColor White
Write-Host "2. Crear una base de datos llamada 'sisagent'" -ForegroundColor White
Write-Host "3. Configurar las credenciales en el archivo .env" -ForegroundColor White
Write-Host ""
Write-Host "Ejemplo de comandos MySQL:" -ForegroundColor Cyan
Write-Host "CREATE DATABASE sisagent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" -ForegroundColor Gray
Write-Host "CREATE USER 'sisagent_user'@'localhost' IDENTIFIED BY 'tu_password';" -ForegroundColor Gray
Write-Host "GRANT ALL PRIVILEGES ON sisagent.* TO 'sisagent_user'@'localhost';" -ForegroundColor Gray
Write-Host "FLUSH PRIVILEGES;" -ForegroundColor Gray
Write-Host ""

Read-Host "Presiona Enter para continuar"

Write-Host ""
Write-Host "Iniciando SISAGENT..." -ForegroundColor Green
Write-Host ""
Write-Host "El sistema estará disponible en: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Usuario por defecto: admin" -ForegroundColor Cyan
Write-Host "Contraseña por defecto: 61442159" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Ejecutar la aplicación
python app.py 