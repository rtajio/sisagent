# 🔧 ACTUALIZAR CONTRASEÑA DEL ADMIN EN RAILWAY

## Problema
No puedes ingresar con admin/61442159 en Railway.

## Solución

### Opción 1: Esperar al Deploy (Recomendado)
El código ya está actualizado y se desplegará automáticamente. Espera 3-5 minutos y la contraseña se actualizará automáticamente cuando Railway reinicie la aplicación.

### Opción 2: Ejecutar Script Manualmente en Railway

Si el deploy no funciona, puedes ejecutar el script manualmente:

1. **Conectar a Railway CLI:**
   ```bash
   railway login
   railway link
   ```

2. **Ejecutar el script:**
   ```bash
   railway run python forzar_admin_railway_final.py
   ```

### Opción 3: Usar Railway Dashboard

1. Ve a https://railway.app/
2. Selecciona tu proyecto
3. Ve a la pestaña "Deployments"
4. Haz clic en el deployment más reciente
5. Ve a "Logs" y verifica que `init_db()` se ejecutó
6. Busca el mensaje: "✅ Contraseña del admin actualizada y verificada"

## Credenciales

- **Usuario:** `admin`
- **Contraseña:** `61442159`

## Verificación

Después de que el deploy termine, intenta ingresar con las credenciales. Si aún no funciona:

1. Verifica los logs de Railway para ver si hay errores
2. Ejecuta el script `forzar_admin_railway_final.py` manualmente
3. Verifica que la base de datos tenga el usuario admin

## Scripts Disponibles

- `forzar_admin_railway_final.py` - Actualiza la contraseña del admin en Railway
- `verificar_admin.py` - Verifica las credenciales del admin localmente
- `restablecer_admin.py` - Restablece la contraseña del admin localmente

