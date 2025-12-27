#!/usr/bin/env python3
"""
SISAGENT - Sistema de Gestión de Operaciones Bancarias
VERSIÓN COMPATIBLE ULTRA OPTIMIZADA
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_caching import Cache
from flask_compress import Compress
import pytz
import time

# Configuración de zona horaria (UTC-5 para Perú)
peru_tz = pytz.timezone('America/Lima')

def get_peru_time():
    """Obtiene la hora actual en zona horaria de Perú"""
    return datetime.now(peru_tz)

# Función removida - usar db.func.date() directamente en las consultas
# Las operaciones se guardan con get_peru_time() que ya incluye la zona horaria de Perú
# PostgreSQL está configurado con timezone 'America/Lima' en las conexiones

def format_peru_time(dt):
    """Formatea una fecha/hora para mostrar en zona horaria de Perú"""
    if dt is None:
        return ""
    if dt.tzinfo is not None:
        return dt.astimezone(peru_tz).strftime('%H:%M:%S')
    else:
        return dt.replace(tzinfo=pytz.UTC).astimezone(peru_tz).strftime('%H:%M:%S')

def format_peru_date(dt):
    """Formatea una fecha para mostrar en zona horaria de Perú"""
    if dt is None:
        return ""
    if dt.tzinfo is not None:
        return dt.astimezone(peru_tz).strftime('%d/%m/%Y')
    else:
        return dt.replace(tzinfo=pytz.UTC).astimezone(peru_tz).strftime('%d/%m/%Y')

def format_peru_datetime(dt):
    """Formatea una fecha/hora completa para mostrar en zona horaria de Perú"""
    if dt is None:
        return ""
    if dt.tzinfo is not None:
        return dt.astimezone(peru_tz).strftime('%d/%m/%Y %H:%M:%S')
    else:
        return dt.replace(tzinfo=pytz.UTC).astimezone(peru_tz).strftime('%d/%m/%Y %H:%M:%S')

def format_peru_datetime_short(dt):
    """Formatea una fecha/hora corta para mostrar en zona horaria de Perú"""
    if dt is None:
        return ""
    if dt.tzinfo is not None:
        return dt.astimezone(peru_tz).strftime('%d/%m/%Y %H:%M')
    else:
        return dt.replace(tzinfo=pytz.UTC).astimezone(peru_tz).strftime('%d/%m/%Y %H:%M')

print("🚀 SISAGENT Flask COMPATIBLE ULTRA OPTIMIZADO arrancando...")
print("⚡ OPTIMIZACIONES: Caché, Compresión, Consultas optimizadas, Paginación")
print("🔄 Actualización Railway - " + get_peru_time().strftime("%Y-%m-%d %H:%M:%S"))

# Configuración de la aplicación Flask
app = Flask(__name__)

print("✅ Flask app creada")

# Configuración para Railway
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Usando PostgreSQL en Railway: {database_url[:20]}...")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_consolidada.db'
    print("✅ Usando SQLite para desarrollo local")

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# OPTIMIZACIÓN ULTRA: Configuración de caché
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutos

# OPTIMIZACIÓN ULTRA: Configuración de compresión
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'text/javascript',
    'application/json', 'application/javascript'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OPTIMIZACIÓN ULTRA: Inicializar caché y compresión
cache = Cache(app)
Compress(app)

# Context processor para exponer funciones de formato en templates
@app.context_processor
def inject_format_functions():
    return {
        'format_peru_time': format_peru_time,
        'format_peru_date': format_peru_date,
        'format_peru_datetime': format_peru_datetime,
        'format_peru_datetime_short': format_peru_datetime_short,
    }

# Manejo global de errores para debugging
@app.errorhandler(Exception)
def handle_error(e):
    import traceback
    error_msg = f"Error: {type(e).__name__}: {str(e)}"
    print("=" * 80)
    print("ERROR EN LA APLICACIÓN:")
    print(error_msg)
    print("=" * 80)
    traceback.print_exc()
    print("=" * 80)
    
    # Intentar rollback de la sesión si hay error de BD
    try:
        db.session.rollback()
    except:
        pass
    
    # Si el usuario está autenticado, redirigir al dashboard con mensaje de error
    try:
        from flask_login import current_user
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('dashboard'))
    except:
        pass
    
    # Si no está autenticado, redirigir al login
    flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('login'))

print("✅ Configuración de base de datos completada")
print("✅ SQLAlchemy y LoginManager configurados")
print("✅ Caché y compresión configurados")
print("✅ Configuración de zona horaria completada")

# Modelos de base de datos COMPATIBLES con la estructura existente
class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    activa = db.Column(db.Boolean, default=True)
    operaciones = db.relationship('Operacion', backref='sucursal', lazy='dynamic')

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=True)  # Nombre completo del usuario
    es_admin = db.Column(db.Boolean, default=False)
    es_admin_sucursal = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    # Relación con sucursal para evitar errores en templates
    sucursal = db.relationship('Sucursal', backref='usuarios', lazy='joined')
    operaciones = db.relationship('Operacion', backref='usuario', lazy='dynamic')
    
    def es_admin_de_sucursal(self):
        """Verifica si el usuario es administrador de una sucursal"""
        return self.es_admin_sucursal and self.sucursal_id is not None
    
    def es_admin_o_admin_sucursal(self):
        """Verifica si el usuario es admin global o admin de sucursal"""
        return self.es_admin or self.es_admin_de_sucursal()
    
    def puede_crear_usuario_en_sucursal(self, sucursal_id):
        """Verifica si el usuario puede crear usuarios en una sucursal específica"""
        if self.es_admin:
            return True
        if self.es_admin_de_sucursal():
            return self.sucursal_id == sucursal_id
        return False

class Operacion(db.Model):
    __tablename__ = 'operacion'
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    comision = db.Column(db.Numeric(10, 2), nullable=False)
    medio = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.DateTime, default=lambda: get_peru_time())
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)

class MedioPago(db.Model):
    __tablename__ = 'medio_pago'
    id = db.Column(db.Integer, primary_key=True)
    nombre_abreviado = db.Column(db.String(20), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)

class MedioSucursal(db.Model):
    """Tabla intermedia para la relación many-to-many entre Sucursal y MedioPago"""
    __tablename__ = 'medio_sucursal'
    id = db.Column(db.Integer, primary_key=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False, index=True)
    medio_pago_id = db.Column(db.Integer, db.ForeignKey('medio_pago.id'), nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True, index=True)
    sucursal = db.relationship('Sucursal', backref='medios_sucursal')
    medio_pago = db.relationship('MedioPago', backref='sucursales_medio')
    
    # Evitar duplicados
    __table_args__ = (db.UniqueConstraint('sucursal_id', 'medio_pago_id', name='uq_sucursal_medio'),)

class ComisionDiaria(db.Model):
    __tablename__ = 'comision_diaria'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    total_comision = db.Column(db.Numeric(10, 2), default=0.0)

class ComisionMensual(db.Model):
    __tablename__ = 'comision_mensual'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    total_comision = db.Column(db.Numeric(10, 2), default=0.0)

# OPTIMIZACIÓN ULTRA: Cache de medios de pago
@cache.memoize(timeout=300)
def get_medios_pago_cache():
    """Obtener medios de pago con caché"""
    return MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()

# OPTIMIZACIÓN ULTRA: Cache de sucursales activas
@cache.memoize(timeout=300)
def get_sucursales_activas_cache():
    """Obtener sucursales activas con caché"""
    return Sucursal.query.filter_by(activa=True).all()

# OPTIMIZACIÓN ULTRA: Cache de estadísticas del dashboard
@cache.memoize(timeout=60)
def get_dashboard_stats_cache(user_id, is_admin):
    """Obtener estadísticas del dashboard con caché"""
    ahora = get_peru_time()
    hoy = ahora.date()
    
    # Calcular rango de tiempo para el día en hora de Perú (00:00:00 a 23:59:59)
    inicio_dia = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=peru_tz)
    fin_dia = datetime.combine(hoy, datetime.max.time()).replace(tzinfo=peru_tz)
    # Ajustar fin_dia para que sea 23:59:59.999999
    fin_dia = fin_dia.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    if is_admin:
        # Estadísticas para admin - usar rango de tiempo en hora de Perú
        operaciones_hoy = db.session.query(db.func.count(Operacion.id)).filter(
            Operacion.hora >= inicio_dia,
            Operacion.hora <= fin_dia
        ).scalar() or 0
        
        total_operaciones = db.session.query(db.func.count(Operacion.id)).scalar() or 0
        
        comision_hoy = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).filter(
            Operacion.hora >= inicio_dia,
            Operacion.hora <= fin_dia
        ).scalar() or 0
        
        total_comision = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).scalar() or 0
        
        sucursales_activas = db.session.query(db.func.count(Sucursal.id)).filter_by(activa=True).scalar() or 0
        
        usuarios_total = db.session.query(db.func.count(Usuario.id)).scalar() or 0
        
    else:
        # Estadísticas para usuario normal - usar rango de tiempo en hora de Perú
        operaciones_hoy = db.session.query(db.func.count(Operacion.id)).filter(
            Operacion.usuario_id == user_id,
            Operacion.hora >= inicio_dia,
            Operacion.hora <= fin_dia
        ).scalar() or 0
        
        total_operaciones = db.session.query(db.func.count(Operacion.id)).filter(
            Operacion.usuario_id == user_id
        ).scalar() or 0
        
        comision_hoy = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).filter(
            Operacion.usuario_id == user_id,
            Operacion.hora >= inicio_dia,
            Operacion.hora <= fin_dia
        ).scalar() or 0
        
        total_comision = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).filter(
            Operacion.usuario_id == user_id
        ).scalar() or 0
        
        sucursales_activas = 1  # Usuario normal solo ve su sucursal
        usuarios_total = 1  # Usuario normal solo se ve a sí mismo
    
    return {
        'operaciones_hoy': operaciones_hoy,
        'total_operaciones': total_operaciones,
        'comision_hoy': float(comision_hoy),
        'total_comision': float(total_comision),
        'sucursales_activas': sucursales_activas,
        'usuarios_total': usuarios_total
    }

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# OPTIMIZACIÓN ULTRA: Función para limpiar caché
def clear_cache():
    """Limpiar todo el caché"""
    cache.clear()

def asegurar_admin_existe():
    """Asegurar que el usuario admin exista con la contraseña 'vivalavida'"""
    try:
        admin = Usuario.query.filter_by(username='admin').first()
        password_hash = generate_password_hash('vivalavida')
        
        if not admin:
            # Crear admin si no existe
            admin = Usuario(
                username='admin',
                password_hash=password_hash,
                es_admin=True,
                es_admin_sucursal=False
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuario 'admin' creado con contraseña 'vivalavida'")
        else:
            # Actualizar contraseña y asegurar que es admin
            admin.password_hash = password_hash
            admin.es_admin = True
            admin.es_admin_sucursal = False
            db.session.commit()
            print("✅ Usuario 'admin' actualizado con contraseña 'vivalavida'")
    except Exception as e:
        print(f"⚠️  Error al asegurar admin: {e}")
        db.session.rollback()

# Rutas optimizadas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Asegurar que el admin exista antes de procesar el login
    try:
        asegurar_admin_existe()
    except:
        pass
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            # Limpiar caché al hacer login
            clear_cache()
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Redirige al dashboard según rol usando templates existentes"""
    try:
        stats = get_dashboard_stats_cache(current_user.id, current_user.es_admin)
        base_ctx = {
            'total_sucursales': stats.get('sucursales_activas', 0),
            'total_usuarios': stats.get('usuarios_total', 0),
            'comisiones_hoy': [],
            'comisiones_mes': {},
            **stats,
        }

        if current_user.es_admin:
            # Calcular comisiones por sucursal (día y mes) para admin global
            ahora = get_peru_time()
            hoy = ahora.date()
            año_actual = ahora.year
            mes_actual = ahora.month
            
            # Calcular rango de tiempo para hoy en hora de Perú (00:00:00 a 23:59:59)
            inicio_hoy = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=peru_tz)
            fin_hoy = datetime.combine(hoy, datetime.max.time()).replace(tzinfo=peru_tz)
            fin_hoy = fin_hoy.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Calcular rango de tiempo para el mes (desde el primer día del mes hasta hoy)
            inicio_mes = datetime.combine(datetime(año_actual, mes_actual, 1).date(), datetime.min.time()).replace(tzinfo=peru_tz)

            # Obtener todas las sucursales activas
            sucursales_activas = Sucursal.query.filter_by(activa=True).all()
            
            # Obtener comisiones del día por sucursal
            comisiones_hoy_query = db.session.query(
                Operacion.sucursal_id,
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0).label('total')
            ).filter(
                Operacion.hora >= inicio_hoy,
                Operacion.hora <= fin_hoy
            ).group_by(Operacion.sucursal_id).all()
            
            comisiones_hoy_dict = {suc_id: float(total) for suc_id, total in comisiones_hoy_query}

            # Obtener comisiones del mes por sucursal
            comisiones_mes_query = db.session.query(
                Operacion.sucursal_id,
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0).label('total')
            ).filter(
                Operacion.hora >= inicio_mes,
                Operacion.hora <= fin_hoy
            ).group_by(Operacion.sucursal_id).all()
            
            comisiones_mes_dict = {suc_id: float(total) for suc_id, total in comisiones_mes_query}

            # Crear lista con todas las sucursales, incluso si no tienen comisiones
            comisiones_hoy_list = []
            comisiones_mes_dict_final = {}
            
            for sucursal in sucursales_activas:
                comision_hoy = comisiones_hoy_dict.get(sucursal.id, 0.0)
                comision_mes = comisiones_mes_dict.get(sucursal.id, 0.0)
                comisiones_hoy_list.append((sucursal.id, sucursal.nombre, comision_hoy))
                comisiones_mes_dict_final[sucursal.id] = comision_mes

            base_ctx['comisiones_hoy'] = comisiones_hoy_list
            base_ctx['comisiones_mes'] = comisiones_mes_dict_final

            return render_template('admin_dashboard.html', **base_ctx)
        elif current_user.es_admin_de_sucursal():
            # Dashboard para administrador de sucursal
            ahora = get_peru_time()
            hoy = ahora.date()
            año_actual = ahora.year
            mes_actual = ahora.month
            
            # Calcular rango de tiempo para hoy en hora de Perú (00:00:00 a 23:59:59)
            inicio_hoy = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=peru_tz)
            fin_hoy = datetime.combine(hoy, datetime.max.time()).replace(tzinfo=peru_tz)
            fin_hoy = fin_hoy.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Calcular rango de tiempo para el mes (desde el primer día del mes hasta hoy)
            inicio_mes = datetime.combine(datetime(año_actual, mes_actual, 1).date(), datetime.min.time()).replace(tzinfo=peru_tz)
            
            sucursal_id = current_user.sucursal_id
            
            # Obtener comisiones del día para la sucursal
            comision_hoy = db.session.query(
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
            ).filter(
                Operacion.sucursal_id == sucursal_id,
                Operacion.hora >= inicio_hoy,
                Operacion.hora <= fin_hoy
            ).scalar() or 0.0
            
            # Obtener comisiones del mes para la sucursal
            comision_mes = db.session.query(
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
            ).filter(
                Operacion.sucursal_id == sucursal_id,
                Operacion.hora >= inicio_mes,
                Operacion.hora <= fin_hoy
            ).scalar() or 0.0
            
            # Obtener usuarios de la sucursal
            usuarios_sucursal = Usuario.query.filter_by(sucursal_id=sucursal_id).all()
            
            # Calcular comisiones por usuario del día
            comisiones_usuarios_hoy = []
            for usuario in usuarios_sucursal:
                comision_usuario_hoy = db.session.query(
                    db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
                ).filter(
                    Operacion.usuario_id == usuario.id,
                    Operacion.hora >= inicio_hoy,
                    Operacion.hora <= fin_hoy
                ).scalar() or 0.0
                comisiones_usuarios_hoy.append({
                    'usuario_id': usuario.id,
                    'nombre': usuario.nombre_completo or usuario.username,
                    'comision': float(comision_usuario_hoy)
                })
            
            base_ctx['comision_hoy'] = float(comision_hoy)
            base_ctx['comision_mes'] = float(comision_mes)
            base_ctx['usuarios_sucursal'] = usuarios_sucursal
            base_ctx['comisiones_usuarios_hoy'] = comisiones_usuarios_hoy
            base_ctx['sucursal'] = current_user.sucursal
            
            return render_template('admin_sucursal_dashboard.html', **base_ctx)
        else:
            # Para usuarios normales: agregar variables que el template espera
            ahora = get_peru_time()
            hoy = ahora.date()
            # Calcular rango de tiempo para el día en hora de Perú (00:00:00 a 23:59:59)
            inicio_dia = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=peru_tz)
            fin_dia = datetime.combine(hoy, datetime.max.time()).replace(tzinfo=peru_tz)
            fin_dia = fin_dia.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            base_ctx['total_comision_hoy'] = stats.get('comision_hoy', 0.0)
            # Obtener operaciones del día para el usuario usando rango de tiempo
            operaciones_hoy_list = Operacion.query.filter(
                Operacion.usuario_id == current_user.id,
                Operacion.hora >= inicio_dia,
                Operacion.hora <= fin_dia
            ).order_by(Operacion.hora.desc()).limit(10).all()
            base_ctx['operaciones_hoy'] = operaciones_hoy_list
            return render_template('user_dashboard.html', **base_ctx)
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Respuesta explícita para depurar en producción
        return f"Error en dashboard: {str(e)}", 500

@app.route('/operaciones')
@login_required
def operaciones():
    # OPTIMIZACIÓN ULTRA: Paginación para operaciones
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Reducido para mayor velocidad
    
    # Obtener parámetros de filtro
    fecha = request.args.get('fecha')
    medio = request.args.get('medio')
    hora_inicio = request.args.get('hora_inicio')
    hora_fin = request.args.get('hora_fin')
    
    # Query base optimizada según el rol del usuario
    if current_user.es_admin:
        # Admin global: puede ver todas las operaciones
        query = Operacion.query
        if request.args.get('sucursal_id'):
            query = query.filter_by(sucursal_id=request.args.get('sucursal_id'))
    elif current_user.es_admin_de_sucursal():
        # Admin de sucursal: puede ver operaciones de su sucursal
        query = Operacion.query.filter_by(sucursal_id=current_user.sucursal_id)
    else:
        # Usuario normal: solo puede ver sus propias operaciones
        query = Operacion.query.filter_by(usuario_id=current_user.id)
    
    # Obtener fecha actual para comparación en hora de Perú
    ahora = get_peru_time()
    hoy = ahora.date()
    
    # Calcular rango de tiempo para hoy en hora de Perú (00:00:00 a 23:59:59)
    inicio_hoy = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=peru_tz)
    fin_hoy = datetime.combine(hoy, datetime.max.time()).replace(tzinfo=peru_tz)
    fin_hoy = fin_hoy.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    # Aplicar filtros
    if fecha:
        fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d').date()
        if not current_user.es_admin_o_admin_sucursal() and fecha_objeto != hoy:
            flash('Solo los administradores pueden consultar operaciones de otros días', 'warning')
            fecha = None
        
        if fecha:
            # Usar rango de tiempo para la fecha específica en hora de Perú
            inicio_fecha = datetime.combine(fecha_objeto, datetime.min.time()).replace(tzinfo=peru_tz)
            fin_fecha = datetime.combine(fecha_objeto, datetime.max.time()).replace(tzinfo=peru_tz)
            fin_fecha = fin_fecha.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(
                Operacion.hora >= inicio_fecha,
                Operacion.hora <= fin_fecha
            )
    
    if not fecha or not current_user.es_admin_o_admin_sucursal():
        # Usar rango de tiempo para hoy en hora de Perú
        query = query.filter(
            Operacion.hora >= inicio_hoy,
            Operacion.hora <= fin_hoy
        )
    
    if medio:
        query = query.filter(Operacion.medio == medio)
    
    if hora_inicio:
        query = query.filter(Operacion.hora >= hora_inicio)
    
    if hora_fin:
        query = query.filter(Operacion.hora <= hora_fin)
    
    # OPTIMIZACIÓN ULTRA: Paginación
    operaciones_paginated = query.order_by(Operacion.hora.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Detectar si hay filtros aplicados
    filtros_aplicados = bool(fecha or medio or hora_inicio or hora_fin or (current_user.es_admin and request.args.get('sucursal_id')))
    
    # OPTIMIZACIÓN ULTRA: Cargar sucursales solo si es admin global
    sucursales = []
    if current_user.es_admin:
        sucursales = get_sucursales_activas_cache()
    
    # OPTIMIZACIÓN ULTRA: Cargar medios de pago con caché
    medios_pago = get_medios_pago_cache()
    
    return render_template('operaciones.html',
                         operaciones=operaciones_paginated.items,
                         pagination=operaciones_paginated,
                         fecha_actual=fecha or datetime.now(peru_tz).strftime('%Y-%m-%d'),
                         fecha_hoy=datetime.now(peru_tz).strftime('%Y-%m-%d'),
                         filtros_aplicados=filtros_aplicados,
                         sucursales=sucursales,
                         medios_pago=medios_pago)

@app.route('/operaciones/<int:operacion_id>/eliminar', methods=['POST'])
@login_required
def eliminar_operacion(operacion_id):
    """Eliminar operación; admin puede todas, usuario solo las suyas o de su sucursal."""
    operacion = Operacion.query.get_or_404(operacion_id)
    if not current_user.es_admin:
        # Restringir a sucursal y, si no es admin de sucursal, a su propio registro
        if operacion.sucursal_id != current_user.sucursal_id:
            flash('No tienes permisos para eliminar esta operación', 'error')
            return redirect(url_for('operaciones'))
        if not current_user.es_admin_de_sucursal() and operacion.usuario_id != current_user.id:
            flash('No tienes permisos para eliminar esta operación', 'error')
            return redirect(url_for('operaciones'))
    db.session.delete(operacion)
    db.session.commit()
    flash('Operación eliminada', 'success')
    return redirect(url_for('operaciones'))


@app.route('/operaciones/registrar', methods=['GET', 'POST'])
@login_required
def registrar_operacion():
    if request.method == 'POST':
        monto = float(request.form['monto'])
        comision = float(request.form['comision'])
        medio = request.form['medio']
        
        # Determinar sucursal
        if current_user.es_admin:
            sucursal_id = int(request.form.get('sucursal_id'))
        else:
            sucursal_id = current_user.sucursal_id
        
        # Crear operación con hora explícita de Perú
        hora_peru = get_peru_time()
        operacion = Operacion(
            monto=monto,
            comision=comision,
            medio=medio,
            usuario_id=current_user.id,
            sucursal_id=sucursal_id,
            hora=hora_peru  # Asegurar que se guarde con hora de Perú
        )
        
        db.session.add(operacion)
        
        # Actualizar comisiones
        hoy = get_peru_time().date()
        comision_diaria = ComisionDiaria.query.filter_by(
            fecha=hoy,
            sucursal_id=sucursal_id
        ).first()
        
        if comision_diaria:
            comision_diaria.total_comision = float(comision_diaria.total_comision) + comision
        else:
            comision_diaria = ComisionDiaria(
                fecha=hoy,
                sucursal_id=sucursal_id,
                total_comision=comision
            )
            db.session.add(comision_diaria)
        
        # Actualizar comisión mensual
        ahora = get_peru_time()
        año_actual = ahora.year
        mes_actual = ahora.month
        
        comision_mensual = ComisionMensual.query.filter_by(
            año=año_actual,
            mes=mes_actual,
            sucursal_id=sucursal_id
        ).first()
        
        if comision_mensual:
            comision_mensual.total_comision = float(comision_mensual.total_comision) + comision
        else:
            comision_mensual = ComisionMensual(
                año=año_actual,
                mes=mes_actual,
                sucursal_id=sucursal_id,
                total_comision=comision
            )
            db.session.add(comision_mensual)
        
        db.session.commit()
        
        # Limpiar caché después de cambios
        clear_cache()
        
        flash('Operación bancaria registrada exitosamente', 'success')
        return redirect(url_for('operaciones'))
    
    # OPTIMIZACIÓN ULTRA: Cargar sucursales solo si es admin
    sucursales = []
    if current_user.es_admin:
        sucursales = get_sucursales_activas_cache()
    
    return render_template('registrar_operacion.html', sucursales=sucursales)

@app.route('/operaciones/<int:operacion_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_operacion(operacion_id):
    operacion = Operacion.query.get_or_404(operacion_id)
    
    if not current_user.es_admin and operacion.usuario_id != current_user.id:
        flash('No tienes permisos para editar esta operación', 'error')
        return redirect(url_for('operaciones'))
    
    if request.method == 'POST':
        monto_anterior = float(operacion.comision)
        sucursal_anterior = operacion.sucursal_id
        monto = float(request.form['monto'])
        comision = float(request.form['comision'])
        medio = request.form['medio']
        
        if current_user.es_admin:
            nueva_sucursal_id = int(request.form.get('sucursal_id'))
        else:
            nueva_sucursal_id = operacion.sucursal_id
        
        # Actualizar operación
        operacion.monto = monto
        operacion.comision = comision
        operacion.medio = medio
        operacion.sucursal_id = nueva_sucursal_id
        
        # Actualizar comisiones (lógica simplificada)
        db.session.commit()
        
        # Limpiar caché después de cambios
        clear_cache()
        
        flash('Operación actualizada exitosamente', 'success')
        return redirect(url_for('operaciones'))
    
    # OPTIMIZACIÓN ULTRA: Cargar sucursales solo si es admin

@app.route('/api/operaciones/<int:operacion_id>', methods=['PUT'])
@login_required
def api_actualizar_operacion(operacion_id):
    """API para actualizar operaciones (edición inline)"""
    try:
        # Obtener la operación
        operacion = Operacion.query.get_or_404(operacion_id)
        
        # Verificar permisos
        if not current_user.es_admin:
            # Si no es admin, verificar que sea el dueño o admin de sucursal
            if operacion.usuario_id != current_user.id:
                if not current_user.es_admin_de_sucursal() or operacion.sucursal_id != current_user.sucursal_id:
                    return jsonify({'success': False, 'message': 'No tienes permisos para editar esta operación'}), 403
        
        # Obtener datos del JSON
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400
        
        monto = data.get('monto')
        comision = data.get('comision')
        medio = data.get('medio')
        
        # Validar datos
        if monto is None or comision is None or not medio:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400
        
        try:
            monto = float(monto)
            comision = float(comision)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Monto y comisión deben ser números válidos'}), 400
        
        if monto <= 0:
            return jsonify({'success': False, 'message': 'El monto debe ser mayor a 0'}), 400
        
        if comision < 0:
            return jsonify({'success': False, 'message': 'La comisión no puede ser negativa'}), 400
        
        # Validar medio de pago
        medio_valido = MedioPago.query.filter_by(nombre_abreviado=medio, activo=True).first()
        if not medio_valido:
            return jsonify({'success': False, 'message': 'Medio de pago no válido'}), 400
        
        # Actualizar operación
        operacion.monto = monto
        operacion.comision = comision
        operacion.medio = medio
        
        db.session.commit()
        
        # Limpiar caché después de cambios
        clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Operación actualizada exitosamente',
            'monto': float(monto),
            'comision': float(comision),
            'medio': medio
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({'success': False, 'message': f'Error al actualizar la operación: {str(e)}'}), 500
    
    # OPTIMIZACIÓN ULTRA: Cargar sucursales solo si es admin
    sucursales = []
    if current_user.es_admin:
        sucursales = get_sucursales_activas_cache()
    
    return render_template('editar_operacion.html', operacion=operacion, sucursales=sucursales)

# Rutas de administración optimizadas
@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not current_user.es_admin_o_admin_sucursal():
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    # OPTIMIZACIÓN ULTRA: Paginación para usuarios
    page = request.args.get('page', 1, type=int)
    query = Usuario.query
    
    # Si es admin de sucursal, filtrar solo usuarios de su sucursal
    if current_user.es_admin_de_sucursal() and not current_user.es_admin:
        query = query.filter_by(sucursal_id=current_user.sucursal_id)
    
    usuarios_paginated = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin_usuarios.html', 
                         usuarios=usuarios_paginated.items,
                         pagination=usuarios_paginated)

@app.route('/admin/usuarios/crear', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if not current_user.es_admin_o_admin_sucursal():
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        nombre_completo = request.form.get('nombre_completo', '').strip()
        
        # Si es admin de sucursal, asignar automáticamente a su sucursal
        if current_user.es_admin_de_sucursal() and not current_user.es_admin:
            sucursal_id = current_user.sucursal_id
            es_admin = False
            es_admin_sucursal = False
        else:
            # Admin global puede asignar sucursal y roles
            sucursal_id = request.form.get('sucursal_id')
            sucursal_id = int(sucursal_id) if sucursal_id else None
            es_admin = 'es_admin' in request.form
            es_admin_sucursal = 'es_admin_sucursal' in request.form
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            sucursales = Sucursal.query.filter_by(activa=True).all() if current_user.es_admin else []
            return render_template('crear_usuario.html', sucursales=sucursales)
        
        nuevo_usuario = Usuario(
            username=username,
            password_hash=generate_password_hash(password),
            nombre_completo=nombre_completo,
            sucursal_id=sucursal_id,
            es_admin=es_admin,
            es_admin_sucursal=es_admin_sucursal
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('admin_usuarios'))
    
    # Obtener sucursales disponibles
    if current_user.es_admin:
        sucursales = Sucursal.query.filter_by(activa=True).all()
    else:
        # Admin de sucursal solo puede ver su sucursal
        sucursales = [current_user.sucursal] if current_user.sucursal else []
    
    return render_template('crear_usuario.html', sucursales=sucursales)

@app.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    if not current_user.es_admin_o_admin_sucursal():
        flash('Acceso denegado', 'error')
        return redirect(url_for('admin_usuarios'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Si es admin de sucursal, solo puede editar usuarios de su sucursal
    if current_user.es_admin_de_sucursal() and not current_user.es_admin:
        if usuario.sucursal_id != current_user.sucursal_id:
            flash('No tienes permisos para editar este usuario', 'error')
            return redirect(url_for('admin_usuarios'))
    
    if request.method == 'POST':
        nuevo_username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        nombre_completo = request.form.get('nombre_completo', '').strip()
        
        if nuevo_username:
            usuario.username = nuevo_username
        if password:
            usuario.password_hash = generate_password_hash(password)
        if nombre_completo:
            usuario.nombre_completo = nombre_completo
        
        # Solo admin global puede cambiar sucursal y roles
        if current_user.es_admin:
            sucursal_id = request.form.get('sucursal_id')
            if sucursal_id:
                usuario.sucursal_id = int(sucursal_id)
            usuario.es_admin = 'es_admin' in request.form
            usuario.es_admin_sucursal = 'es_admin_sucursal' in request.form
        else:
            # Admin de sucursal solo puede asegurar que el usuario esté en su sucursal
            usuario.sucursal_id = current_user.sucursal_id
        
        db.session.commit()
        flash('Usuario actualizado', 'success')
        return redirect(url_for('admin_usuarios'))
    
    sucursales = Sucursal.query.filter_by(activa=True).all() if current_user.es_admin else [current_user.sucursal] if current_user.sucursal else []
    return render_template('editar_usuario.html', usuario=usuario, sucursales=sucursales)

# Rutas mínimas para medios de pago (compatibilidad)
@app.route('/admin/medios')
@login_required
def admin_medios():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medios = MedioPago.query.order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    return render_template('admin_medios.html', medios=medios)

@app.route('/admin/medios/<int:medio_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_medio(medio_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    if request.method == 'POST':
        abreviado = request.form.get('nombre_abreviado', '').strip()
        completo = request.form.get('nombre_completo', '').strip()
        if abreviado and completo:
            medio.nombre_abreviado = abreviado
            medio.nombre_completo = completo
            db.session.commit()
            flash('Medio actualizado', 'success')
            return redirect(url_for('admin_medios'))
    return render_template('editar_medio.html', medio=medio)

@app.route('/admin/medios/<int:medio_id>/eliminar', methods=['POST'])
@login_required
def eliminar_medio(medio_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    db.session.delete(medio)
    db.session.commit()
    flash('Medio eliminado', 'success')
    return redirect(url_for('admin_medios'))

@app.route('/admin/medios/<int:medio_id>/activar', methods=['POST'])
@login_required
def activar_medio(medio_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    medio.activo = not medio.activo
    db.session.commit()
    return redirect(url_for('admin_medios'))

@app.route('/admin/medios/<int:medio_id>/subir', methods=['POST'])
@login_required
def subir_medio(medio_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    return redirect(url_for('admin_medios'))

@app.route('/admin/medios/<int:medio_id>/bajar', methods=['POST'])
@login_required
def bajar_medio(medio_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    return redirect(url_for('admin_medios'))

@app.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    """Eliminar usuario: solo admin global; protege admin/admin1."""
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('admin_usuarios'))
    usuario = Usuario.query.get_or_404(usuario_id)
    if usuario.username in ('admin', 'admin1'):
        flash('No se puede eliminar este usuario', 'warning')
        return redirect(url_for('admin_usuarios'))
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado', 'success')
    return redirect(url_for('admin_usuarios'))


@app.route('/admin/sucursales')
@login_required
def admin_sucursales():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Consulta segura de sucursales
        sucursales = Sucursal.query.filter_by(activa=True).all()
        
        # Pre-calcular conteos de forma segura
        for s in sucursales:
            try:
                s._usuarios_count = db.session.query(db.func.count(Usuario.id)).filter(
                    Usuario.sucursal_id == s.id
                ).scalar() or 0
            except Exception as e:
                print(f"Error contando usuarios para sucursal {s.id}: {e}")
                s._usuarios_count = 0
            
            try:
                s._operaciones_count = db.session.query(db.func.count(Operacion.id)).filter(
                    Operacion.sucursal_id == s.id
                ).scalar() or 0
            except Exception as e:
                print(f"Error contando operaciones para sucursal {s.id}: {e}")
                s._operaciones_count = 0
        
        return render_template('admin_sucursales.html', sucursales=sucursales)
    except Exception as e:
        import traceback
        error_msg = f"ERROR en admin_sucursales: {type(e).__name__}: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        try:
            db.session.rollback()
        except:
            pass
        flash(f'Error al cargar sucursales: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/admin/sucursales/crear', methods=['GET', 'POST'])
@login_required
def crear_sucursal():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        direccion = request.form.get('direccion', '').strip()
        if not nombre:
            flash('El nombre es requerido', 'error')
            medios = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
            return render_template('crear_sucursal.html', medios=medios)
        if Sucursal.query.filter_by(nombre=nombre).first():
            flash('Ya existe una sucursal con ese nombre', 'warning')
            medios = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
            return render_template('crear_sucursal.html', medios=medios)
        suc = Sucursal(nombre=nombre, direccion=direccion, activa=True)
        db.session.add(suc)
        db.session.flush()  # Para obtener el ID de la sucursal
        
        # Manejar medios de pago seleccionados
        medios_seleccionados = request.form.getlist('medios')
        medios_seleccionados = [int(m) for m in medios_seleccionados if m]
        
        # Obtener todos los medios de pago activos
        todos_medios = MedioPago.query.filter_by(activo=True).all()
        
        # Crear relaciones con medios de pago seleccionados
        for medio in todos_medios:
            if medio.id in medios_seleccionados:
                medio_sucursal = MedioSucursal(
                    sucursal_id=suc.id,
                    medio_pago_id=medio.id,
                    activo=True
                )
                db.session.add(medio_sucursal)
        
        db.session.commit()
        flash('Sucursal creada', 'success')
        return redirect(url_for('admin_sucursales'))
    
    # Obtener todos los medios de pago activos para el formulario
    medios = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    return render_template('crear_sucursal.html', medios=medios)

@app.route('/admin/sucursales/<int:sucursal_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_sucursal(sucursal_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    suc = Sucursal.query.get_or_404(sucursal_id)
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        direccion = request.form.get('direccion', '').strip()
        activa = 'activa' in request.form
        
        if nombre:
            suc.nombre = nombre
        suc.direccion = direccion
        suc.activa = activa
        
        # Manejar medios de pago seleccionados
        medios_seleccionados = request.form.getlist('medios')
        medios_seleccionados = [int(m) for m in medios_seleccionados if m]
        
        # Obtener todos los medios de pago activos
        todos_medios = MedioPago.query.filter_by(activo=True).all()
        
        # Actualizar la relación con medios de pago
        for medio in todos_medios:
            medio_sucursal = MedioSucursal.query.filter_by(
                sucursal_id=suc.id,
                medio_pago_id=medio.id
            ).first()
            
            if medio.id in medios_seleccionados:
                # Debe estar activo
                if not medio_sucursal:
                    # Crear nueva relación
                    medio_sucursal = MedioSucursal(
                        sucursal_id=suc.id,
                        medio_pago_id=medio.id,
                        activo=True
                    )
                    db.session.add(medio_sucursal)
                else:
                    # Activar si estaba desactivado
                    medio_sucursal.activo = True
            else:
                # Debe estar desactivado
                if medio_sucursal:
                    medio_sucursal.activo = False
                # Si no existe, no crear (solo desactivar si existe)
        
        db.session.commit()
        flash('Sucursal actualizada', 'success')
        return redirect(url_for('admin_sucursales'))
    
    # Obtener medios de pago activos para esta sucursal
    medios_activos = db.session.query(MedioSucursal.medio_pago_id).filter_by(
        sucursal_id=suc.id,
        activo=True
    ).all()
    medios_activos_ids = [m[0] for m in medios_activos]
    
    # Obtener todos los medios de pago activos
    medios = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    
    return render_template('editar_sucursal.html', 
                         sucursal=suc, 
                         medios=medios, 
                         medios_activos=medios_activos_ids)

@app.route('/admin/sucursales/<int:sucursal_id>/eliminar', methods=['POST'])
@login_required
def eliminar_sucursal(sucursal_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    suc = Sucursal.query.get_or_404(sucursal_id)
    db.session.delete(suc)
    db.session.commit()
    flash('Sucursal eliminada', 'success')
    return redirect(url_for('admin_sucursales'))

@app.route('/reportes')
@login_required
def reportes():
    """Página de reportes para administradores."""
    if not current_user.es_admin_o_admin_sucursal():
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener sucursales y medios de pago
    if current_user.es_admin:
        sucursales = get_sucursales_activas_cache()
    else:
        # Admin de sucursal solo ve su sucursal
        sucursales = [current_user.sucursal] if current_user.sucursal else []
    
    medios_pago = get_medios_pago_cache()
    
    return render_template('reportes.html', sucursales=sucursales, medios_pago=medios_pago)

@app.route('/api/reportes/operaciones')
@login_required
def api_reportes_operaciones():
    """API para generar reportes de operaciones con filtros."""
    try:
        if not current_user.es_admin_o_admin_sucursal():
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        sucursal_id = request.args.get('sucursal_id')
        medio = request.args.get('medio')
        
        query = Operacion.query
        
        # Si es admin de sucursal, filtrar automáticamente por su sucursal (ignorar parámetro sucursal_id)
        if current_user.es_admin_de_sucursal() and not current_user.es_admin:
            if current_user.sucursal_id:
                query = query.filter(Operacion.sucursal_id == current_user.sucursal_id)
        elif sucursal_id and sucursal_id.strip():
            # Solo aplicar filtro de sucursal si es admin global
            try:
                sucursal_id_int = int(sucursal_id)
                query = query.filter(Operacion.sucursal_id == sucursal_id_int)
            except ValueError:
                pass  # Ignorar si no se puede convertir
        
        # Aplicar filtros de fecha usando rangos de tiempo en hora de Perú
        if fecha_inicio:
            fecha_inicio_obj = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            inicio_fecha = datetime.combine(fecha_inicio_obj, datetime.min.time()).replace(tzinfo=peru_tz)
            query = query.filter(Operacion.hora >= inicio_fecha)
        
        if fecha_fin:
            fecha_fin_obj = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            fin_fecha = datetime.combine(fecha_fin_obj, datetime.max.time()).replace(tzinfo=peru_tz)
            fin_fecha = fin_fecha.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(Operacion.hora <= fin_fecha)
        
        if medio:
            query = query.filter(Operacion.medio == medio)
        
        # Cache de medios de pago
        medios_cache = {mp.nombre_abreviado: mp.nombre_completo for mp in MedioPago.query.filter_by(activo=True).all()}
        
        # Obtener todas las operaciones sin límite (según filtros aplicados)
        # Usar joinedload para cargar relaciones de forma eficiente
        from sqlalchemy.orm import joinedload
        operaciones = query.options(
            joinedload(Operacion.usuario).load_only(Usuario.id, Usuario.username, Usuario.nombre_completo),
            joinedload(Operacion.sucursal).load_only(Sucursal.id, Sucursal.nombre)
        ).order_by(Operacion.hora.desc()).all()
        
        # Procesar datos
        datos = []
        total_monto = 0.0
        total_comision = 0.0
        
        for op in operaciones:
            monto = float(op.monto)
            comision = float(op.comision)
            total_monto += monto
            total_comision += comision
            
            # Obtener datos de usuario y sucursal de forma segura
            usuario_nombre = 'N/A'
            if hasattr(op, 'usuario') and op.usuario:
                usuario_nombre = op.usuario.nombre_completo if op.usuario.nombre_completo else op.usuario.username
            
            sucursal_nombre = 'Sin sucursal'
            if hasattr(op, 'sucursal') and op.sucursal:
                sucursal_nombre = op.sucursal.nombre
            
            datos.append({
                'id': op.id,
                'fecha': format_peru_date(op.hora),
                'hora': format_peru_time(op.hora),
                'monto': monto,
                'comision': comision,
                'medio': medios_cache.get(op.medio, op.medio),
                'usuario': usuario_nombre,
                'sucursal': sucursal_nombre
            })
        
        return jsonify({
            'operaciones': datos,
            'total_operaciones': len(operaciones),
            'total_monto': total_monto,
            'total_comision': total_comision
        })
    except Exception as e:
        import traceback
        error_msg = f"Error al generar reporte: {type(e).__name__}: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({'error': str(e)}), 500

# Healthcheck optimizado
@app.route('/api/dashboard/comisiones')
@login_required
def api_dashboard_comisiones():
    """API para obtener comisiones actualizadas del dashboard"""
    try:
        if not current_user.es_admin:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        ahora = get_peru_time()
        hoy = ahora.date()
        año_actual = ahora.year
        mes_actual = ahora.month
        
        # Calcular rango de tiempo para hoy en hora de Perú (00:00:00 a 23:59:59)
        inicio_hoy = datetime.combine(hoy, datetime.min.time()).replace(tzinfo=peru_tz)
        fin_hoy = datetime.combine(hoy, datetime.max.time()).replace(tzinfo=peru_tz)
        fin_hoy = fin_hoy.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Calcular rango de tiempo para el mes (desde el primer día del mes hasta hoy)
        inicio_mes = datetime.combine(datetime(año_actual, mes_actual, 1).date(), datetime.min.time()).replace(tzinfo=peru_tz)
        
        # Obtener todas las sucursales activas
        sucursales_activas = Sucursal.query.filter_by(activa=True).all()
        
        # Obtener comisiones del día por sucursal
        comisiones_hoy_query = db.session.query(
            Operacion.sucursal_id,
            db.func.coalesce(db.func.sum(Operacion.comision), 0.0).label('total')
        ).filter(
            Operacion.hora >= inicio_hoy,
            Operacion.hora <= fin_hoy
        ).group_by(Operacion.sucursal_id).all()
        
        comisiones_hoy_dict = {suc_id: float(total) for suc_id, total in comisiones_hoy_query}
        
        # Obtener comisiones del mes por sucursal
        comisiones_mes_query = db.session.query(
            Operacion.sucursal_id,
            db.func.coalesce(db.func.sum(Operacion.comision), 0.0).label('total')
        ).filter(
            Operacion.hora >= inicio_mes,
            Operacion.hora <= fin_hoy
        ).group_by(Operacion.sucursal_id).all()
        
        comisiones_mes_dict = {suc_id: float(total) for suc_id, total in comisiones_mes_query}
        
        # Crear lista con todas las sucursales
        comisiones_list = []
        total_comision_hoy = 0.0
        
        for sucursal in sucursales_activas:
            comision_hoy = comisiones_hoy_dict.get(sucursal.id, 0.0)
            comision_mes = comisiones_mes_dict.get(sucursal.id, 0.0)
            total_comision_hoy += comision_hoy
            
            comisiones_list.append({
                'id': sucursal.id,
                'nombre': sucursal.nombre,
                'comision_hoy': comision_hoy,
                'comision_mes': comision_mes
            })
        
        return jsonify({
            'success': True,
            'comisiones_hoy': comisiones_list,
            'total_comision_hoy': total_comision_hoy,
            'timestamp': ahora.isoformat()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/ping')
def ping():
    return jsonify({'status': 'ok', 'timestamp': get_peru_time().isoformat()})

# Inicialización de la base de datos COMPATIBLE
def init_db():
    """Inicializar la base de datos con datos básicos"""
    with app.app_context():
        try:
            # Solo crear tablas si no existen
            db.create_all()
            
            # Asegurar que el admin exista con la contraseña correcta
            asegurar_admin_existe()
            
            # Crear sucursal principal si no existe
            sucursal_principal = Sucursal.query.filter_by(nombre='Principal').first()
            if not sucursal_principal:
                sucursal_principal = Sucursal(
                    nombre='Principal',
                    direccion='Sede Principal',
                    activa=True
                )
                db.session.add(sucursal_principal)
                db.session.commit()
                print("✅ Sucursal principal creada")
            
            # Crear medios de pago básicos si no existen
            medios_basicos = [
                ('EFECTIVO', 'Efectivo'),
                ('TARJETA', 'Tarjeta de Débito/Crédito'),
                ('TRANSFERENCIA', 'Transferencia Bancaria'),
                ('YAPE', 'Yape'),
                ('PLIN', 'Plin')
            ]
            
            for abreviado, completo in medios_basicos:
                medio = MedioPago.query.filter_by(nombre_abreviado=abreviado).first()
                if not medio:
                    medio = MedioPago(
                        nombre_abreviado=abreviado,
                        nombre_completo=completo,
                        activo=True
                    )
                    db.session.add(medio)
            
            db.session.commit()
            print("✅ Medios de pago básicos creados")
            
        except Exception as e:
            print(f"⚠️ Error en inicialización (continuando): {e}")
            # Continuar aunque haya errores menores

# Asegurar inicialización cuando se importa (Gunicorn/Railway)
try:
    init_db()
except Exception as e:
    print(f"⚠️ Error al inicializar en import: {e}")

if __name__ == '__main__':
    init_db()
    print("🎉 SISAGENT Flask COMPATIBLE ULTRA OPTIMIZADO cargado completamente - Listo para producción!")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
