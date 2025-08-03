# 🚀 GUÍA DE DESPLIEGUE EN RAILWAY

## 📋 **ESTADO ACTUAL**
- ✅ Código listo para Railway
- ✅ Configuración completa
- ❌ Railway CLI no disponible en el sistema

## 🔧 **OPCIONES DE DESPLIEGUE**

### **Opción 1: Instalar Railway CLI (Recomendado)**

#### **Paso 1: Instalar Node.js**
1. Descargar Node.js desde: https://nodejs.org/
2. Instalar Node.js (incluye npm)
3. Reiniciar PowerShell

#### **Paso 2: Instalar Railway CLI**
```bash
npm install -g @railway/cli
```

#### **Paso 3: Desplegar**
```bash
railway login
railway link
railway up
```

### **Opción 2: Despliegue via GitHub (Alternativo)**

#### **Paso 1: Crear repositorio en GitHub**
1. Ir a https://github.com/
2. Crear nuevo repositorio: `sisagent`
3. Subir el código

#### **Paso 2: Conectar Railway con GitHub**
1. Ir a https://railway.app/
2. Crear cuenta/login
3. Crear nuevo proyecto
4. Seleccionar "Deploy from GitHub repo"
5. Conectar con el repositorio `sisagent`

#### **Paso 3: Configurar variables de entorno**
En Railway Dashboard:
- `SECRET_KEY`: `tu-clave-secreta-muy-segura`
- `DATABASE_URL`: Se configura automáticamente

### **Opción 3: Despliegue Manual via Railway Dashboard**

#### **Paso 1: Preparar archivos**
1. Comprimir todos los archivos del proyecto
2. Excluir: `__pycache__`, `.git`, `instance/`

#### **Paso 2: Subir a Railway**
1. Ir a https://railway.app/
2. Crear nuevo proyecto
3. Seleccionar "Deploy from template"
4. Subir el archivo comprimido

## 🎯 **RECOMENDACIÓN INMEDIATA**

### **Para desplegar AHORA:**

1. **Instalar Node.js**:
   - Descargar desde: https://nodejs.org/
   - Instalar versión LTS
   - Reiniciar PowerShell

2. **Instalar Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

3. **Desplegar**:
   ```bash
   railway login
   railway link
   railway up
   ```

## 📁 **ARCHIVOS NECESARIOS PARA DESPLIEGUE**

### **Archivos principales**:
- ✅ `app.py` - Aplicación principal
- ✅ `wsgi.py` - Configuración WSGI
- ✅ `requirements.txt` - Dependencias
- ✅ `railway.toml` - Configuración Railway
- ✅ `Procfile` - Configuración Procfile
- ✅ `init_db.py` - Inicialización de base de datos

### **Archivos de configuración**:
- ✅ `config.env` - Variables de entorno (local)
- ✅ `config.py` - Configuración de la aplicación

### **Templates y estáticos**:
- ✅ `templates/` - Templates HTML
- ✅ `static/` - Archivos estáticos (si existen)

## 🔍 **VERIFICACIÓN POST-DESPLIEGUE**

### **Comandos de verificación**:
```bash
# Ver estado
railway status

# Ver logs
railway logs

# Obtener URL
railway domain

# Ver variables
railway variables
```

### **URLs de prueba**:
- `/health` - Health check básico
- `/railway-health` - Health check Railway
- `/api/health` - Health check API
- `/login` - Página de login

## ⚠️ **NOTAS IMPORTANTES**

1. **Base de datos**: Railway creará automáticamente una base de datos PostgreSQL
2. **Variables de entorno**: Se configuran en Railway Dashboard
3. **Dominio**: Railway asignará un dominio automáticamente
4. **Logs**: Disponibles en Railway Dashboard

## 🚀 **PRÓXIMOS PASOS**

1. **Instalar Node.js** (si no está instalado)
2. **Instalar Railway CLI**
3. **Ejecutar comandos de despliegue**
4. **Verificar funcionamiento**
5. **Probar todas las funcionalidades**

**¿Quieres que proceda con la instalación de Node.js o prefieres usar otra opción?** 