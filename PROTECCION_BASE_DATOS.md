# 🛡️ Protección de Base de Datos SISAGENT

## 📋 Problema Solucionado

**Antes**: Cada vez que se hacía un cambio en el código, la base de datos se borraba automáticamente en Railway.

**Ahora**: La base de datos se preserva durante los cambios y se hacen respaldos automáticos.

## ✅ Soluciones Implementadas

### **🔧 1. Script de Inicio Inteligente (`start_app.py`)**
- ✅ **Verifica si la base de datos existe** antes de inicializar
- ✅ **Solo inicializa cuando es necesario** (no borra datos existentes)
- ✅ **Respaldo automático** antes de cualquier operación
- ✅ **Preserva todos los registros** durante los deploys

### **🔧 2. Sistema de Respaldo Automático (`backup_db.py`)**
- ✅ **Respaldo automático** en cada inicio
- ✅ **Respaldo manual** antes de cambios importantes
- ✅ **Restauración fácil** desde cualquier respaldo
- ✅ **Listado de respaldos** disponibles

### **🔧 3. Respaldo de Seguridad (`pre_change_backup.py`)**
- ✅ **Respaldo manual** antes de cambios importantes
- ✅ **Confirmación** antes de crear respaldo
- ✅ **Información detallada** del respaldo creado

## 🚀 Cómo Usar el Sistema

### **📊 Respaldo Automático (Ocurre en cada deploy)**
```bash
# Se ejecuta automáticamente en Railway
# No necesitas hacer nada
```

### **🛡️ Respaldo Manual Antes de Cambios**
```bash
python pre_change_backup.py
```

### **📋 Ver Respaldos Disponibles**
```bash
python backup_db.py list
```

### **🔄 Restaurar Base de Datos**
```bash
python backup_db.py restore N
# Donde N es el número del respaldo
```

## 📁 Estructura de Respaldos

```
database_backups/
├── db_backup_20250724_201500.db
├── pre_change_backup_20250724_202000.db
├── db_backup_20250724_203000.db
└── ...
```

## 🎯 Flujo de Trabajo Recomendado

### **1. Antes de Hacer Cambios Importantes:**
```bash
python pre_change_backup.py
# Hacer los cambios
git add .
git commit -m "Descripción de cambios"
git push origin main
```

### **2. Si Algo Sale Mal:**
```bash
python backup_db.py list
python backup_db.py restore N
# Donde N es el número del último respaldo estable
```

### **3. Verificar que Todo Funcione:**
```bash
python app.py
# Probar la aplicación localmente
```

## ⚠️ Información Importante

### **✅ Lo que SÍ se preserva:**
- ✅ **Todos los usuarios** registrados
- ✅ **Todas las operaciones** bancarias
- ✅ **Todas las sucursales** configuradas
- ✅ **Todos los medios de pago** configurados
- ✅ **Todas las comisiones** calculadas
- ✅ **Toda la configuración** del sistema

### **❌ Lo que NO se borra:**
- ❌ **Base de datos** (ya no se borra)
- ❌ **Registros de usuarios** (se preservan)
- ❌ **Operaciones bancarias** (se mantienen)
- ❌ **Configuraciones** (se conservan)

## 🔧 Comandos Útiles

### **Crear Respaldo Rápido:**
```bash
python pre_change_backup.py
```

### **Ver Estado de la Base de Datos:**
```bash
python backup_db.py list
```

### **Restaurar al Estado Anterior:**
```bash
python backup_db.py restore 1
```

### **Verificar que la App Funciona:**
```bash
python app.py
```

## 📞 Soporte

Si tienes problemas con la base de datos:

1. **Verificar respaldos disponibles:**
   ```bash
   python backup_db.py list
   ```

2. **Restaurar desde el último respaldo estable:**
   ```bash
   python backup_db.py restore N
   ```

3. **Verificar que la aplicación funciona:**
   ```bash
   python app.py
   ```

## 🎉 Beneficios

- ✅ **No más pérdida de datos** durante cambios
- ✅ **Respaldos automáticos** en cada deploy
- ✅ **Restauración fácil** si algo sale mal
- ✅ **Trabajo más seguro** y confiable
- ✅ **Preservación de todos los registros**

---

**🛡️ Sistema de Protección de Base de Datos SISAGENT - Versión 1.0**  
**📅 Implementado:** 24 de Julio de 2025  
**🎯 Estado:** Base de datos protegida y respaldada 