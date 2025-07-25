# 🚀 SOLUCIÓN: Configurar PostgreSQL en Railway

## **¿Por qué se borran los datos?**

Railway usa contenedores que se recrean en cada deploy. Si usas SQLite, la base de datos está dentro del contenedor y se pierde.

## **SOLUCIÓN: PostgreSQL**

PostgreSQL es una base de datos externa que persiste entre deploys.

---

## **PASOS PARA CONFIGURAR**

### **Paso 1: Crear Base de Datos PostgreSQL**

1. Ve a: https://railway.app/dashboard
2. Selecciona tu proyecto: `sisagent`
3. Haz clic en **"New"** (botón verde)
4. Selecciona **"Database"**
5. Elige **"PostgreSQL"**
6. Nombre: `sisagent-db`
7. Haz clic en **"Deploy"**

### **Paso 2: Verificar Variables de Entorno**

Railway automáticamente agregará:
- `DATABASE_URL` = `postgresql://...`

### **Paso 3: Hacer Deploy**

```bash
git add .
git commit -m "Configurar PostgreSQL"
git push
```

---

## **¿QUÉ PASA DESPUÉS?**

✅ **Los datos se mantienen** entre deploys
✅ **Auto-deploy sigue funcionando**
✅ **No necesitas variables adicionales**
✅ **La aplicación detecta automáticamente PostgreSQL**

---

## **VERIFICACIÓN**

Después del deploy, verás en los logs:
```
✅ Usando PostgreSQL en Railway: postgresql://...
```

En lugar de:
```
✅ Usando SQLite para desarrollo local
```

---

## **VENTAJAS**

- 🔄 **Auto-deploy sin pérdida de datos**
- 🚀 **Más rápido que SQLite**
- 📊 **Mejor para producción**
- 🔒 **Más seguro**
- 📈 **Escalable**

---

## **NOTA IMPORTANTE**

Tu código ya está configurado para usar PostgreSQL automáticamente cuando detecte `DATABASE_URL`. No necesitas cambiar nada en el código. 