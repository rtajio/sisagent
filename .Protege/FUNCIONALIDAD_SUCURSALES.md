# 🏢 Funcionalidad de Selección de Sucursales por Administradores

## 📋 Resumen

**SISAGENT** ahora permite que **solo los administradores** puedan asignar sucursales específicas a las operaciones bancarias. Los usuarios regulares están restringidos a su sucursal asignada automáticamente.

## 🎯 Características Principales

### 👑 Para Administradores
- ✅ **Selección libre** de sucursales al registrar operaciones
- ✅ **Cambio de sucursal** al editar operaciones existentes
- ✅ **Dropdown dinámico** con todas las sucursales activas
- ✅ **Validación obligatoria** de selección de sucursal
- ✅ **Transferencia automática** de comisiones entre sucursales

### 👤 Para Usuarios Regulares
- ✅ **Sucursal fija** asignada automáticamente
- ✅ **No pueden cambiar** la sucursal de las operaciones
- ✅ **Campo de solo lectura** que muestra su sucursal
- ✅ **Validación** de que tengan sucursal asignada

## 🔄 Flujo de Trabajo

### Registro de Operaciones

#### Administradores:
1. **Acceder** a "Nueva Operación"
2. **Completar** monto, comisión y medio de pago
3. **Seleccionar** sucursal del dropdown
4. **Registrar** operación
5. **Comisión** se suma automáticamente a la sucursal seleccionada

#### Usuarios Regulares:
1. **Acceder** a "Nueva Operación"
2. **Completar** monto, comisión y medio de pago
3. **Sucursal** se asigna automáticamente (campo de solo lectura)
4. **Registrar** operación
5. **Comisión** se suma automáticamente a su sucursal asignada

### Edición de Operaciones

#### Administradores:
1. **Acceder** a "Editar Operación"
2. **Modificar** cualquier campo (incluyendo sucursal)
3. **Si cambia sucursal**: comisiones se transfieren automáticamente
4. **Guardar** cambios

#### Usuarios Regulares:
1. **Acceder** a "Editar Operación"
2. **Modificar** solo monto, comisión y medio de pago
3. **Sucursal** no se puede cambiar (campo de solo lectura)
4. **Guardar** cambios

## 🎨 Interfaz de Usuario

### Formulario de Registro

#### Para Administradores:
```html
<div class="col-md-6 mb-3">
    <label class="form-label">
        <i class="fas fa-building me-1"></i>
        Sucursal
    </label>
    <select class="form-select" id="sucursal_id" name="sucursal_id" required>
        <option value="">Seleccione una sucursal</option>
        {% for sucursal in sucursales %}
        <option value="{{ sucursal.id }}">
            {{ sucursal.nombre }}
        </option>
        {% endfor %}
    </select>
    <div class="form-text">Solo los administradores pueden asignar sucursales</div>
</div>
```

#### Para Usuarios Regulares:
```html
<div class="col-md-6 mb-3">
    <label class="form-label">
        <i class="fas fa-building me-1"></i>
        Sucursal
    </label>
    <input type="text" 
           class="form-control" 
           value="{{ current_user.sucursal.nombre }}" 
           readonly 
           style="background-color: #f8f9fa;">
    <input type="hidden" name="sucursal_id" value="{{ current_user.sucursal_id }}">
    <div class="form-text">Su sucursal asignada</div>
</div>
```

### Mensajes Informativos

#### Para Administradores:
> "Esta operación se registrará en la sucursal seleccionada y la comisión se sumará automáticamente al total diario de esa sucursal."

#### Para Usuarios Regulares:
> "Esta operación se registrará en la sucursal [NOMBRE_SUCURSAL] y la comisión se sumará automáticamente al total diario."

## 🔧 Implementación Técnica

### Backend (app.py)

#### Función de Registro:
```python
@app.route('/operaciones/registrar', methods=['GET', 'POST'])
@login_required
def registrar_operacion():
    if request.method == 'POST':
        # Determinar la sucursal para la operación
        if current_user.es_admin:
            # Los administradores pueden seleccionar la sucursal
            sucursal_id = request.form.get('sucursal_id')
            if not sucursal_id:
                flash('Debe seleccionar una sucursal para la operación', 'error')
                return redirect(url_for('registrar_operacion'))
            sucursal_id = int(sucursal_id)
        else:
            # Los usuarios regulares usan su sucursal asignada
            if not current_user.sucursal_id:
                flash('Debe tener una sucursal asignada para registrar operaciones', 'error')
                return redirect(url_for('registrar_operacion'))
            sucursal_id = current_user.sucursal_id
        
        # Crear operación con la sucursal determinada
        nueva_operacion = Operacion(
            monto=monto,
            comision=comision,
            medio=medio,
            hora=hora_actual,
            usuario_id=current_user.id,
            sucursal_id=sucursal_id
        )
        
        # Actualizar comisiones para la sucursal correcta
        # ... código de actualización de comisiones
```

#### Función de Edición:
```python
@app.route('/operaciones/<int:operacion_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_operacion(operacion_id):
    if request.method == 'POST':
        # Determinar la nueva sucursal
        if current_user.es_admin:
            nueva_sucursal_id = int(request.form.get('sucursal_id'))
        else:
            nueva_sucursal_id = operacion.sucursal_id
        
        # Si cambió la sucursal, transferir comisiones
        if current_user.es_admin and nueva_sucursal_id != sucursal_anterior:
            # Restar de la sucursal anterior
            # Sumar a la nueva sucursal
            # ... código de transferencia
```

### Frontend (Templates)

#### Condicionales en Jinja2:
```html
{% if current_user.es_admin %}
    <!-- Dropdown para administradores -->
    <select class="form-select" id="sucursal_id" name="sucursal_id" required>
        <option value="">Seleccione una sucursal</option>
        {% for sucursal in sucursales %}
        <option value="{{ sucursal.id }}">
            {{ sucursal.nombre }}
        </option>
        {% endfor %}
    </select>
{% else %}
    <!-- Campo de solo lectura para usuarios -->
    <input type="text" 
           class="form-control" 
           value="{{ current_user.sucursal.nombre }}" 
           readonly>
    <input type="hidden" name="sucursal_id" value="{{ current_user.sucursal_id }}">
{% endif %}
```

## 🔒 Seguridad y Validaciones

### Validaciones Implementadas:

1. **Verificación de permisos**: Solo administradores pueden cambiar sucursales
2. **Validación de sucursal**: Administradores deben seleccionar una sucursal
3. **Verificación de asignación**: Usuarios regulares deben tener sucursal asignada
4. **Transferencia segura**: Comisiones se transfieren correctamente al cambiar sucursal

### Mensajes de Error:

- **Para administradores**: "Debe seleccionar una sucursal para la operación"
- **Para usuarios**: "Debe tener una sucursal asignada para registrar operaciones"
- **Permisos**: "No tienes permisos para editar esta operación"

## 📊 Gestión de Comisiones

### Actualización Automática:

1. **Al registrar**: Comisión se suma a la sucursal seleccionada/asignada
2. **Al editar**: Comisión se actualiza en la sucursal correspondiente
3. **Al cambiar sucursal**: Comisión se resta de la anterior y suma a la nueva
4. **Al eliminar**: Comisión se resta de la sucursal correspondiente

### Cálculos Precisos:

- **Comisiones diarias**: Se actualizan por fecha y sucursal
- **Comisiones mensuales**: Se actualizan por año, mes y sucursal
- **Manejo de decimales**: Uso de `float()` para evitar errores de tipo

## 🚀 Cómo Usar

### Para Administradores:

1. **Acceder** al sistema con credenciales de administrador
2. **Ir** a "Operaciones" → "Nueva Operación"
3. **Completar** los datos de la operación
4. **Seleccionar** la sucursal del dropdown
5. **Registrar** la operación

### Para Usuarios Regulares:

1. **Acceder** al sistema con credenciales de usuario
2. **Ir** a "Operaciones" → "Nueva Operación"
3. **Completar** los datos de la operación
4. **Verificar** que la sucursal mostrada es la correcta
5. **Registrar** la operación

## ✅ Beneficios

1. **Control granular**: Los administradores pueden asignar operaciones a cualquier sucursal
2. **Seguridad**: Los usuarios regulares están restringidos a su sucursal
3. **Flexibilidad**: Permite gestión centralizada de operaciones
4. **Precisión**: Comisiones se calculan correctamente por sucursal
5. **Auditoría**: Trazabilidad completa de operaciones por sucursal

## 🔄 Próximas Mejoras

- [ ] **Filtros por sucursal** en reportes para administradores
- [ ] **Dashboard por sucursal** con estadísticas específicas
- [ ] **Notificaciones** cuando se cambia la sucursal de una operación
- [ ] **Historial** de cambios de sucursal en operaciones
- [ ] **Exportación** de datos por sucursal

---

**SISAGENT** - Sistema de Gestión de Operaciones Bancarias
*Versión con funcionalidad de selección de sucursales por administradores* 