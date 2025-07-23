# Instrucciones de Instalación Manual - SISAGENT

## Prerrequisitos

### 1. Instalar Python 3.8 o superior

**Opción A: Descarga directa**
1. Ve a https://www.python.org/downloads/
2. Descarga Python 3.11.8 (última versión estable)
3. Ejecuta el instalador
4. **IMPORTANTE**: Marca la casilla "Add Python to PATH"
5. Completa la instalación

**Opción B: Microsoft Store**
1. Abre Microsoft Store
2. Busca "Python 3.11"
3. Instala la versión oficial de Python Software Foundation

### 2. Instalar MySQL

**Opción A: MySQL Community Server**
1. Ve a https://dev.mysql.com/downloads/mysql/
2. Descarga MySQL Community Server
3. Ejecuta el instalador
4. Configura una contraseña para el usuario root
5. Completa la instalación

**Opción B: XAMPP (incluye MySQL)**
1. Ve a https://www.apachefriends.org/
2. Descarga XAMPP
3. Instala y ejecuta MySQL desde el panel de control

## Instalación de SISAGENT

### Paso 1: Verificar Python
Abre PowerShell o CMD y ejecuta:
```bash
python --version
```
Deberías ver algo como: `Python 3.11.8`

### Paso 2: Instalar dependencias
En la carpeta del proyecto, ejecuta:
```bash
pip install -r requirements.txt
```

### Paso 3: Configurar base de datos MySQL

1. **Abrir MySQL Command Line Client** o **phpMyAdmin** (si usas XAMPP)

2. **Crear la base de datos**:
```sql
CREATE DATABASE sisagent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. **Crear usuario** (opcional, puedes usar root):
```sql
CREATE USER 'sisagent_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON sisagent.* TO 'sisagent_user'@'localhost';
FLUSH PRIVILEGES;
```

### Paso 4: Configurar variables de entorno

1. **Copiar archivo de configuración**:
```bash
copy config.env .env
```

2. **Editar el archivo .env** con tus credenciales:
```env
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DATABASE_URL=mysql+pymysql://usuario:password@localhost/sisagent
```

**Ejemplos de configuración**:

Si usas el usuario root:
```env
DATABASE_URL=mysql+pymysql://root:tu_password_root@localhost/sisagent
```

Si creaste un usuario específico:
```env
DATABASE_URL=mysql+pymysql://sisagent_user:tu_password@localhost/sisagent
```

### Paso 5: Ejecutar SISAGENT

```bash
python app.py
```

### Paso 6: Acceder al sistema

1. Abre tu navegador
2. Ve a: http://localhost:5000
3. **Credenciales por defecto**:
   - Usuario: `admin`
   - Contraseña: `61442159`

## Solución de Problemas

### Error: "No module named 'flask'"
```bash
pip install flask
```

### Error: "No module named 'pymysql'"
```bash
pip install pymysql
```

### Error de conexión a MySQL
1. Verifica que MySQL esté ejecutándose
2. Verifica las credenciales en el archivo .env
3. Verifica que la base de datos 'sisagent' exista

### Error: "Port 5000 is already in use"
Cambia el puerto en app.py:
```python
app.run(debug=True, port=5001)
```

## Scripts Automatizados

### Usar script batch (Windows)
```bash
instalar_sisagent.bat
```

### Usar script PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File instalar_sisagent.ps1
```

## Estructura del Proyecto

```
sisagent/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── config.env            # Configuración
├── .env                  # Variables de entorno (crear)
├── instalar_sisagent.bat # Script de instalación
├── instalar_sisagent.ps1 # Script PowerShell
├── templates/            # Plantillas HTML
└── logs/                 # Archivos de log
```

## Características del Sistema

✅ **Gestión de usuarios y permisos**
✅ **Gestión de sucursales**
✅ **Registro de operaciones bancarias**
✅ **Comisiones automáticas (diarias y mensuales)**
✅ **Filtros avanzados de consulta**
✅ **Edición y eliminación de operaciones**
✅ **Notificaciones con sonido**
✅ **Zona horaria de Perú (UTC-5)**
✅ **Moneda en Soles Peruanos**

## Soporte

Si tienes problemas con la instalación:
1. Verifica que Python esté en el PATH
2. Verifica que MySQL esté ejecutándose
3. Verifica las credenciales de la base de datos
4. Revisa los logs de error en la consola 