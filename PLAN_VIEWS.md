# Plan: SQL Views + Live Updates sin Refresh

## FASE 1: Editar Medios de Pago
- [ ] Página `/admin/medios-pago` con tabla editable
- [ ] API `/api/medios/crear`, `/api/medios/editar`, `/api/medios/eliminar`
- [ ] Live table update sin refresh

## FASE 2: SQL Views para todos los READ
### Views a crear:
1. `vista_operaciones` - operación + usuario + sucursal + medio_pago
2. `vista_ventas` - venta + producto + usuario + sucursal
3. `vista_productos` - producto + sucursal (con detalles)
4. `vista_usuarios` - usuario + rol + sucursal
5. `vista_sucursales` - sucursal (con medios_activos)
6. `vista_medios_pago` - medio + sucursales_asignadas

### Rutas a actualizar:
- `/operaciones` → usa `vista_operaciones`
- `/ventas` → usa `vista_ventas`
- `/inventario` → usa `vista_productos`
- `/admin/usuarios` → usa `vista_usuarios`
- `/admin/medios-pago` → usa `vista_medios_pago`

### Live updates (sin refresh):
- Operaciones: cada 3s
- Ventas: cada 3s
- Productos: cada 5s
- Usuarios: click actualizar
- Medios: inmediato

