# 🚀 SISAGENT - Sistema de Gestión de Operaciones Bancarias

## 📋 **Descripción**

SISAGENT es un sistema web completo para la gestión de operaciones bancarias, tareos y reportes. Desarrollado con Flask, incluye funcionalidades avanzadas para administradores y usuarios regulares.

## ✨ **Características Principales**

### 🔐 **Autenticación y Usuarios**
- Sistema de login/logout seguro
- Gestión de usuarios (admin y regulares)
- Perfiles de usuario personalizables
- Control de acceso basado en roles

### 🏢 **Gestión de Sucursales**
- CRUD completo de sucursales
- Asignación de usuarios a sucursales
- Gestión de medios de pago por sucursal

### 💰 **Operaciones Bancarias**
- Registro de operaciones con múltiples medios de pago
- Cálculo automático de comisiones
- Edición y eliminación de operaciones
- Filtros avanzados por fecha, sucursal y medio

### 📊 **Reportes y Analytics**
- Reportes detallados de operaciones
- Exportación a PDF, Excel y CSV
- Gráficos de comisiones diarias y mensuales
- Filtros por fecha y sucursal

### 📋 **Sistema de Tareos**
- Creación y gestión de tareos diarios
- Operaciones asignadas automáticamente
- Sistema de checklists con estado en tiempo real
- Aleatorización automática de montos
- Reset diario automático de estados

### 🎯 **Funcionalidades Avanzadas**
- Zona horaria de Perú (UTC-5) implementada
- Optimización de base de datos con índices
- Interfaz responsive con Bootstrap
- API RESTful para operaciones AJAX

## 🛠️ **Tecnologías Utilizadas**

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Reportes**: ReportLab, OpenPyXL
- **Despliegue**: Railway, Gunicorn

## 🚀 **Instalación y Configuración**

### **Requisitos Previos**
- Python 3.8+
- pip
- Git

### **Instalación Local**

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/sisagent.git
   cd sisagent
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   ```bash
   # Crear archivo config.env
   SECRET_KEY=tu-clave-secreta-muy-segura
   DATABASE_URL=sqlite:///sisagent_consolidada.db
   ```

4. **Inicializar base de datos**:
   ```bash
   python init_db.py
   ```

5. **Ejecutar la aplicación**:
   ```bash
   python app.py
   ```

### **Despliegue en Railway**

1. **Crear cuenta en Railway**: https://railway.app/
2. **Conectar repositorio de GitHub**
3. **Configurar variables de entorno**:
   - `SECRET_KEY`: Clave secreta para sesiones
   - `DATABASE_URL`: Se configura automáticamente

## 📁 **Estructura del Proyecto**

```
sisagent/
├── app.py                 # Aplicación principal Flask
├── wsgi.py               # Configuración WSGI para producción
├── config.py             # Configuración de la aplicación
├── init_db.py            # Inicialización de base de datos
├── requirements.txt      # Dependencias de Python
├── railway.toml          # Configuración Railway
├── Procfile              # Configuración Procfile
├── templates/            # Templates HTML
│   ├── base.html         # Template base
│   ├── login.html        # Página de login
│   ├── admin_dashboard.html
│   ├── user_dashboard.html
│   └── ...
├── static/               # Archivos estáticos (CSS, JS, imágenes)
└── backups/              # Backups del sistema
```

## 🔧 **Configuración de Base de Datos**

### **Modelos Principales**
- **Usuario**: Gestión de usuarios y autenticación
- **Sucursal**: Información de sucursales
- **Operacion**: Registro de operaciones bancarias
- **Tareo**: Sistema de tareos diarios
- **OperacionTareo**: Operaciones dentro de tareos
- **MedioPago**: Medios de pago disponibles

### **Índices Optimizados**
- Índices en tablas principales para mejor rendimiento
- Consultas optimizadas para operaciones frecuentes

## 🌐 **Rutas Principales**

### **Autenticación**
- `/login` - Página de login
- `/logout` - Cerrar sesión

### **Dashboard**
- `/admin` - Dashboard de administrador
- `/user` - Dashboard de usuario
- `/app` - Dashboard principal

### **Gestión**
- `/admin/usuarios` - Gestión de usuarios
- `/admin/sucursales` - Gestión de sucursales
- `/admin/medios` - Gestión de medios de pago
- `/admin/tareos` - Gestión de tareos

### **Operaciones**
- `/operaciones` - Lista de operaciones
- `/operaciones/registrar` - Registrar nueva operación
- `/operaciones/<id>/editar` - Editar operación

### **Tareos**
- `/tareos` - Lista de tareos del usuario
- `/tareos/<id>` - Ver tareo específico

### **Reportes**
- `/reportes` - Generar reportes
- `/api/reportes/exportar/<formato>` - Exportar reportes

### **API**
- `/api/operaciones` - API de operaciones
- `/api/tareos` - API de tareos
- `/api/comisiones` - API de comisiones

## 🔐 **Variables de Entorno**

### **Requeridas**
- `SECRET_KEY`: Clave secreta para sesiones Flask
- `DATABASE_URL`: URL de conexión a base de datos

### **Opcionales**
- `PORT`: Puerto de la aplicación (por defecto: 5000)
- `FLASK_ENV`: Entorno de Flask (development/production)

## 📊 **Funcionalidades de Tareos**

### **Para Usuarios**
- Ver tareos asignados
- Completar operaciones con checkboxes
- Ver progreso en tiempo real
- Interfaz deshabilitada para tareos de días anteriores

### **Para Administradores**
- Crear y gestionar tareos
- Editar operaciones de tareos
- Aleatorización manual de montos
- Aleatorización automática diaria
- Reset completo de estados

### **Sistema Automático**
- Detección de cambio de día
- Deshabilitación automática de checklists
- Aleatorización automática de montos
- Reset de estado a pendiente

## 🎯 **Reglas de Aleatorización**

- **BBVA**: 10-40 soles
- **KS**: 100-150 soles  
- **BN**: 10 soles (fijo)
- **Otros medios**: Mantienen monto actual

## 🔍 **Health Checks**

- `/health` - Health check básico
- `/railway-health` - Health check específico para Railway
- `/api/health` - Health check de API

## 🚀 **Despliegue**

### **Railway (Recomendado)**
1. Conectar repositorio de GitHub
2. Configurar variables de entorno
3. Despliegue automático

### **Heroku**
1. Crear aplicación Heroku
2. Conectar repositorio
3. Configurar variables de entorno

### **VPS/Dedicado**
1. Instalar dependencias del servidor
2. Configurar Gunicorn
3. Configurar Nginx (opcional)

## 📝 **Logs y Monitoreo**

- Logs de aplicación en tiempo real
- Monitoreo de base de datos
- Health checks automáticos
- Alertas de errores

## 🔒 **Seguridad**

- Autenticación segura con Flask-Login
- Protección CSRF
- Validación de entrada
- Escape de datos en templates
- Control de acceso basado en roles

## 🤝 **Contribución**

1. Fork el proyecto
2. Crear rama para nueva funcionalidad
3. Commit los cambios
4. Push a la rama
5. Crear Pull Request

## 📄 **Licencia**

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 **Soporte**

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

## 🎉 **Estado del Proyecto**

✅ **Completamente funcional**
✅ **Listo para producción**
✅ **Optimizado para Railway**
✅ **Todas las funcionalidades implementadas**

---

**SISAGENT** - Sistema de Gestión de Operaciones Bancarias
*Desarrollado con ❤️ para optimizar la gestión bancaria* 