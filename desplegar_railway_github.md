# 🚀 DESPLIEGUE EN RAILWAY VIA GITHUB

## 📋 **PASOS PARA DESPLEGAR**

### **Paso 1: Crear Repositorio en GitHub**

1. **Ir a GitHub**: https://github.com/
2. **Crear nuevo repositorio**:
   - Nombre: `sisagent`
   - Descripción: "Sistema de Gestión de Operaciones Bancarias"
   - Público o Privado (según preferencia)
   - **NO** inicializar con README (ya tenemos uno)

### **Paso 2: Subir Código a GitHub**

```bash
# Agregar el repositorio remoto (reemplaza TU_USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/sisagent.git

# Subir el código
git branch -M main
git push -u origin main
```

### **Paso 3: Crear Proyecto en Railway**

1. **Ir a Railway**: https://railway.app/
2. **Crear cuenta** o iniciar sesión
3. **Crear nuevo proyecto**
4. **Seleccionar "Deploy from GitHub repo"**
5. **Conectar con el repositorio `sisagent`**

### **Paso 4: Configurar Variables de Entorno**

En Railway Dashboard:

1. **Ir a la pestaña "Variables"**
2. **Agregar variables**:
   ```
   SECRET_KEY=tu-clave-secreta-muy-segura-aqui-2025
   ```

3. **DATABASE_URL se configura automáticamente** por Railway

### **Paso 5: Verificar Despliegue**

1. **Ir a la pestaña "Deployments"**
2. **Verificar que el build sea exitoso**
3. **Obtener la URL del proyecto** en la pestaña "Settings"

### **Paso 6: Probar la Aplicación**

1. **Acceder a la URL de Railway**
2. **Probar health checks**:
   - `https://tu-app.railway.app/health`
   - `https://tu-app.railway.app/railway-health`
   - `https://tu-app.railway.app/api/health`

3. **Probar login**:
   - Usuario: `admin`
   - Contraseña: `admin123`

## 🔧 **COMANDOS PARA EJECUTAR AHORA**

### **Si tienes GitHub CLI**:
```bash
# Crear repositorio
gh repo create sisagent --public --description "Sistema de Gestión de Operaciones Bancarias"

# Subir código
git remote add origin https://github.com/TU_USUARIO/sisagent.git
git branch -M main
git push -u origin main
```

### **Si no tienes GitHub CLI**:
1. Crear repositorio manualmente en GitHub
2. Ejecutar los comandos git de arriba

## 📊 **VERIFICACIÓN POST-DESPLIEGUE**

### **Health Checks**:
- ✅ `/health` - Debe responder 200 OK
- ✅ `/railway-health` - Debe responder 200 OK
- ✅ `/api/health` - Debe responder JSON con estado

### **Funcionalidades a Probar**:
- ✅ Login de administrador
- ✅ Dashboard de administrador
- ✅ Gestión de usuarios
- ✅ Gestión de sucursales
- ✅ Registro de operaciones
- ✅ Sistema de tareos
- ✅ Reportes y exportación

### **Base de Datos**:
- ✅ Conexión a PostgreSQL
- ✅ Tablas creadas automáticamente
- ✅ Datos de prueba disponibles

## 🎯 **URLS IMPORTANTES**

### **Después del despliegue**:
- **Aplicación**: `https://tu-app.railway.app/`
- **Login**: `https://tu-app.railway.app/login`
- **Admin**: `https://tu-app.railway.app/admin`
- **Health**: `https://tu-app.railway.app/health`

### **Railway Dashboard**:
- **Proyecto**: https://railway.app/dashboard
- **Logs**: Disponibles en Railway Dashboard
- **Variables**: Configurables en Railway Dashboard

## ⚠️ **NOTAS IMPORTANTES**

1. **Base de datos**: Railway creará automáticamente una base de datos PostgreSQL
2. **Dominio**: Railway asignará un dominio automáticamente
3. **Logs**: Disponibles en Railway Dashboard
4. **Variables**: Se configuran en Railway Dashboard
5. **Auto-deploy**: Habilitado por defecto (se actualiza automáticamente al hacer push)

## 🚀 **PRÓXIMOS PASOS**

1. **Crear repositorio en GitHub**
2. **Subir código**
3. **Conectar con Railway**
4. **Configurar variables**
5. **Probar funcionamiento**

## 📞 **SOPORTE**

Si hay problemas:
1. Revisar logs en Railway Dashboard
2. Verificar variables de entorno
3. Comprobar que todos los archivos estén en el repositorio
4. Verificar que requirements.txt esté actualizado

---

**¿Listo para desplegar? ¡Sigue los pasos arriba!** 🚀 