# SISAGENT - Sistema Multisucursal de Operaciones Bancarias

## Descripción

SISAGENT es un sistema web completo para la gestión de operaciones bancarias en múltiples sucursales. Permite registrar operaciones con montos, comisiones y medios de pago, con control de acceso por roles y seguimiento automático de comisiones diarias y mensuales.

## Características Principales

### 🔐 Gestión de Usuarios y Permisos
- **Administradores**: Pueden crear sucursales, gestionar usuarios y ver todas las operaciones
- **Usuarios**: Solo pueden registrar operaciones en su sucursal asignada
- **Control de acceso**: Los usuarios normales solo pueden ver operaciones del día actual

### 🏢 Gestión de Sucursales
- Crear, editar y eliminar sucursales
- Asignar usuarios a sucursales específicas
- Control de estado activo/inactivo

### 💰 Operaciones Bancarias
- Registro de operaciones con monto y comisión
- Medios de pago: BCP, KS, IBK, BN, AQP, NIUBIZ, CONFIANZA, BBVA, ICA, IZIPAY, CULQI, BIM
- Hora automática en zona horaria de Perú (UTC-5)
- Moneda en Soles Peruanos (S/)

### 📊 Comisiones Automáticas
- **Comisión Diaria**: Se reinicia cada día a las 00:00
- **Comisión Mensual**: Acumulativo por mes y sucursal
- Solo administradores pueden ver comisiones mensuales

### 🔍 Consultas y Filtros
- Filtros por fecha, medio de pago, hora y sucursal
- Administradores pueden consultar operaciones de cualquier fecha
- Usuarios solo pueden ver operaciones del día actual

### ✏️ Gestión de Operaciones
- Editar operaciones existentes
- Eliminar operaciones con confirmación
- Actualización automática de comisiones al editar/eliminar

### 🔔 Notificaciones
- Notificaciones pop-up con sonido
- Verde: Operación creada exitosamente
- Naranja: Operación editada exitosamente  
- Rojo: Operación eliminada exitosamente

## Instalación

### Prerrequisitos
- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd sisagent
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos MySQL
```sql
CREATE DATABASE sisagent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'sisagent_user'@'localhost' IDENTIFIED BY 'tu_password';
GRANT ALL PRIVILEGES ON sisagent.* TO 'sisagent_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configurar variables de entorno
Copiar `config.env` a `.env` y editar con tus credenciales:
```bash
cp config.env .env
```

Editar `.env`:
```env
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
DATABASE_URL=mysql+pymysql://sisagent_user:tu_password@localhost/sisagent
```

### 6. Ejecutar la aplicación
```bash
python app.py
```

La aplicación estará disponible en: http://localhost:5000

## Credenciales por Defecto

- **Usuario**: admin
- **Contraseña**: 61442159

## Estructura del Proyecto

```
sisagent/
├── app.py                 # Aplicación principal Flask
├── requirements.txt       # Dependencias de Python
├── config.env            # Configuración de entorno
├── README.md             # Documentación
├── templates/            # Plantillas HTML
│   ├── base.html         # Plantilla base
│   ├── login.html        # Página de login
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   ├── operaciones.html
│   ├── registrar_operacion.html
│   ├── editar_operacion.html
│   ├── admin_sucursales.html
│   ├── crear_sucursal.html
│   ├── editar_sucursal.html
│   ├── admin_usuarios.html
│   ├── crear_usuario.html
│   └── editar_usuario.html
└── logs/                 # Archivos de log
```

## Modelos de Base de Datos

### Usuario
- ID, username, email, password_hash
- nombre_completo, es_admin, sucursal_id
- activo, created_at

### Sucursal
- ID, nombre, direccion
- activa, created_at

### Operacion
- ID, monto, comision, medio
- hora, usuario_id, sucursal_id, created_at

### ComisionDiaria
- ID, fecha, sucursal_id, total_comision, created_at

### ComisionMensual
- ID, año, mes, sucursal_id, total_comision, created_at

## Funcionalidades por Rol

### Administrador
- ✅ Crear/editar/eliminar sucursales
- ✅ Crear/editar/eliminar usuarios
- ✅ Asignar privilegios de administrador
- ✅ Ver todas las operaciones de todas las sucursales
- ✅ Consultar operaciones de cualquier fecha
- ✅ Ver comisiones diarias y mensuales
- ✅ Editar/eliminar cualquier operación
- ✅ Modificar su propio perfil

### Usuario Normal
- ✅ Registrar operaciones en su sucursal
- ✅ Ver operaciones del día actual de su sucursal
- ✅ Ver comisión diaria de su sucursal
- ✅ Editar/eliminar sus propias operaciones
- ❌ Ver comisiones mensuales
- ❌ Consultar operaciones de otros días
- ❌ Ver operaciones de otras sucursales

## Medios de Pago Soportados

- BCP
- KS
- IBK
- BN
- AQP
- NIUBIZ
- CONFIANZA
- BBVA
- ICA
- IZIPAY
- CULQI
- BIM

## Zona Horaria

El sistema utiliza la zona horaria de Perú (UTC-5) para todas las operaciones.

## Notificaciones

El sistema incluye notificaciones pop-up con sonido para:
- ✅ Operaciones creadas (verde)
- ⚠️ Operaciones editadas (naranja)
- ❌ Operaciones eliminadas (rojo)

## Seguridad

- Contraseñas hasheadas con Werkzeug
- Control de acceso por roles
- Validación de formularios
- Protección CSRF implícita
- Sesiones seguras

## Soporte

Para soporte técnico o reportar problemas, contactar al administrador del sistema.

## Licencia

Este software es de uso interno y confidencial. 