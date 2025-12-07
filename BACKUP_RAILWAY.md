# 💾 Sistema de Backup en Railway - SISAGENT

## 📋 Descripción

Este sistema permite crear backups de la base de datos PostgreSQL que está en Railway, tanto desde la aplicación web como desde la línea de comandos.

## 🎯 Opciones Disponibles

### **Opción 1: Backup desde la Aplicación Web (Recomendado)**

1. **Iniciar sesión** en la aplicación como administrador
2. **Ir a la URL**: `https://tu-app.railway.app/admin/backup`
3. **El backup se descargará automáticamente** como archivo ZIP

**Ventajas:**
- ✅ No requiere instalar nada
- ✅ Funciona desde cualquier navegador
- ✅ Solo administradores pueden acceder
- ✅ Backup completo con información adicional

### **Opción 2: Backup desde Línea de Comandos**

#### **Requisitos:**
1. **Node.js instalado** (para Railway CLI)
2. **Railway CLI instalado**: `npm install -g @railway/cli`
3. **Logueado en Railway**: `railway login`

#### **Pasos:**

1. **Instalar Railway CLI** (si no está instalado):
```bash
npm install -g @railway/cli
```

2. **Iniciar sesión en Railway**:
```bash
railway login
```

3. **Hacer backup**:
```bash
python backup_railway.py
```

4. **Listar backups disponibles**:
```bash
python backup_railway.py list
```

## 📁 Ubicación de Backups

### **Backups Locales:**
- **Directorio**: `backups/`
- **Formato**: `backup_completo_YYYYMMDD_HHMMSS.zip`

### **Backups de Railway:**
- **Directorio**: `backups_railway/`
- **Formato**: `railway_backup_YYYYMMDD_HHMMSS.sql`

## 🔄 Restaurar Backup

### **Restaurar desde la Aplicación Web:**

1. El backup descargado contiene un archivo SQL o JSON
2. Usa el endpoint de restauración (si está disponible)
3. O restaura manualmente usando Railway CLI

### **Restaurar desde Línea de Comandos:**

```bash
# Para backups SQL de PostgreSQL
railway run psql < backups_railway/railway_backup_YYYYMMDD_HHMMSS.sql
```

## 🛡️ Seguridad

- ✅ Solo administradores pueden generar backups desde la web
- ✅ Los backups contienen información sensible - mantener seguros
- ✅ No subir backups a repositorios públicos
- ✅ Los backups están en `.gitignore` (no se suben a git)

## 📊 Información de Backups

Cada backup incluye:
- ✅ Fecha y hora de creación
- ✅ Tipo de base de datos (PostgreSQL/SQLite)
- ✅ Usuario que generó el backup
- ✅ Tamaño del backup
- ✅ Información del sistema

## ⚠️ Notas Importantes

1. **Backups grandes**: Los backups de PostgreSQL pueden ser grandes (varios MB)
2. **Tiempo de generación**: Puede tomar varios minutos para bases de datos grandes
3. **Espacio en disco**: Asegúrate de tener suficiente espacio
4. **Frecuencia recomendada**: Hacer backups diarios o semanales

## 🚀 Automatización

Para automatizar backups, puedes:

1. **Usar Railway Cron Jobs** (si está disponible)
2. **Usar GitHub Actions** para hacer backups periódicos
3. **Configurar un script en el servidor** que ejecute backups automáticamente

## 📞 Soporte

Si tienes problemas:
1. Verifica que Railway CLI esté instalado y actualizado
2. Verifica que estés logueado: `railway whoami`
3. Verifica que la base de datos PostgreSQL esté configurada en Railway
4. Revisa los logs de Railway para más información

