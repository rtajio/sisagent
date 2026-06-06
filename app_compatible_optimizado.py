#!/usr/bin/env python3
"""
SISAGENT - Sistema de Gestión de Operaciones Bancarias
VERSIÓN COMPATIBLE ULTRA OPTIMIZADA
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, session
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

def _fecha_rango(fecha_str, es_fin=False):
    """
    Convierte una fecha 'YYYY-MM-DD' en un datetime naive en hora Perú
    comparable con los valores guardados en la DB.
    TODO se guarda como wall-clock Perú (naive).
    """
    try:
        d = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None
    if es_fin:
        dt_peru = datetime.combine(d, datetime.max.time()).replace(
            tzinfo=peru_tz, hour=23, minute=59, second=59, microsecond=999999)
    else:
        dt_peru = datetime.combine(d, datetime.min.time()).replace(tzinfo=peru_tz)

    # Retornar como naive Perú (wall-clock) para comparar directamente con BD
    return dt_peru.replace(tzinfo=None)


def _to_peru(dt):
    """
    Normaliza cualquier datetime a hora de Perú (America/Lima, UTC-5).

    Estrategia unificada: TODO se guarda como wall-clock Perú (naive) en ambos backends.
    - Con tzinfo: convertir a Perú (puede venir de librerías externas)
    - Sin tzinfo: asumir que YA es hora Perú, solo agregar zona para operaciones
    """
    if dt is None:
        return None
    if dt.tzinfo is not None:
        # Ya tiene zona horaria → convertir a Perú
        return dt.astimezone(peru_tz)
    # Naive: asumir que YA es hora Perú (guarda como wall-clock en la BD)
    return peru_tz.localize(dt)

def format_peru_time(dt):
    """Formatea una hora para mostrar en zona horaria de Perú"""
    t = _to_peru(dt)
    return t.strftime('%H:%M:%S') if t else ""

def format_peru_date(dt):
    """Formatea una fecha para mostrar en zona horaria de Perú"""
    t = _to_peru(dt)
    return t.strftime('%d/%m/%Y') if t else ""

def format_peru_datetime(dt):
    """Formatea fecha/hora completa en zona horaria de Perú"""
    t = _to_peru(dt)
    return t.strftime('%d/%m/%Y %H:%M:%S') if t else ""

def format_peru_datetime_short(dt):
    """Formatea fecha/hora corta en zona horaria de Perú"""
    t = _to_peru(dt)
    return t.strftime('%d/%m/%Y %H:%M') if t else ""

print("[*] SISAGENT Flask COMPATIBLE ULTRA OPTIMIZADO arrancando...")
print("[!] OPTIMIZACIONES: Caché, Compresión, Consultas optimizadas, Paginación")
print("[~] Actualización Railway - " + get_peru_time().strftime("%Y-%m-%d %H:%M:%S"))

# Configuración de la aplicación Flask
app = Flask(__name__)

print("[OK] Flask app creada")

# Configuración para Railway
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"[OK] Usando PostgreSQL en Railway: {database_url[:20]}...")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_consolidada.db'
    print("[OK] Usando SQLite para desarrollo local")

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

print("[OK] Configuración de base de datos completada")
print("[OK] SQLAlchemy y LoginManager configurados")
print("[OK] Caché y compresión configurados")
print("[OK] Configuración de zona horaria completada")

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
    email = db.Column(db.String(120), nullable=False, default='')
    password_hash = db.Column(db.String(120), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=True)
    es_admin = db.Column(db.Boolean, default=False)
    es_admin_sucursal = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    # Token de sesión: se regenera al cambiar contraseña o al forzar cierre de sesión
    session_token  = db.Column(db.String(36), nullable=True)
    # Último acceso: se actualiza en cada request autenticado (para presencia en tiempo real)
    ultimo_acceso  = db.Column(db.DateTime, nullable=True)
    sucursal = db.relationship('Sucursal', backref='usuarios', lazy='joined')
    operaciones = db.relationship('Operacion', backref='usuario', lazy='dynamic')

    def regenerate_session_token(self):
        """Genera un nuevo token, invalidando todas las sesiones activas."""
        self.session_token = str(uuid.uuid4())

    def esta_en_linea(self):
        """True si el usuario tuvo actividad en los últimos 10 minutos.
        ultimo_acceso se guarda en hora Perú (naive wall-clock)."""
        if self.ultimo_acceso is None:
            return False
        ahora_peru = get_peru_time().replace(tzinfo=None)
        delta = ahora_peru - self.ultimo_acceso
        return delta.total_seconds() < 600  # 10 minutos

    def es_admin_de_sucursal(self):
        return self.es_admin_sucursal and self.sucursal_id is not None

    def es_admin_o_admin_sucursal(self):
        return self.es_admin or self.es_admin_de_sucursal()

    def puede_crear_usuario_en_sucursal(self, sucursal_id):
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
    hora = db.Column(db.DateTime, default=lambda: get_peru_time().replace(tzinfo=None))
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
    user = Usuario.query.get(int(user_id))
    if user is None:
        return None
    # Si el usuario tiene token definido, validar que coincida con el de la sesión actual
    if user.session_token is not None:
        if session.get('_user_session_token') != user.session_token:
            return None  # Token inválido → fuerza logout
    return user

@app.before_request
def actualizar_ultimo_acceso():
    """Actualiza el timestamp de último acceso del usuario autenticado.
    Guarda en hora Perú (wall-clock naive) para consistencia total."""
    if current_user and current_user.is_authenticated:
        ahora_peru = get_peru_time().replace(tzinfo=None)
        ultimo = current_user.ultimo_acceso
        # Solo escribir en DB si pasaron más de 60 s (evita escritura en cada request)
        if ultimo is None or (ahora_peru - ultimo).total_seconds() > 60:
            try:
                current_user.ultimo_acceso = ahora_peru
                db.session.commit()
            except Exception:
                db.session.rollback()

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
                email='admin@sisagent.local',
                password_hash=password_hash,
                es_admin=True,
                es_admin_sucursal=False,
                nombre_completo='Administrador Global'
            )
            db.session.add(admin)
            db.session.commit()
            print("[OK] Usuario 'admin' creado con contraseña 'vivalavida'")
        else:
            # Actualizar contraseña y asegurar que es admin
            admin.password_hash = password_hash
            admin.es_admin = True
            admin.es_admin_sucursal = False
            # Asegurar que tenga email si no lo tiene
            if not admin.email:
                admin.email = 'admin@sisagent.local'
            if not admin.nombre_completo:
                admin.nombre_completo = 'Administrador Global'
            db.session.commit()
            print("[OK] Usuario 'admin' actualizado con contraseña 'vivalavida'")
    except Exception as e:
        print(f"[!!]  Error al asegurar admin: {e}")
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
            # Asegurar que el usuario tenga session_token
            if user.session_token is None:
                user.regenerate_session_token()
                db.session.commit()
            login_user(user)
            session['_user_session_token'] = user.session_token
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

    # Cargar medios de pago filtrados por sucursal
    if current_user.es_admin:
        # Admin: si hay sucursal_id en params, filtrar; si no, mostrar todos
        filtro_sucursal_id = request.args.get('sucursal_id', type=int)
        if filtro_sucursal_id:
            medios_pago = MedioPago.query.join(
                MedioSucursal,
                (MedioSucursal.medio_pago_id == MedioPago.id) &
                (MedioSucursal.sucursal_id == filtro_sucursal_id) &
                (MedioSucursal.activo == True)
            ).filter(MedioPago.activo == True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
        else:
            medios_pago = get_medios_pago_cache()
    else:
        # Usuario/admin de sucursal: filtrar medios habilitados para su sucursal
        sucursal_id_usuario = current_user.sucursal_id
        if sucursal_id_usuario:
            medios_pago = MedioPago.query.join(
                MedioSucursal,
                (MedioSucursal.medio_pago_id == MedioPago.id) &
                (MedioSucursal.sucursal_id == sucursal_id_usuario) &
                (MedioSucursal.activo == True)
            ).filter(MedioPago.activo == True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
        else:
            medios_pago = get_medios_pago_cache()
    
    # Calcular comisión del día para sucursal específica si es admin global
    comision_dia = 0.0
    sucursal_nombre = None
    if current_user.es_admin and request.args.get('sucursal_id'):
        try:
            sucursal_id = int(request.args.get('sucursal_id'))
            sucursal = Sucursal.query.get(sucursal_id)
            if sucursal:
                sucursal_nombre = sucursal.nombre
                # Calcular comisión del día para esta sucursal
                comision_dia_query = db.session.query(
                    db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
                ).filter(
                    Operacion.sucursal_id == sucursal_id,
                    Operacion.hora >= inicio_hoy,
                    Operacion.hora <= fin_hoy
                ).scalar() or 0.0
                comision_dia = float(comision_dia_query)
        except (ValueError, TypeError) as e:
            print(f"Error al procesar sucursal_id: {e}")
            comision_dia = 0.0
            sucursal_nombre = None
    
    return render_template('operaciones.html',
                         operaciones=operaciones_paginated.items,
                         pagination=operaciones_paginated,
                         fecha_actual=fecha or datetime.now(peru_tz).strftime('%Y-%m-%d'),
                         fecha_hoy=datetime.now(peru_tz).strftime('%Y-%m-%d'),
                         filtros_aplicados=filtros_aplicados,
                         sucursales=sucursales,
                         medios_pago=medios_pago,
                         comision_dia=comision_dia,
                         sucursal_nombre=sucursal_nombre)

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
        
        # Crear operación con hora Perú (wall-clock naive, sin tzinfo)
        hora_peru = get_peru_time().replace(tzinfo=None)
        operacion = Operacion(
            monto=monto,
            comision=comision,
            medio=medio,
            usuario_id=current_user.id,
            sucursal_id=sucursal_id,
            hora=hora_peru  # Guardar como naive Perú para consistencia
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

@app.route('/api/sucursal/<int:sucursal_id>/medios')
@login_required
def api_medios_por_sucursal(sucursal_id):
    """Devuelve los medios de pago habilitados para una sucursal específica."""
    medios = MedioPago.query.join(
        MedioSucursal,
        (MedioSucursal.medio_pago_id == MedioPago.id) &
        (MedioSucursal.sucursal_id == sucursal_id) &
        (MedioSucursal.activo == True)
    ).filter(MedioPago.activo == True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    return {'medios': [{'value': m.nombre_abreviado, 'label': m.nombre_abreviado} for m in medios]}

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
        
        # Generar email por defecto si no existe (usar username como base)
        email_default = f"{username}@sisagent.local"
        
        nuevo_usuario = Usuario(
            username=username,
            email=email_default,  # Email por defecto basado en username
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
            # Regenerar token → cierra todas las sesiones activas de este usuario
            usuario.regenerate_session_token()
        if nombre_completo:
            usuario.nombre_completo = nombre_completo
        
        # Asegurar que el usuario tenga email (generar si no existe)
        if not usuario.email:
            usuario.email = f"{usuario.username}@sisagent.local"
        
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
        return {'ok': False, 'error': 'Acceso denegado'}, 403
    medio = MedioPago.query.get_or_404(medio_id)
    medio.activo = not medio.activo
    db.session.commit()
    cache.clear()
    # Soporta tanto AJAX como form POST normal
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return {'ok': True, 'activo': medio.activo}
    return redirect(url_for('admin_medios'))

@app.route('/admin/medios/<int:medio_id>/subir', methods=['POST'])
@login_required
def subir_medio(medio_id):
    # Mantenido por compatibilidad — reordenamiento via API /api/medios/orden
    return redirect(url_for('admin_medios'))

@app.route('/admin/medios/<int:medio_id>/bajar', methods=['POST'])
@login_required
def bajar_medio(medio_id):
    return redirect(url_for('admin_medios'))

@app.route('/api/medios/orden', methods=['POST'])
@login_required
def api_medios_orden():
    """Guarda el nuevo orden de medios de pago (drag-and-drop)."""
    if not current_user.es_admin:
        return {'ok': False, 'error': 'Acceso denegado'}, 403
    data = request.get_json()
    ids = data.get('ids', [])
    for i, mid in enumerate(ids):
        m = MedioPago.query.get(mid)
        if m:
            m.orden = i
    db.session.commit()
    cache.clear()
    return {'ok': True}

@app.route('/api/medios/<int:medio_id>/editar', methods=['POST'])
@login_required
def api_editar_medio(medio_id):
    """Edita inline nombre abreviado y completo de un medio."""
    if not current_user.es_admin:
        return {'ok': False, 'error': 'Acceso denegado'}, 403
    medio = MedioPago.query.get_or_404(medio_id)
    data = request.get_json()
    abreviado = (data.get('nombre_abreviado') or '').strip().upper()
    completo  = (data.get('nombre_completo')  or '').strip()
    if not abreviado or not completo:
        return {'ok': False, 'error': 'Datos incompletos'}, 400
    medio.nombre_abreviado = abreviado
    medio.nombre_completo  = completo
    db.session.commit()
    cache.clear()
    return {'ok': True, 'abreviado': medio.nombre_abreviado, 'completo': medio.nombre_completo}

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


@app.route('/admin/usuarios/<int:usuario_id>/cerrar-sesion', methods=['POST'])
@login_required
def forzar_cierre_sesion(usuario_id):
    """Admin cierra la sesión activa de un usuario específico regenerando su token."""
    if not current_user.es_admin_o_admin_sucursal():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'Acceso denegado'}), 403
        flash('Acceso denegado', 'error')
        return redirect(url_for('admin_usuarios'))

    usuario = Usuario.query.get_or_404(usuario_id)

    # No se puede cerrar la sesión del propio usuario admin actual
    if usuario.id == current_user.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'ok': False, 'error': 'No puedes cerrar tu propia sesión desde aquí'}), 400
        flash('No puedes cerrar tu propia sesión desde aquí', 'warning')
        return redirect(url_for('admin_usuarios'))

    # Admin de sucursal solo puede afectar usuarios de su sucursal
    if current_user.es_admin_de_sucursal() and not current_user.es_admin:
        if usuario.sucursal_id != current_user.sucursal_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'ok': False, 'error': 'Sin permisos sobre este usuario'}), 403
            flash('Sin permisos sobre este usuario', 'error')
            return redirect(url_for('admin_usuarios'))

    usuario.regenerate_session_token()
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'ok': True, 'mensaje': f'Sesión de {usuario.username} cerrada'})
    flash(f'Sesión de {usuario.username} cerrada correctamente', 'success')
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
        
        # Filtros de fecha: usar _fecha_rango para adaptarse al backend (SQLite vs PostgreSQL)
        if fecha_inicio:
            inicio = _fecha_rango(fecha_inicio, es_fin=False)
            if inicio:
                query = query.filter(Operacion.hora >= inicio)

        if fecha_fin:
            fin = _fecha_rango(fecha_fin, es_fin=True)
            if fin:
                query = query.filter(Operacion.hora <= fin)
        
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


# ── Función auxiliar: obtener operaciones filtradas ─────────────────────────
def _get_operaciones_filtradas():
    """Devuelve lista de dicts con las operaciones según los parámetros de la request."""
    if not current_user.es_admin_o_admin_sucursal():
        return None, 403

    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin    = request.args.get('fecha_fin')
    sucursal_id  = request.args.get('sucursal_id')
    medio        = request.args.get('medio')

    query = Operacion.query

    if current_user.es_admin_de_sucursal() and not current_user.es_admin:
        if current_user.sucursal_id:
            query = query.filter(Operacion.sucursal_id == current_user.sucursal_id)
    elif sucursal_id and sucursal_id.strip():
        try:
            query = query.filter(Operacion.sucursal_id == int(sucursal_id))
        except ValueError:
            pass

    if fecha_inicio:
        inicio = _fecha_rango(fecha_inicio, es_fin=False)
        if inicio:
            query = query.filter(Operacion.hora >= inicio)

    if fecha_fin:
        fin = _fecha_rango(fecha_fin, es_fin=True)
        if fin:
            query = query.filter(Operacion.hora <= fin)

    if medio:
        query = query.filter(Operacion.medio == medio)

    from sqlalchemy.orm import joinedload
    operaciones = query.options(
        joinedload(Operacion.usuario).load_only(Usuario.id, Usuario.username, Usuario.nombre_completo),
        joinedload(Operacion.sucursal).load_only(Sucursal.id, Sucursal.nombre)
    ).order_by(Operacion.hora.asc()).all()

    medios_cache = {mp.nombre_abreviado: mp.nombre_completo for mp in MedioPago.query.filter_by(activo=True).all()}

    filas = []
    for op in operaciones:
        usuario_nombre = 'N/A'
        if op.usuario:
            usuario_nombre = op.usuario.nombre_completo or op.usuario.username
        sucursal_nombre = op.sucursal.nombre if op.sucursal else 'Sin sucursal'
        filas.append({
            'id':       op.id,
            'fecha':    format_peru_date(op.hora),
            'hora':     format_peru_time(op.hora),
            'monto':    float(op.monto),
            'comision': float(op.comision),
            'medio':    medios_cache.get(op.medio, op.medio),
            'usuario':  usuario_nombre,
            'sucursal': sucursal_nombre,
        })
    return filas, 200


# ── Exportar CSV ─────────────────────────────────────────────────────────────
@app.route('/api/reportes/exportar/csv')
@login_required
def exportar_csv():
    filas, status = _get_operaciones_filtradas()
    if status != 200:
        return jsonify({'error': 'Acceso denegado'}), status

    import csv, io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['N°', 'Fecha', 'Hora', 'Monto (S/)', 'Comisión (S/)', 'Medio', 'Usuario', 'Sucursal'])
    for i, f in enumerate(filas, 1):
        writer.writerow([i, f['fecha'], f['hora'],
                         f'{f["monto"]:.2f}', f'{f["comision"]:.2f}',
                         f['medio'], f['usuario'], f['sucursal']])
    # Totales
    writer.writerow([])
    writer.writerow(['', '', 'TOTAL',
                     f'{sum(f["monto"] for f in filas):.2f}',
                     f'{sum(f["comision"] for f in filas):.2f}', '', '', ''])

    from flask import Response
    return Response(
        '﻿' + output.getvalue(),      # BOM para Excel
        mimetype='text/csv; charset=utf-8-sig',
        headers={'Content-Disposition': 'attachment; filename=reporte_operaciones.csv'}
    )


# ── Exportar XLSX ─────────────────────────────────────────────────────────────
@app.route('/api/reportes/exportar/xlsx')
@login_required
def exportar_xlsx():
    filas, status = _get_operaciones_filtradas()
    if status != 200:
        return jsonify({'error': 'Acceso denegado'}), status

    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    import io

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Operaciones'

    # Paleta clara y profesional para Excel (legible en impresión y pantalla)
    COLOR_HEADER = '1F4E79'   # azul oscuro profesional
    COLOR_TITLE  = '2E75B6'   # azul medio para título
    COLOR_TOTAL  = 'D6E4F0'   # azul muy claro para totales
    COLOR_ODD    = 'FFFFFF'   # blanco
    COLOR_EVEN   = 'EBF3FA'   # azul muy claro alternado

    header_font  = Font(bold=True, color='FFFFFF', size=10)
    total_font   = Font(bold=True, color='1F4E79', size=10)
    data_font    = Font(color='1A1A1A', size=10)
    header_fill  = PatternFill('solid', fgColor=COLOR_HEADER)
    total_fill   = PatternFill('solid', fgColor=COLOR_TOTAL)
    odd_fill     = PatternFill('solid', fgColor=COLOR_ODD)
    even_fill    = PatternFill('solid', fgColor=COLOR_EVEN)
    center       = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_wrap    = Alignment(horizontal='left',   vertical='center', wrap_text=True)
    right_al     = Alignment(horizontal='right',  vertical='center')
    thin         = Side(style='thin', color='BDD7EE')
    border       = Border(left=thin, right=thin, top=thin, bottom=thin)

    # Título
    ws.merge_cells('A1:H1')
    title_cell = ws['A1']
    title_cell.value = 'REPORTE DE OPERACIONES — SISAGENT'
    title_cell.font  = Font(bold=True, size=14, color='FFFFFF')
    title_cell.fill  = PatternFill('solid', fgColor=COLOR_TITLE)
    title_cell.alignment = center
    ws.row_dimensions[1].height = 30

    # Parámetros del reporte en fila 2
    fecha_ini = request.args.get('fecha_inicio', '')
    fecha_fin = request.args.get('fecha_fin', '')
    ws.merge_cells('A2:H2')
    ws['A2'].value = f'Período: {fecha_ini or "—"}  →  {fecha_fin or "—"}    Total registros: {len(filas)}'
    ws['A2'].font  = Font(italic=True, color='2E75B6', size=9)
    ws['A2'].fill  = PatternFill('solid', fgColor='DEEAF1')
    ws['A2'].alignment = center
    ws.row_dimensions[2].height = 16

    # Cabecera columnas (fila 4)
    headers = ['N°', 'Fecha', 'Hora', 'Monto (S/)', 'Comisión (S/)', 'Medio', 'Usuario', 'Sucursal']
    widths  = [5,     12,      10,     14,            14,              22,      22,         22]
    for col, (h, w) in enumerate(zip(headers, widths), 1):
        cell = ws.cell(row=4, column=col, value=h)
        cell.font      = header_font
        cell.fill      = header_fill
        cell.alignment = center
        cell.border    = border
        ws.column_dimensions[get_column_letter(col)].width = w
    ws.row_dimensions[4].height = 20

    # Datos
    money_fmt = '#,##0.00'
    for i, f in enumerate(filas, 1):
        row = i + 4
        values = [i, f['fecha'], f['hora'], f['monto'], f['comision'],
                  f['medio'], f['usuario'], f['sucursal']]
        fill_bg = odd_fill if i % 2 == 1 else even_fill
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.fill   = fill_bg
            cell.border = border
            cell.font   = data_font
            if col in (4, 5):
                cell.number_format = money_fmt
                cell.alignment = right_al
            elif col == 1:
                cell.alignment = center
            else:
                cell.alignment = left_wrap
        ws.row_dimensions[row].height = 15

    # Totales
    total_row = len(filas) + 5
    ws.merge_cells(f'A{total_row}:C{total_row}')
    ws[f'A{total_row}'].value     = 'TOTALES'
    ws[f'A{total_row}'].font      = total_font
    ws[f'A{total_row}'].fill      = total_fill
    ws[f'A{total_row}'].alignment = center
    ws[f'A{total_row}'].border    = border

    for col, val in [(4, sum(f['monto'] for f in filas)),
                     (5, sum(f['comision'] for f in filas))]:
        cell = ws.cell(row=total_row, column=col, value=val)
        cell.font          = total_font
        cell.fill          = total_fill
        cell.number_format = money_fmt
        cell.alignment     = Alignment(horizontal='right')
        cell.border        = border

    for col in range(6, 9):
        cell = ws.cell(row=total_row, column=col, value='')
        cell.fill   = total_fill
        cell.border = border

    ws.freeze_panes = 'A5'

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    from flask import Response
    return Response(
        buf.read(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=reporte_operaciones.xlsx'}
    )


# ── Exportar PDF ─────────────────────────────────────────────────────────────
@app.route('/api/reportes/exportar/pdf')
@login_required
def exportar_pdf():
    filas, status = _get_operaciones_filtradas()
    if status != 200:
        return jsonify({'error': 'Acceso denegado'}), status

    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                    Paragraph, Spacer)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    import io

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4),
                            leftMargin=12*mm, rightMargin=12*mm,
                            topMargin=14*mm, bottomMargin=14*mm)

    # Paleta oscura cálida → para PDF usamos versión legible (fondo blanco papel)
    C_DARK    = colors.HexColor('#2A2420')
    C_ACCENT  = colors.HexColor('#A0845A')
    C_MID     = colors.HexColor('#332E28')
    C_LIGHT   = colors.HexColor('#F2EDE4')
    C_MUTED   = colors.HexColor('#8A7E70')
    C_ROW_ODD = colors.HexColor('#F7F3EE')
    C_ROW_EVEN= colors.HexColor('#EDE6DC')
    C_SUCCESS = colors.HexColor('#3A6A3A')
    C_WHITE   = colors.white

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Normal'],
                                 fontSize=16, fontName='Helvetica-Bold',
                                 textColor=C_DARK, alignment=TA_CENTER, spaceAfter=2*mm)
    sub_style   = ParagraphStyle('Sub', parent=styles['Normal'],
                                 fontSize=9, fontName='Helvetica',
                                 textColor=C_MUTED, alignment=TA_CENTER, spaceAfter=4*mm)

    fecha_ini = request.args.get('fecha_inicio', '—')
    fecha_fin = request.args.get('fecha_fin', '—')

    elements = [
        Paragraph('REPORTE DE OPERACIONES', title_style),
        Paragraph(f'SISAGENT &nbsp;|&nbsp; Período: {fecha_ini} → {fecha_fin} &nbsp;|&nbsp; {len(filas)} registros', sub_style),
    ]

    # Estilos para celdas con texto largo (permiten wrap automático)
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'],
                                fontSize=8, fontName='Helvetica',
                                textColor=C_DARK, leading=10, alignment=TA_LEFT)
    cell_right = ParagraphStyle('CellR', parent=cell_style, alignment=TA_RIGHT)

    def P(text, style=None):
        """Convierte texto a Paragraph para que haga word-wrap en la celda."""
        return Paragraph(str(text) if text else '', style or cell_style)

    # Tabla de datos
    # Landscape A4: 297mm - 24mm márgenes = 273mm útiles
    # N°:8 | Fecha:22 | Hora:17 | Monto:24 | Comisión:24 | Medio:52 | Usuario:62 | Sucursal:62 = 271mm
    col_headers = ['N°', 'Fecha', 'Hora', 'Monto (S/)', 'Comisión (S/)', 'Medio', 'Usuario', 'Sucursal']
    col_widths  = [8*mm, 22*mm, 17*mm, 24*mm, 24*mm, 52*mm, 62*mm, 62*mm]

    table_data = [col_headers]
    for i, f in enumerate(filas, 1):
        table_data.append([
            str(i),
            f['fecha'],
            f['hora'],
            P(f'S/ {f["monto"]:,.2f}', cell_right),
            P(f'S/ {f["comision"]:,.2f}', cell_right),
            P(f['medio']),
            P(f['usuario']),
            P(f['sucursal']),
        ])

    # Fila de totales
    total_m = sum(f['monto'] for f in filas)
    total_c = sum(f['comision'] for f in filas)
    tot_style = ParagraphStyle('Tot', parent=cell_right,
                               fontName='Helvetica-Bold', textColor=C_LIGHT)
    table_data.append(['', '', P('TOTAL', ParagraphStyle('TotC', parent=cell_style,
                       fontName='Helvetica-Bold', textColor=C_LIGHT, alignment=TA_CENTER)),
                       P(f'S/ {total_m:,.2f}', tot_style),
                       P(f'S/ {total_c:,.2f}', tot_style),
                       '', '', ''])

    t = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Estilos de la tabla
    style_cmds = [
        ('BACKGROUND',  (0, 0), (-1, 0),  C_DARK),
        ('TEXTCOLOR',   (0, 0), (-1, 0),  C_LIGHT),
        ('FONTNAME',    (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, 0),  9),
        ('ALIGN',       (0, 0), (-1, 0),  'CENTER'),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE',    (0, 1), (-1, -1), 8),
        ('FONTNAME',    (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN',       (3, 1), (4, -1),  'RIGHT'),
        ('ALIGN',       (0, 1), (0, -1),  'CENTER'),
        ('GRID',        (0, 0), (-1, -1), 0.4, C_MUTED),
        ('TOPPADDING',  (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING',(0, 0), (-1, -1), 3),
        ('ROWHEIGHT',   (0, 0), (-1, 0),  16),
        # Fila de totales
        ('BACKGROUND',  (0, -1), (-1, -1), C_ACCENT),
        ('TEXTCOLOR',   (0, -1), (-1, -1), C_LIGHT),
        ('FONTNAME',    (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('ROWHEIGHT',   (0, -1), (-1, -1), 16),
    ]
    # Filas alternadas
    for row_i in range(1, len(table_data) - 1):
        bg = C_ROW_ODD if row_i % 2 == 1 else C_ROW_EVEN
        style_cmds.append(('BACKGROUND', (0, row_i), (-1, row_i), bg))

    t.setStyle(TableStyle(style_cmds))
    elements.append(t)

    doc.build(elements)
    buf.seek(0)

    from flask import Response
    return Response(
        buf.read(),
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=reporte_operaciones.pdf'}
    )


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

            # Migración: agregar columnas nuevas si no existen
            # NOTA: En Railway con múltiples workers, los ALTERs pueden causar race conditions
            # Solución: hacer las ALTERs de forma segura con manejo de locks
            try:
                from sqlalchemy import text, event

                # En Railway, usar transaction safety
                if os.environ.get('DATABASE_URL'):
                    try:
                        with db.engine.begin() as _conn:
                            # Usar CONCURRENTLY si es PostgreSQL 9.2+
                            _conn.execute(text(
                                "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS session_token VARCHAR(36)"))
                            _conn.execute(text(
                                "ALTER TABLE usuario ADD COLUMN IF NOT EXISTS ultimo_acceso TIMESTAMP"))
                        print("[OK] Columnas verificadas (PostgreSQL)")
                    except Exception as e:
                        if "already exists" in str(e) or "duplicate" in str(e).lower():
                            print("[OK] Columnas ya existen")
                        else:
                            print(f"[WARN] Error en migración: {e}")
                else:
                    # SQLite: ejecutar por separado, ignorar error si ya existe
                    for col_sql in [
                        "ALTER TABLE usuario ADD COLUMN session_token VARCHAR(36)",
                        "ALTER TABLE usuario ADD COLUMN ultimo_acceso TIMESTAMP",
                    ]:
                        try:
                            with db.engine.connect() as _conn:
                                _conn.execute(text(col_sql))
                                _conn.commit()
                        except Exception:
                            pass
                    print("[OK] Columnas verificadas (SQLite)")
            except Exception as e:
                print(f"[WARN] Error general en migración de columnas: {e}")

            # Asignar session_token a usuarios existentes que tengan NULL
            # (ocurre en deploys post-migración: usuarios registrados antes del feature)
            try:
                usuarios_sin_token = Usuario.query.filter(
                    Usuario.session_token == None).all()
                if usuarios_sin_token:
                    for u in usuarios_sin_token:
                        u.session_token = str(uuid.uuid4())
                    db.session.commit()
                    print(f"[OK] Tokens asignados a {len(usuarios_sin_token)} usuarios existentes")
            except Exception as e:
                print(f"[WARN] No se pudo asignar tokens iniciales: {e}")

            # Migración: Corregir operaciones guardadas en UTC (antes del refactor a Perú puro)
            # NOTA: Migración DESACTIVADA por ahora - usar SQL directo si es necesario
            # El problema es que consultar todas las operaciones puede causar timeout en Railway
            # Solución: ejecutar manualmente en Railway cuando sea necesario
            try:
                print("[INFO] Migración de Operacion.hora desactivada (ejecutar manualmente si es necesario)")
            except Exception as e:
                print(f"[WARN] Nota sobre migración: {e}")

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
                print("[OK] Sucursal principal creada")
            
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
            print("[OK] Medios de pago básicos creados")
            
        except Exception as e:
            print(f"[!!] Error en inicialización (continuando): {e}")
            # Continuar aunque haya errores menores

# Asegurar inicialización cuando se importa (Gunicorn/Railway)
try:
    init_db()
except Exception as e:
    print(f"[!!] Error al inicializar en import: {e}")

if __name__ == '__main__':
    init_db()
    print("[OK] SISAGENT Flask COMPATIBLE ULTRA OPTIMIZADO cargado completamente - Listo para produccion!")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
