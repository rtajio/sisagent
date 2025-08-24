# Backup Pre-Deploy Vouchers - 20250824_131706

## 📋 Información del Backup

**Fecha:** 24/08/2025 13:17:07
**Versión:** Pre-deploy Sistema de Vouchers
**Descripción:** Backup completo del sistema antes de implementar el sistema de vouchers

## 📁 Contenido del Backup

- ✅ **Base de datos:** sisagent.db
- ✅ **Archivos principales:** app.py, config.py, requirements.txt, etc.
- ✅ **Templates:** Directorio completo de templates
- ✅ **Configuraciones:** .env, .gitignore, README files
- ✅ **Instance:** Directorio de configuración local
- ✅ **Logs:** Historial de logs del sistema

## 🔄 Cómo Restaurar

1. **Detener el servidor actual**
2. **Restaurar la base de datos:**
   ```bash
   cp sisagent.db.backup sisagent.db
   ```
3. **Restaurar archivos principales:**
   ```bash
   cp app.py.backup app.py
   cp config.py.backup config.py
   # ... otros archivos
   ```
4. **Restaurar templates:**
   ```bash
   rm -rf templates
   cp -r templates.backup templates
   ```
5. **Reiniciar el servidor**

## ⚠️ Notas Importantes

- Este backup fue creado ANTES de implementar el sistema de vouchers
- Si algo sale mal, puedes restaurar completamente el sistema
- Los nuevos archivos de vouchers NO están incluidos en este backup

## 🎯 Cambios Implementados

- Sistema de vouchers para ticketeras térmicas
- Plantillas 58mm y 80mm
- Rutas para generar e imprimir vouchers
- Selección de tamaño de voucher
- Integración con sistema de operaciones

---
**Backup creado automáticamente por el sistema SISAGENT**
