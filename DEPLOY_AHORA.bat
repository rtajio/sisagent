@echo off
chcp 65001 >nul
echo ============================================================
echo 🚀 FORZANDO DEPLOY EN RAILWAY
echo ============================================================
echo.

cd /d "C:\Users\LENOVO\sisagent"

echo 📁 Directorio: %CD%
echo.

echo 📋 PASO 1: Verificando estado de git...
git status --short
echo.

echo 📋 PASO 2: Agregando cambios...
git add app_compatible_optimizado.py templates/operaciones.html
git add deploy_trigger.txt 2>nul
echo ✅ Archivos agregados
echo.

echo 📋 PASO 3: Haciendo commit...
git commit -m "FIX: agregar ruta API /api/operaciones/<id> PUT para edición de operaciones"
echo.

echo 📋 PASO 4: Haciendo push a GitHub (esto activará Railway)...
git push origin main
echo.

echo ============================================================
echo ✅ PUSH COMPLETADO
echo ============================================================
echo.
echo 📊 PRÓXIMOS PASOS:
echo    1. Ve al dashboard de Railway
echo    2. Revisa la pestaña "Deployments"
echo    3. Deberías ver un nuevo deploy iniciándose
echo    4. Espera 2-5 minutos para que se complete
echo.
echo ============================================================
pause

