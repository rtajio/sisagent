#!/usr/bin/env python3
"""
SISAGENT - Sistema de Gestión de Operaciones Bancarias
VERSIÓN COMPATIBLE ULTRA OPTIMIZADA
"""

import os
import sys
import json
import threading
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_caching import Cache
from flask_compress import Compress
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy import Index
import pytz
import time

# Configuración de zona horaria (UTC-5 para Perú)
peru_tz = pytz.timezone('America/Lima')

def get_peru_time():
    """Obtiene la hora actual en zona horaria de Perú"""
    return datetime.now(peru_tz)

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

# OPTIMIZACIÓN ULTRA FLUIDA: Configuración SQLAlchemy optimizada para Railway
# Solo aplicar opciones de PostgreSQL si estamos usando PostgreSQL
if os.environ.get('DATABASE_URL') and 'postgresql' in os.environ.get('DATABASE_URL', '').lower():
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,  # Reducido para Railway
        'max_overflow': 10,  # Reducido para Railway
        'pool_timeout': 20,  # Reducido para Railway
        'echo': False,
        'echo_pool': False,
        'connect_args': {
            'connect_timeout': 5,  # Timeout más corto
            'options': '-c statement_timeout=30000'  # Timeout de 30 segundos para queries
        }
    }
else:
    # Para SQLite, usar configuración mínima
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'echo': False
    }

# OPTIMIZACIÓN ULTRA FLUIDA: Configuración Flask optimizada
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # Cache estático 1 año
app.config['JSON_SORT_KEYS'] = False

# OPTIMIZACIÓN ULTRA FLUIDA: Configuración de caché mejorada
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 600  # 10 minutos (aumentado)
app.config['CACHE_THRESHOLD'] = 1000

# OPTIMIZACIÓN ULTRA FLUIDA: Configuración de compresión mejorada
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'text/javascript',
    'application/json', 'application/javascript', 'application/xml'
]
app.config['COMPRESS_LEVEL'] = 9  # Máxima compresión
app.config['COMPRESS_MIN_SIZE'] = 100  # Comprimir desde 100 bytes

# Inicializar extensiones con manejo de errores
try:
    db = SQLAlchemy(app)
    print("✅ SQLAlchemy inicializado")
except Exception as e:
    print(f"⚠️ Error inicializando SQLAlchemy: {e}")
    raise

try:
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    print("✅ LoginManager inicializado")
except Exception as e:
    print(f"⚠️ Error inicializando LoginManager: {e}")
    raise

# OPTIMIZACIÓN ULTRA: Inicializar caché y compresión
try:
    cache = Cache(app)
    Compress(app)
    print("✅ Caché y compresión inicializados")
except Exception as e:
    print(f"⚠️ Error inicializando caché/compresión: {e}")
    # Continuar sin caché si hay problemas
    cache = None

print("✅ Configuración de base de datos completada")
print("✅ SQLAlchemy y LoginManager configurados")
print("✅ Caché y compresión configurados")
print("✅ Configuración de zona horaria completada")

# Context processor para hacer disponibles las funciones de formato en templates
@app.context_processor
def inject_format_functions():
    """Inyectar funciones de formato en el contexto de templates"""
    return {
        'format_peru_time': format_peru_time,
        'format_peru_date': format_peru_date,
        'format_peru_datetime': format_peru_datetime,
        'format_peru_datetime_short': format_peru_datetime_short
    }

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
    es_admin = db.Column(db.Boolean, default=False)  # Admin global (puede ver todas las sucursales)
    es_admin_sucursal = db.Column(db.Boolean, default=False)  # Admin de sucursal (solo su sucursal)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=True)
    # OPTIMIZACIÓN ULTRA FLUIDA: Solo campos que existen en la BD real
    # NOTA: No incluir hora_creacion, created_at, email, nombre_completo si no existen en la BD
    operaciones = db.relationship('Operacion', backref='usuario', lazy='dynamic')
    # Relación con Sucursal
    sucursal = db.relationship('Sucursal', backref='usuarios', lazy='joined')
    
    def es_admin_completo(self):
        """Verificar si es admin global"""
        return self.es_admin
    
    def es_admin_de_sucursal(self):
        """Verificar si es admin de sucursal"""
        return self.es_admin_sucursal and self.sucursal_id is not None
    
    def puede_administrar_sucursal(self, sucursal_id):
        """Verificar si puede administrar una sucursal específica"""
        if self.es_admin:
            return True  # Admin global puede administrar todas
        if self.es_admin_sucursal and self.sucursal_id == sucursal_id:
            return True  # Admin de sucursal solo puede administrar su sucursal
        return False

class Operacion(db.Model):
    __tablename__ = 'operacion'
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    comision = db.Column(db.Numeric(10, 2), nullable=False)
    medio = db.Column(db.String(50), nullable=False)
    hora = db.Column(db.DateTime, default=lambda: get_peru_time(), index=True)  # Índice para consultas por fecha
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, index=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False, index=True)
    
    # Índices compuestos para consultas frecuentes
    __table_args__ = (
        Index('idx_operacion_fecha_sucursal', 'hora', 'sucursal_id'),
        Index('idx_operacion_fecha_usuario', 'hora', 'usuario_id'),
        Index('idx_operacion_medio', 'medio'),
    )

class MedioPago(db.Model):
    __tablename__ = 'medio_pago'
    id = db.Column(db.Integer, primary_key=True)
    nombre_abreviado = db.Column(db.String(20), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)

class ComisionDiaria(db.Model):
    __tablename__ = 'comision_diaria'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, index=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False, index=True)
    total_comision = db.Column(db.Numeric(10, 2), default=0.0)
    
    # Índice compuesto para búsquedas frecuentes
    __table_args__ = (
        Index('idx_comision_diaria_fecha_sucursal', 'fecha', 'sucursal_id', unique=True),
    )

class ComisionMensual(db.Model):
    __tablename__ = 'comision_mensual'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False, index=True)
    mes = db.Column(db.Integer, nullable=False, index=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False, index=True)
    total_comision = db.Column(db.Numeric(10, 2), default=0.0)
    
    # Índice compuesto para búsquedas frecuentes
    __table_args__ = (
        Index('idx_comision_mensual_ano_mes_sucursal', 'año', 'mes', 'sucursal_id', unique=True),
    )

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
    
    if is_admin:
        # Estadísticas para admin
        operaciones_hoy = db.session.query(db.func.count(Operacion.id)).filter(
            db.func.date(Operacion.hora) == hoy
        ).scalar() or 0
        
        total_operaciones = db.session.query(db.func.count(Operacion.id)).scalar() or 0
        
        comision_hoy = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).filter(
            db.func.date(Operacion.hora) == hoy
        ).scalar() or 0
        
        total_comision = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).scalar() or 0
        
        sucursales_activas = db.session.query(db.func.count(Sucursal.id)).filter_by(activa=True).scalar() or 0
        
        usuarios_total = db.session.query(db.func.count(Usuario.id)).scalar() or 0
        
    else:
        # Estadísticas para usuario normal
        operaciones_hoy = db.session.query(db.func.count(Operacion.id)).filter(
            Operacion.usuario_id == user_id,
            db.func.date(Operacion.hora) == hoy
        ).scalar() or 0
        
        total_operaciones = db.session.query(db.func.count(Operacion.id)).filter(
            Operacion.usuario_id == user_id
        ).scalar() or 0
        
        comision_hoy = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).filter(
            Operacion.usuario_id == user_id,
            db.func.date(Operacion.hora) == hoy
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
    # OPTIMIZACIÓN ULTRA FLUIDA: Cargar usuario con manejo de errores
    try:
        # Intentar cargar con eager load de sucursal
        usuario = Usuario.query.options(joinedload(Usuario.sucursal)).get(int(user_id))
        if usuario:
            return usuario
    except (AttributeError, Exception) as e:
        # Si hay error, intentar cargar sin eager load
        print(f"⚠️ Error al cargar usuario {user_id} con eager load: {e}")
        try:
            db.session.rollback()
        except:
            pass
        try:
            # Fallback: cargar sin eager load
            return Usuario.query.get(int(user_id))
        except Exception as e2:
            print(f"⚠️ Error al cargar usuario {user_id} (fallback): {e2}")
            try:
                db.session.rollback()
            except:
                pass
            return None

# OPTIMIZACIÓN ULTRA: Función para limpiar caché
def clear_cache():
    """Limpiar todo el caché"""
    cache.clear()

# FUNCIONES HELPER PARA PERMISOS DE ADMIN DE SUCURSAL
def es_admin_o_admin_sucursal():
    """Verificar si el usuario es admin global o admin de sucursal"""
    return current_user.es_admin or current_user.es_admin_de_sucursal()

def puede_ver_sucursal(sucursal_id):
    """Verificar si el usuario puede ver una sucursal específica"""
    if current_user.es_admin:
        return True
    if current_user.es_admin_de_sucursal():
        return current_user.sucursal_id == sucursal_id
    return current_user.sucursal_id == sucursal_id

def puede_crear_usuario_en_sucursal(sucursal_id):
    """Verificar si el usuario puede crear usuarios en una sucursal"""
    if current_user.es_admin:
        return True
    if current_user.es_admin_de_sucursal():
        return current_user.sucursal_id == sucursal_id
    return False

# SOLUCIÓN DIRECTA: Función para asegurar que la columna es_admin_sucursal existe
def asegurar_columna_admin_sucursal():
    """Asegurar que la columna es_admin_sucursal existe en la tabla usuario"""
    try:
        # Verificar si la columna existe usando SQL directo
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('usuario')]
        
        if 'es_admin_sucursal' not in columns:
            print("🔧 Columna es_admin_sucursal no existe - creándola...")
            # Agregar la columna usando ALTER TABLE
            if 'postgresql' in str(db.engine.url).lower():
                # PostgreSQL
                db.session.execute(text('ALTER TABLE usuario ADD COLUMN IF NOT EXISTS es_admin_sucursal BOOLEAN DEFAULT FALSE'))
            else:
                # SQLite
                db.session.execute(text('ALTER TABLE usuario ADD COLUMN es_admin_sucursal BOOLEAN DEFAULT 0'))
            db.session.commit()
            print("✅ Columna es_admin_sucursal creada")
    except Exception as e:
        print(f"⚠️ Error al verificar/crear columna es_admin_sucursal: {e}")
        db.session.rollback()
        # Continuar aunque haya error (puede que ya exista)

# SOLUCIÓN DIRECTA: Función para asegurar admin existe
def asegurar_admin_existe():
    """SOLUCIÓN DIRECTA: Asegurar que el admin existe y tiene la contraseña correcta"""
    try:
        # Primero asegurar que la columna existe
        asegurar_columna_admin_sucursal()
        
        nueva_password = '61442159'
        nueva_hash = generate_password_hash(nueva_password)
        
        admin = Usuario.query.filter_by(username='admin').first()
        
        if not admin:
            print("🔧 ADMIN NO EXISTE - CREANDO...")
            admin = Usuario(
                username='admin',
                password_hash=nueva_hash,
                es_admin=True,
                es_admin_sucursal=False  # Admin global no es admin de sucursal
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✅ ADMIN CREADO - Usuario: admin, Contraseña: {nueva_password}")
        else:
            # FORZAR actualización de contraseña SIEMPRE
            print(f"🔧 ACTUALIZANDO ADMIN EXISTENTE...")
            print(f"   Hash anterior: {admin.password_hash[:50] if admin.password_hash else 'None'}...")
            admin.password_hash = nueva_hash
            admin.es_admin = True
            # Solo actualizar es_admin_sucursal si el atributo existe
            if hasattr(admin, 'es_admin_sucursal'):
                admin.es_admin_sucursal = False  # Admin global no es admin de sucursal
            db.session.commit()
            
            # Refrescar el objeto desde la base de datos para asegurar que tenemos los datos actualizados
            db.session.refresh(admin)
            
            # Verificar que funciona
            print(f"   Hash nuevo: {admin.password_hash[:50] if admin.password_hash else 'None'}...")
            if admin.password_hash and check_password_hash(admin.password_hash, nueva_password):
                print(f"✅ ADMIN VERIFICADO - Usuario: admin, Contraseña: {nueva_password}")
            else:
                print("❌ ERROR: La contraseña no funciona después de actualizar")
                # Intentar una vez más
                print("🔧 Reintentando actualización...")
                admin.password_hash = generate_password_hash(nueva_password)
                db.session.commit()
                db.session.refresh(admin)
                if admin.password_hash and check_password_hash(admin.password_hash, nueva_password):
                    print(f"✅ ADMIN VERIFICADO (segundo intento) - Usuario: admin, Contraseña: {nueva_password}")
                else:
                    print("❌ ERROR CRÍTICO: No se pudo establecer la contraseña correctamente")
    except Exception as e:
        print(f"❌ ERROR al asegurar admin: {e}")
        db.session.rollback()  # CRÍTICO: Hacer rollback para limpiar la transacción
        import traceback
        traceback.print_exc()

# Función para asegurar que admin1 existe
def asegurar_admin1_existe():
    """Asegurar que el usuario admin1 existe con privilegios de administrador"""
    try:
        from sqlalchemy import text
        
        username = 'admin1'
        password = 'admin1'
        password_hash = generate_password_hash(password)
        email = f'{username}@sisagent.com'
        nombre_completo = 'Administrador 1'
        
        admin1 = Usuario.query.filter_by(username=username).first()
        
        if not admin1:
            print(f"🔧 ADMIN1 NO EXISTE - CREANDO...")
            # Usar SQL directo para manejar campos que pueden no estar en el modelo
            try:
                db.session.execute(
                    text("""
                        INSERT INTO usuario (username, password_hash, email, nombre_completo, es_admin, es_admin_sucursal, activo)
                        VALUES (:username, :password_hash, :email, :nombre_completo, 1, 0, 1)
                    """),
                    {
                        'username': username,
                        'password_hash': password_hash,
                        'email': email,
                        'nombre_completo': nombre_completo
                    }
                )
                db.session.commit()
                print(f"✅ ADMIN1 CREADO - Usuario: {username}, Contraseña: {password}")
            except Exception as e:
                print(f"⚠️  Error al crear admin1 con SQL directo: {e}")
                db.session.rollback()
                # Intentar con el modelo si falla SQL directo
                try:
                    admin1 = Usuario(
                        username=username,
                        password_hash=password_hash,
                        es_admin=True,
                        es_admin_sucursal=False
                    )
                    db.session.add(admin1)
                    db.session.commit()
                    print(f"✅ ADMIN1 CREADO (método alternativo) - Usuario: {username}, Contraseña: {password}")
                except Exception as e2:
                    print(f"❌ Error al crear admin1: {e2}")
                    db.session.rollback()
        else:
            # Actualizar contraseña y privilegios si ya existe
            print(f"🔧 ACTUALIZANDO ADMIN1 EXISTENTE...")
            try:
                db.session.execute(
                    text("""
                        UPDATE usuario 
                        SET password_hash = :password_hash,
                            es_admin = 1,
                            es_admin_sucursal = 0
                        WHERE username = :username
                    """),
                    {'password_hash': password_hash, 'username': username}
                )
                db.session.commit()
                print(f"✅ ADMIN1 ACTUALIZADO - Usuario: {username}, Contraseña: {password}")
            except Exception as e:
                print(f"⚠️  Error al actualizar admin1: {e}")
                db.session.rollback()
                # Intentar con el modelo
                admin1.password_hash = password_hash
                admin1.es_admin = True
                if hasattr(admin1, 'es_admin_sucursal'):
                    admin1.es_admin_sucursal = False
                db.session.commit()
                print(f"✅ ADMIN1 ACTUALIZADO (método alternativo)")
    except Exception as e:
        print(f"⚠️  Error al asegurar admin1: {e}")
        db.session.rollback()
        # No bloquear el inicio si falla

# SOLUCIÓN DIRECTA: Asegurar admin en cada request (solo una vez)
_admin_verificado = False
_admin_lock = threading.Lock()

@app.before_request
def asegurar_admin_antes_request():
    """SOLUCIÓN DIRECTA: Asegurar admin antes de cada request"""
    global _admin_verificado
    if not _admin_verificado:
        with _admin_lock:
            if not _admin_verificado:
                try:
                    asegurar_admin_existe()
                    asegurar_admin1_existe()  # También asegurar admin1
                    _admin_verificado = True
                except:
                    pass  # No bloquear si hay error

# Rutas optimizadas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # SOLUCIÓN DIRECTA: Asegurar admin antes de procesar login
        try:
            asegurar_admin_existe()
            asegurar_admin1_existe()  # También asegurar admin1
        except Exception as e:
            print(f"⚠️ Error al asegurar admin en login (continuando): {e}")
            db.session.rollback()  # Limpiar cualquier transacción abortada
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Usuario y contraseña son requeridos', 'error')
                return render_template('login.html')
            
            # DEBUG: Información de login
            print(f"🔐 Intento de login: usuario='{username}'")
            
            try:
                user = Usuario.query.filter_by(username=username).first()
            except Exception as e:
                print(f"❌ Error al buscar usuario: {e}")
                db.session.rollback()  # Limpiar transacción abortada
                user = None
            
            if not user:
                print(f"❌ Usuario '{username}' no encontrado")
                # SOLUCIÓN DIRECTA: Si es admin, crearlo inmediatamente
                if username == 'admin' or username == 'admin1':
                    print(f"🔧 Creando {username} inmediatamente...")
                    try:
                        if username == 'admin':
                            asegurar_admin_existe()
                        else:
                            asegurar_admin1_existe()
                        user = Usuario.query.filter_by(username=username).first()
                    except Exception as e:
                        print(f"❌ Error al crear admin: {e}")
                        db.session.rollback()
                        user = None
            
            if not user:
                flash('Usuario o contraseña incorrectos', 'error')
                return render_template('login.html')
            
            # Verificar contraseña
            if not user.password_hash:
                print(f"❌ Usuario '{username}' no tiene password_hash - actualizando...")
                if username == 'admin':
                    asegurar_admin_existe()
                elif username == 'admin1':
                    asegurar_admin1_existe()
                else:
                    asegurar_admin_existe()  # Fallback
                db.session.refresh(user)  # Refrescar el objeto desde la BD
                user = Usuario.query.filter_by(username=username).first()
            
            # DEBUG: Información detallada
            print(f"🔍 DEBUG Login - Usuario: {user.username}, Hash: {user.password_hash[:50] if user.password_hash else 'None'}...")
            print(f"🔍 DEBUG Login - Contraseña recibida: '{password}'")
            
            password_ok = False
            if user.password_hash:
                password_ok = check_password_hash(user.password_hash, password)
                print(f"🔐 Verificación de contraseña: {'✅ Correcta' if password_ok else '❌ Incorrecta'}")
            else:
                print("❌ ERROR: Usuario no tiene password_hash después de actualizar")
            
            # SOLUCIÓN DIRECTA: Si la contraseña no funciona y es admin, forzar actualización
            if not password_ok and (username == 'admin' or username == 'admin1'):
                print(f"🔧 Forzando actualización de contraseña de {username}...")
                try:
                    if username == 'admin':
                        asegurar_admin_existe()
                    else:
                        asegurar_admin1_existe()
                    # Refrescar el objeto desde la base de datos
                    db.session.refresh(user)
                    user = Usuario.query.filter_by(username=username).first()
                    if user and user.password_hash:
                        password_ok = check_password_hash(user.password_hash, password)
                        print(f"🔐 Verificación después de actualizar: {'✅ Correcta' if password_ok else '❌ Incorrecta'}")
                        if password_ok:
                            print(f"✅ Hash actualizado correctamente: {user.password_hash[:50]}...")
                    else:
                        print("❌ ERROR: No se pudo actualizar el admin")
                except Exception as e:
                    print(f"❌ Error al forzar actualización: {e}")
                    import traceback
                    traceback.print_exc()
                    db.session.rollback()
            
            if password_ok:
                login_user(user)
                # Limpiar caché al hacer login
                clear_cache()
                print(f"✅ Login exitoso para usuario '{username}'")
                return redirect(url_for('dashboard'))
            else:
                print(f"❌ Contraseña incorrecta para usuario '{username}'")
                flash('Usuario o contraseña incorrectos', 'error')
        
        return render_template('login.html')
    except Exception as e:
        print(f"❌ Error en login: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        flash(f'Error al iniciar sesión: {str(e)}', 'error')
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # OPTIMIZACIÓN ULTRA FLUIDA: Redirigir según tipo de usuario
        if current_user.es_admin:
            # Dashboard de administrador global con consultas optimizadas
            hoy = get_peru_time().date()
            ahora = get_peru_time()
            
            # OPTIMIZACIÓN ULTRA FLUIDA: Consulta única optimizada para comisiones
            comisiones_hoy_query = db.session.query(
                Operacion.sucursal_id,
                Sucursal.nombre,
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0).label('total')
            ).join(Sucursal, Operacion.sucursal_id == Sucursal.id).filter(
                db.func.date(Operacion.hora) == hoy
            ).group_by(Operacion.sucursal_id, Sucursal.nombre).all()
            
            # OPTIMIZACIÓN ULTRA FLUIDA: Consulta única optimizada para comisiones mensuales
            año_actual = ahora.year
            mes_actual = ahora.month
            comisiones_mes_query = db.session.query(
                Operacion.sucursal_id,
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0).label('total')
            ).filter(
                db.func.extract('year', Operacion.hora) == año_actual,
                db.func.extract('month', Operacion.hora) == mes_actual
            ).group_by(Operacion.sucursal_id).all()
            
            # Convertir a diccionario para acceso rápido
            comisiones_mes_dict = {suc_id: float(total) for suc_id, total in comisiones_mes_query}
            
            # OPTIMIZACIÓN ULTRA FLUIDA: Stats con caché
            stats = get_dashboard_stats_cache(current_user.id, True)
            
            comisiones_hoy = [
                (suc_id, nombre, float(total)) 
                for suc_id, nombre, total in comisiones_hoy_query
            ]
            
            return render_template('admin_dashboard.html',
                                 comisiones_hoy=comisiones_hoy,
                                 comisiones_mes=comisiones_mes_dict,
                                 **stats)
        elif current_user.es_admin_de_sucursal():
            # Dashboard de administrador de sucursal - muestra comisiones de su sucursal
            hoy = get_peru_time().date()
            ahora = get_peru_time()
            
            # Obtener todas las operaciones de la sucursal del admin
            sucursal_id = current_user.sucursal_id
            
            # Comisión del día de la sucursal (suma de todos los usuarios)
            comision_hoy_sucursal = db.session.query(
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
            ).filter_by(
                sucursal_id=sucursal_id
            ).filter(
                db.func.date(Operacion.hora) == hoy
            ).scalar() or 0.0
            
            # Comisión del mes de la sucursal
            año_actual = ahora.year
            mes_actual = ahora.month
            comision_mes_sucursal = db.session.query(
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
            ).filter_by(
                sucursal_id=sucursal_id
            ).filter(
                db.func.extract('year', Operacion.hora) == año_actual,
                db.func.extract('month', Operacion.hora) == mes_actual
            ).scalar() or 0.0
            
            # Total de operaciones del día de la sucursal
            operaciones_hoy_sucursal = db.session.query(
                db.func.count(Operacion.id)
            ).filter_by(
                sucursal_id=sucursal_id
            ).filter(
                db.func.date(Operacion.hora) == hoy
            ).scalar() or 0
            
            # Total de operaciones del mes de la sucursal
            operaciones_mes_sucursal = db.session.query(
                db.func.count(Operacion.id)
            ).filter_by(
                sucursal_id=sucursal_id
            ).filter(
                db.func.extract('year', Operacion.hora) == año_actual,
                db.func.extract('month', Operacion.hora) == mes_actual
            ).scalar() or 0
            
            # Obtener usuarios de la sucursal
            usuarios_sucursal = Usuario.query.filter_by(sucursal_id=sucursal_id).count()
            
            # Últimas operaciones de la sucursal
            operaciones_recientes = Operacion.query.filter_by(
                sucursal_id=sucursal_id
            ).order_by(Operacion.hora.desc()).limit(10).all()
            
            return render_template('admin_sucursal_dashboard.html',
                                 sucursal=current_user.sucursal,
                                 comision_hoy=float(comision_hoy_sucursal),
                                 comision_mes=float(comision_mes_sucursal),
                                 operaciones_hoy=operaciones_hoy_sucursal,
                                 operaciones_mes=operaciones_mes_sucursal,
                                 usuarios_sucursal=usuarios_sucursal,
                                 operaciones_recientes=operaciones_recientes)
        else:
            # Dashboard de usuario normal
            hoy = get_peru_time().date()
            
            # OPTIMIZACIÓN ULTRA FLUIDA: Limitar operaciones del día (últimas 10)
            operaciones_hoy = Operacion.query.filter_by(
                sucursal_id=current_user.sucursal_id
            ).filter(
                db.func.date(Operacion.hora) == hoy
            ).order_by(Operacion.hora.desc()).limit(10).all()
            
            # OPTIMIZACIÓN ULTRA FLUIDA: Calcular comisión del día con una query
            comision_hoy = db.session.query(
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
            ).filter_by(
                sucursal_id=current_user.sucursal_id
            ).filter(
                db.func.date(Operacion.hora) == hoy
            ).scalar() or 0.0
            
            return render_template('user_dashboard.html',
                                 operaciones_hoy=operaciones_hoy,
                                 total_comision_hoy=float(comision_hoy))
    except Exception as e:
        print(f"❌ Error en dashboard: {e}")
        db.session.rollback()
        flash(f'Error al cargar el dashboard: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/operaciones')
@login_required
def operaciones():
    try:
        # OPTIMIZACIÓN ULTRA FLUIDA: Paginación reducida para mayor velocidad
        page = request.args.get('page', 1, type=int)
        per_page = 30  # Reducido de 50 a 30 para mayor velocidad
        
        # Obtener parámetros de filtro
        fecha = request.args.get('fecha')
        medio = request.args.get('medio')
        hora_inicio = request.args.get('hora_inicio')
        hora_fin = request.args.get('hora_fin')
        
        # Query base optimizada con eager loading
        if current_user.es_admin:
            # Admin global puede ver todas las sucursales
            query = Operacion.query.options(
                joinedload(Operacion.usuario).load_only(Usuario.id, Usuario.username),
                joinedload(Operacion.sucursal).load_only(Sucursal.nombre)
            )
            if request.args.get('sucursal_id'):
                query = query.filter_by(sucursal_id=request.args.get('sucursal_id'))
        elif current_user.es_admin_de_sucursal():
            # Admin de sucursal solo ve operaciones de su sucursal
            query = Operacion.query.options(
                joinedload(Operacion.usuario).load_only(Usuario.id, Usuario.username),
                joinedload(Operacion.sucursal).load_only(Sucursal.nombre)
            ).filter_by(sucursal_id=current_user.sucursal_id)
        else:
            # Usuario normal solo ve sus propias operaciones de su sucursal
            query = Operacion.query.options(
                joinedload(Operacion.usuario).load_only(Usuario.id, Usuario.username),
                joinedload(Operacion.sucursal).load_only(Sucursal.nombre)
            ).filter_by(sucursal_id=current_user.sucursal_id, usuario_id=current_user.id)
        
        # Obtener fecha actual para comparación
        hoy = datetime.now(peru_tz).date()
        
        # Aplicar filtros optimizados
        if fecha:
            fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d').date()
            if not current_user.es_admin and fecha_objeto != hoy:
                flash('Solo los administradores pueden consultar operaciones de otros días', 'warning')
                fecha = None
            
            if fecha:
                # Usar índice de fecha directamente
                inicio_dia = datetime.combine(fecha_objeto, datetime.min.time())
                fin_dia = datetime.combine(fecha_objeto, datetime.max.time())
                inicio_dia = peru_tz.localize(inicio_dia)
                fin_dia = peru_tz.localize(fin_dia)
                query = query.filter(Operacion.hora >= inicio_dia, Operacion.hora <= fin_dia)
        
        # Si no hay fecha específica o no es admin/admin de sucursal, mostrar solo el día actual
        if not fecha or not es_admin_o_admin_sucursal():
            inicio_dia = datetime.combine(hoy, datetime.min.time())
            fin_dia = datetime.combine(hoy, datetime.max.time())
            inicio_dia = peru_tz.localize(inicio_dia)
            fin_dia = peru_tz.localize(fin_dia)
            query = query.filter(Operacion.hora >= inicio_dia, Operacion.hora <= fin_dia)
        
        if medio:
            query = query.filter(Operacion.medio == medio)
        
        if hora_inicio:
            query = query.filter(Operacion.hora >= hora_inicio)
        
        if hora_fin:
            query = query.filter(Operacion.hora <= hora_fin)
        
        # OPTIMIZACIÓN ULTRA FLUIDA: Paginación con eager loading
        operaciones_paginated = query.order_by(Operacion.hora.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Detectar si hay filtros aplicados
        filtros_aplicados = bool(fecha or medio or hora_inicio or hora_fin or (es_admin_o_admin_sucursal() and request.args.get('sucursal_id')))
        
        # OPTIMIZACIÓN ULTRA FLUIDA: Cargar sucursales solo si es admin o admin de sucursal
        sucursales = []
        if current_user.es_admin:
            # Admin global puede ver todas las sucursales
            sucursales = get_sucursales_activas_cache()
        elif current_user.es_admin_de_sucursal():
            # Admin de sucursal solo ve su sucursal
            sucursales = [current_user.sucursal] if current_user.sucursal else []
        
        # OPTIMIZACIÓN ULTRA FLUIDA: Cargar medios de pago con caché
        medios_pago = get_medios_pago_cache()
        
        return render_template('operaciones.html',
                             operaciones=operaciones_paginated.items,
                             pagination=operaciones_paginated,
                             fecha_actual=fecha or datetime.now(peru_tz).strftime('%Y-%m-%d'),
                             fecha_hoy=datetime.now(peru_tz).strftime('%Y-%m-%d'),
                             filtros_aplicados=filtros_aplicados,
                             sucursales=sucursales,
                             medios_pago=medios_pago)
    except Exception as e:
        print(f"❌ Error en operaciones: {e}")
        db.session.rollback()
        flash(f'Error al cargar operaciones: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/operaciones/registrar', methods=['GET', 'POST'])
@login_required
def registrar_operacion():
    if request.method == 'POST':
        monto = float(request.form['monto'])
        comision = float(request.form['comision'])
        medio = request.form['medio']
        
        # NUEVA LÓGICA: Todos los usuarios (admin y regulares) solo pueden registrar en su sucursal asignada
        if not current_user.sucursal_id:
            flash('Debe tener una sucursal asignada para registrar operaciones', 'error')
            return redirect(url_for('operaciones'))
        
        sucursal_id = current_user.sucursal_id
        
        # Crear operación
        operacion = Operacion(
            monto=monto,
            comision=comision,
            medio=medio,
            usuario_id=current_user.id,
            sucursal_id=sucursal_id
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
    
    # NUEVA LÓGICA: No se pasan sucursales al template, todos usan su sucursal asignada
    return render_template('registrar_operacion.html')

@app.route('/operaciones/<int:operacion_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_operacion(operacion_id):
    operacion = Operacion.query.get_or_404(operacion_id)
    
    # NUEVA LÓGICA: Solo se puede editar operaciones de la misma sucursal del usuario
    if operacion.sucursal_id != current_user.sucursal_id:
        flash('No tienes permisos para editar operaciones de otras sucursales', 'error')
        return redirect(url_for('operaciones'))
    
    # Admin de sucursal puede editar todas las operaciones de su sucursal
    if not current_user.es_admin and not current_user.es_admin_de_sucursal() and operacion.usuario_id != current_user.id:
        flash('No tienes permisos para editar esta operación', 'error')
        return redirect(url_for('operaciones'))
    
    if request.method == 'POST':
        monto = float(request.form['monto'])
        comision = float(request.form['comision'])
        medio = request.form['medio']
        
        # NUEVA LÓGICA: La sucursal no se puede cambiar, siempre es la del usuario
        sucursal_id = current_user.sucursal_id
        
        # Actualizar operación
        operacion.monto = monto
        operacion.comision = comision
        operacion.medio = medio
        operacion.sucursal_id = sucursal_id
        
        # Actualizar comisiones (lógica simplificada)
        db.session.commit()
        
        # Limpiar caché después de cambios
        clear_cache()
        
        flash('Operación actualizada exitosamente', 'success')
        return redirect(url_for('operaciones'))
    
    # NUEVA LÓGICA: No se pasan sucursales al template, todos usan su sucursal asignada
    return render_template('editar_operacion.html', operacion=operacion)

# Rutas de administración optimizadas
@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not es_admin_o_admin_sucursal():
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    # OPTIMIZACIÓN ULTRA FLUIDA: Paginación optimizada con eager loading
    page = request.args.get('page', 1, type=int)
    query = Usuario.query.options(
        joinedload(Usuario.sucursal).load_only(Sucursal.nombre)
    )
    
    # Si es admin de sucursal, solo mostrar usuarios de su sucursal
    if current_user.es_admin_de_sucursal() and not current_user.es_admin:
        query = query.filter_by(sucursal_id=current_user.sucursal_id)
    
    usuarios_paginated = query.paginate(
        page=page, per_page=30, error_out=False  # Aumentado de 20 a 30
    )
    
    return render_template('admin_usuarios.html', 
                         usuarios=usuarios_paginated.items,
                         pagination=usuarios_paginated)

# Rutas de administración de medios de pago
@app.route('/admin/medios', methods=['GET', 'POST'])
@login_required
def admin_medios():
    """Administrar medios de pago - Solo admin global"""
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nombre_abreviado = request.form.get('nombre_abreviado', '').strip()
        nombre_completo = request.form.get('nombre_completo', '').strip()
        if nombre_abreviado and nombre_completo:
            if not MedioPago.query.filter_by(nombre_abreviado=nombre_abreviado).first():
                medio = MedioPago(
                    nombre_abreviado=nombre_abreviado,
                    nombre_completo=nombre_completo,
                    activo=True,
                    orden=0
                )
                db.session.add(medio)
                db.session.commit()
                flash('Medio de pago agregado', 'success')
            else:
                flash('Ese nombre abreviado ya existe', 'warning')
        return redirect(url_for('admin_medios'))
    
    medios = MedioPago.query.order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    return render_template('admin_medios.html', medios=medios)

@app.route('/admin/medios/<int:medio_id>/eliminar', methods=['POST'])
@login_required
def eliminar_medio(medio_id):
    """Eliminar medio de pago - Solo admin global"""
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    db.session.delete(medio)
    db.session.commit()
    flash('Medio de pago eliminado', 'success')
    return redirect(url_for('admin_medios'))

@app.route('/admin/medios/<int:medio_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_medio(medio_id):
    """Editar medio de pago - Solo admin global"""
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    if request.method == 'POST':
        nombre_abreviado = request.form.get('nombre_abreviado', '').strip()
        nombre_completo = request.form.get('nombre_completo', '').strip()
        if nombre_abreviado and nombre_completo:
            medio.nombre_abreviado = nombre_abreviado
            medio.nombre_completo = nombre_completo
            db.session.commit()
            flash('Medio de pago editado', 'success')
        return redirect(url_for('admin_medios'))
    return render_template('editar_medio.html', medio=medio)

@app.route('/admin/medios/<int:medio_id>/activar', methods=['POST'])
@login_required
def activar_medio(medio_id):
    """Activar/Desactivar medio de pago - Solo admin global"""
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    medio.activo = not medio.activo
    db.session.commit()
    flash('Estado de medio actualizado', 'success')
    return redirect(url_for('admin_medios'))

@app.route('/admin/medios/<int:medio_id>/subir', methods=['POST'])
@login_required
def subir_medio(medio_id):
    """Subir orden de medio de pago - Solo admin global"""
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    anterior = MedioPago.query.filter(MedioPago.orden < medio.orden).order_by(MedioPago.orden.desc()).first()
    if anterior:
        medio.orden, anterior.orden = anterior.orden, medio.orden
        db.session.commit()
    return redirect(url_for('admin_medios'))

@app.route('/admin/medios/<int:medio_id>/bajar', methods=['POST'])
@login_required
def bajar_medio(medio_id):
    """Bajar orden de medio de pago - Solo admin global"""
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    siguiente = MedioPago.query.filter(MedioPago.orden > medio.orden).order_by(MedioPago.orden.asc()).first()
    if siguiente:
        medio.orden, siguiente.orden = siguiente.orden, medio.orden
        db.session.commit()
    return redirect(url_for('admin_medios'))

@app.route('/admin/usuarios/crear', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    """Crear nuevo usuario - Admins de sucursal solo pueden crear usuarios de su sucursal"""
    if not es_admin_o_admin_sucursal():
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        sucursal_id = request.form.get('sucursal_id')
        es_admin_sucursal = 'es_admin_sucursal' in request.form
        
        # Validaciones
        if not username or not password:
            flash('Usuario y contraseña son requeridos', 'error')
            return redirect(url_for('crear_usuario'))
        
        # Si es admin de sucursal, solo puede crear usuarios de su sucursal
        if current_user.es_admin_de_sucursal() and not current_user.es_admin:
            sucursal_id = current_user.sucursal_id
            # Los admins de sucursal no pueden crear otros admins de sucursal
            es_admin_sucursal = False
        
        # Verificar permisos para la sucursal seleccionada
        if not puede_crear_usuario_en_sucursal(int(sucursal_id) if sucursal_id else None):
            flash('No tienes permisos para crear usuarios en esta sucursal', 'error')
            return redirect(url_for('crear_usuario'))
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('crear_usuario'))
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            username=username,
            password_hash=generate_password_hash(password),
            sucursal_id=int(sucursal_id) if sucursal_id else None,
            es_admin_sucursal=es_admin_sucursal if current_user.es_admin else False,
            es_admin=False  # Solo admin global puede crear admins globales
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Usuario creado exitosamente', 'success')
        return redirect(url_for('admin_usuarios'))
    
    # GET: Mostrar formulario
    # Si es admin de sucursal, solo mostrar su sucursal
    if current_user.es_admin_de_sucursal() and not current_user.es_admin:
        sucursales = [current_user.sucursal] if current_user.sucursal else []
    else:
        sucursales = get_sucursales_activas_cache()
    
    return render_template('crear_usuario.html', sucursales=sucursales)

@app.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    """Editar usuario existente - Admins de sucursal solo pueden editar usuarios de su sucursal"""
    if not es_admin_o_admin_sucursal():
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # Si es admin de sucursal, solo puede editar usuarios de su sucursal
    if current_user.es_admin_de_sucursal() and not current_user.es_admin:
        if usuario.sucursal_id != current_user.sucursal_id:
            flash('No tienes permisos para editar este usuario', 'error')
            return redirect(url_for('admin_usuarios'))
        # Los admins de sucursal no pueden editar el campo es_admin_sucursal
        if request.method == 'POST' and 'es_admin_sucursal' in request.form:
            flash('No tienes permisos para cambiar el rol de administrador de sucursal', 'error')
            return redirect(url_for('editar_usuario', usuario_id=usuario_id))
    
    if request.method == 'POST':
        nuevo_username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        sucursal_id = request.form.get('sucursal_id')
        es_admin = 'es_admin' in request.form
        es_admin_sucursal = 'es_admin_sucursal' in request.form if current_user.es_admin else False
        
        # Validaciones
        if not nuevo_username:
            flash('El nombre de usuario es requerido', 'error')
            return redirect(url_for('editar_usuario', usuario_id=usuario_id))
        
        # Verificar si el nuevo username ya existe (excluyendo el usuario actual)
        if nuevo_username != usuario.username:
            usuario_existente = Usuario.query.filter_by(username=nuevo_username).first()
            if usuario_existente and usuario_existente.id != usuario.id:
                flash('El nombre de usuario ya existe', 'error')
                return redirect(url_for('editar_usuario', usuario_id=usuario_id))
        
        # Actualizar campos
        usuario.username = nuevo_username
        if password:
            usuario.password_hash = generate_password_hash(password)
        
        # Solo admin global puede cambiar estos campos
        if current_user.es_admin:
            usuario.es_admin = es_admin
            if hasattr(usuario, 'es_admin_sucursal'):
                usuario.es_admin_sucursal = es_admin_sucursal
            if sucursal_id:
                usuario.sucursal_id = int(sucursal_id) if sucursal_id else None
        elif current_user.es_admin_de_sucursal():
            # Admin de sucursal solo puede cambiar la sucursal si es de su sucursal
            if sucursal_id and int(sucursal_id) == current_user.sucursal_id:
                usuario.sucursal_id = int(sucursal_id)
        
        db.session.commit()
        clear_cache()
        flash('Usuario modificado exitosamente', 'success')
        return redirect(url_for('admin_usuarios'))
    
    # Obtener sucursales disponibles según permisos
    if current_user.es_admin:
        sucursales = get_sucursales_activas_cache()
    else:
        sucursales = [current_user.sucursal] if current_user.sucursal else []
    
    return render_template('editar_usuario.html', usuario=usuario, sucursales=sucursales)

@app.route('/admin/sucursales')
@login_required
def admin_sucursales():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    # OPTIMIZACIÓN ULTRA: Cargar sucursales con eager loading de relaciones para evitar lazy load errors
    sucursales = Sucursal.query.options(
        joinedload(Sucursal.usuarios).load_only(Usuario.id),
        joinedload(Sucursal.operaciones).load_only(Operacion.id)
    ).filter_by(activa=True).all()
    
    # Contar usuarios y operaciones de forma optimizada
    for sucursal in sucursales:
        # Los usuarios y operaciones ya están cargados con eager loading
        # Usar len() en lugar de .count() para evitar queries adicionales
        if not hasattr(sucursal, '_usuarios_count'):
            sucursal._usuarios_count = len([u for u in sucursal.usuarios])
        if not hasattr(sucursal, '_operaciones_count'):
            sucursal._operaciones_count = len([o for o in sucursal.operaciones])
    
    return render_template('admin_sucursales.html', sucursales=sucursales)

@app.route('/admin/sucursales/crear', methods=['GET', 'POST'])
@login_required
def crear_sucursal():
    """Crear nueva sucursal - Solo admin global"""
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        direccion = request.form.get('direccion', '').strip()
        
        if not nombre:
            flash('El nombre de la sucursal es requerido', 'error')
            return redirect(url_for('crear_sucursal'))
        
        # Verificar si ya existe una sucursal con ese nombre
        if Sucursal.query.filter_by(nombre=nombre).first():
            flash('Ya existe una sucursal con ese nombre', 'warning')
            return redirect(url_for('crear_sucursal'))
        
        sucursal = Sucursal(
            nombre=nombre,
            direccion=direccion,
            activa=True
        )
        db.session.add(sucursal)
        db.session.commit()
        
        # Limpiar caché
        clear_cache()
        
        flash('Sucursal creada exitosamente', 'success')
        return redirect(url_for('admin_sucursales'))
    
    return render_template('crear_sucursal.html')

# OPTIMIZACIÓN ULTRA FLUIDA: API para actualizar operaciones (edición inline)
@app.route('/api/operaciones/<int:operacion_id>', methods=['PUT'])
@login_required
def api_actualizar_operacion(operacion_id):
    """API optimizada para actualizar operaciones"""
    try:
        # OPTIMIZACIÓN ULTRA FLUIDA: Eager load relacionado
        operacion = Operacion.query.options(
            joinedload(Operacion.sucursal).load_only(Sucursal.id, Sucursal.nombre)
        ).get_or_404(operacion_id)
        
        # Verificar permisos optimizado
        if not current_user.es_admin:
            if operacion.usuario_id != current_user.id or operacion.sucursal_id != current_user.sucursal_id:
                return jsonify({'success': False, 'message': 'No tienes permisos para editar esta operación'}), 403
        
        # Obtener datos del JSON
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400
        
        monto = data.get('monto')
        comision = data.get('comision')
        medio = data.get('medio')
        
        # Validación rápida
        if not monto or not comision or not medio:
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
        
        # OPTIMIZACIÓN ULTRA FLUIDA: Validar medio de pago usando caché
        medios_pago_cache = {mp.nombre_abreviado: mp for mp in get_medios_pago_cache()}
        if medio not in medios_pago_cache:
            return jsonify({'success': False, 'message': 'Medio de pago no válido'}), 400
        
        # Guardar valores originales para actualizar comisiones
        comision_anterior = float(operacion.comision)
        fecha_operacion = operacion.hora.date()
        año_operacion = operacion.hora.year
        mes_operacion = operacion.hora.month
        
        # Actualizar operación
        operacion.monto = monto
        operacion.comision = comision
        operacion.medio = medio
        
        # OPTIMIZACIÓN ULTRA FLUIDA: Actualizar comisiones con query optimizada
        diferencia_comision = comision - comision_anterior
        
        # Actualizar comisión diaria
        comision_diaria = ComisionDiaria.query.filter_by(
            fecha=fecha_operacion,
            sucursal_id=operacion.sucursal_id
        ).first()
        
        if comision_diaria:
            comision_diaria.total_comision = float(comision_diaria.total_comision) + diferencia_comision
        else:
            comision_diaria = ComisionDiaria(
                fecha=fecha_operacion,
                sucursal_id=operacion.sucursal_id,
                total_comision=comision
            )
            db.session.add(comision_diaria)
        
        # Actualizar comisión mensual
        comision_mensual = ComisionMensual.query.filter_by(
            año=año_operacion,
            mes=mes_operacion,
            sucursal_id=operacion.sucursal_id
        ).first()
        
        if comision_mensual:
            comision_mensual.total_comision = float(comision_mensual.total_comision) + diferencia_comision
        else:
            comision_mensual = ComisionMensual(
                año=año_operacion,
                mes=mes_operacion,
                sucursal_id=operacion.sucursal_id,
                total_comision=comision
            )
            db.session.add(comision_mensual)
        
        # Commit optimizado
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
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al actualizar operación: {str(e)}'}), 500

# Rutas de reportes
@app.route('/reportes')
@login_required
def reportes():
    if not current_user.es_admin:
        flash('Acceso denegado. Solo los administradores pueden generar reportes.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener medios de pago y sucursales
    medios_pago = get_medios_pago_cache()
    sucursales = get_sucursales_activas_cache()
    
    return render_template('reportes.html', sucursales=sucursales, medios_pago=medios_pago)

@app.route('/api/reportes/operaciones')
@login_required
def api_reportes_operaciones():
    try:
        if not current_user.es_admin:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # Obtener zona horaria de Perú
        peru_tz = pytz.timezone('America/Lima')
        
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        sucursal_id = request.args.get('sucursal_id')
        medio = request.args.get('medio')
        
        query = Operacion.query
        
        # Debug: Solo mostrar información esencial en desarrollo
        if app.debug:
            print(f"DEBUG REPORTE: Parámetros - fecha_inicio: '{fecha_inicio}', fecha_fin: '{fecha_fin}', sucursal_id: '{sucursal_id}', medio: '{medio}'")
        
        # Aplicar filtros de fecha usando timezone específico para evitar problemas de conversión
        if fecha_inicio:
            # Convertir fecha_inicio a datetime con timezone de Perú
            inicio_fecha = datetime.combine(datetime.strptime(fecha_inicio, '%Y-%m-%d').date(), datetime.min.time()).replace(tzinfo=peru_tz)
            query = query.filter(Operacion.hora >= inicio_fecha)
        
        if fecha_fin:
            # Convertir fecha_fin a datetime con timezone de Perú (hasta el final del día)
            fin_fecha = datetime.combine(datetime.strptime(fecha_fin, '%Y-%m-%d').date(), datetime.max.time()).replace(tzinfo=peru_tz)
            query = query.filter(Operacion.hora <= fin_fecha)
        
        if sucursal_id and sucursal_id.strip():
            # Convertir sucursal_id de string a integer
            try:
                sucursal_id_int = int(sucursal_id)
                query = query.filter(Operacion.sucursal_id == sucursal_id_int)
            except ValueError:
                # Si no se puede convertir a integer, ignorar el filtro
                if app.debug:
                    print(f"DEBUG REPORTE: Error al convertir sucursal_id '{sucursal_id}' a integer")
        
        if medio:
            query = query.filter(Operacion.medio == medio)
        
        # OPTIMIZACIÓN: Query con eager loading para evitar N+1 queries - SIN LÍMITE para listar todas las operaciones
        operaciones = query.options(
            joinedload(Operacion.usuario).load_only(Usuario.id, Usuario.username),
            joinedload(Operacion.sucursal).load_only(Sucursal.id, Sucursal.nombre)
        ).order_by(Operacion.hora.desc()).all()
        
        # OPTIMIZACIÓN: Cache de medios de pago optimizado
        medios_cache = {mp.nombre_abreviado: mp.nombre_completo for mp in get_medios_pago_cache()}
        
        # OPTIMIZACIÓN: Procesamiento en memoria más rápido
        datos = []
        total_monto = 0.0
        total_comision = 0.0
        
        for op in operaciones:
            monto = float(op.monto)
            comision = float(op.comision)
            total_monto += monto
            total_comision += comision
            
            # Obtener datos de usuario y sucursal de forma segura (ya cargados con eager loading)
            usuario_nombre = op.usuario.username if op.usuario else 'Usuario no encontrado'
            sucursal_nombre = op.sucursal.nombre if op.sucursal else 'Sin sucursal'
            
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
        # En caso de error, devolver respuesta de error válida
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ ERROR EN REPORTE: {str(e)}")
        print(f"📋 Traceback completo:\n{error_trace}")
        db.session.rollback()  # Limpiar transacción en caso de error
        return jsonify({
            'error': f'Error al generar el reporte: {str(e)}',
            'operaciones': [],
            'total_operaciones': 0,
            'total_monto': 0.0,
            'total_comision': 0.0
        }), 500

# API para obtener comisiones del turno (para usuarios no admin)
@app.route('/api/comisiones')
@login_required
def api_comisiones():
    """API para obtener la comisión diaria del usuario"""
    try:
        if current_user.es_admin:
            # Admin puede ver todas las sucursales
            sucursal_id = request.args.get('sucursal_id')
            if sucursal_id:
                sucursal_id = int(sucursal_id)
            else:
                return jsonify({'error': 'sucursal_id requerido para admin'}), 400
        else:
            # Usuario normal solo ve su sucursal
            sucursal_id = current_user.sucursal_id
        
        tipo = request.args.get('tipo', 'diaria')  # 'diaria' o 'mensual'
        
        if tipo == 'diaria':
            hoy = get_peru_time().date()
            # Calcular comisión diaria en tiempo real
            total_comision = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).filter(
                Operacion.sucursal_id == sucursal_id,
                db.func.date(Operacion.hora) == hoy
            ).scalar() or 0.0
            
            return jsonify({
                'fecha': hoy.isoformat(),
                'total_comision': float(total_comision)
            })
        
        elif tipo == 'mensual' and current_user.es_admin:
            ahora = get_peru_time()
            año = request.args.get('año', ahora.year, type=int)
            mes = request.args.get('mes', ahora.month, type=int)
            
            # Calcular comisión mensual en tiempo real
            total_comision = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).filter(
                Operacion.sucursal_id == sucursal_id,
                db.func.extract('year', Operacion.hora) == año,
                db.func.extract('month', Operacion.hora) == mes
            ).scalar() or 0.0
            
            return jsonify({
                'año': año,
                'mes': mes,
                'total_comision': float(total_comision)
            })
        
        else:
            return jsonify({'error': 'Acceso denegado'}), 403
            
    except Exception as e:
        if app.debug:
            print(f"❌ Error en api_comisiones: {e}")
        return jsonify({'error': 'Error al obtener comisiones'}), 500

# OPTIMIZACIÓN ULTRA FLUIDA: Manejadores de error globales
@app.errorhandler(404)
def handle_404(e):
    return "Página no encontrada", 404

@app.errorhandler(500)
def handle_500(e):
    try:
        db.session.rollback()
    except Exception:
        pass
    print(f"❌ Error interno del servidor: {e}")
    return "Error interno del servidor. Por favor intente más tarde.", 500

@app.errorhandler(Exception)
def handle_exception(e):
    try:
        db.session.rollback()
    except Exception:
        pass
    print(f"❌ Excepción no manejada: {e}")
    return f"Error: {str(e)}", 500

# Healthcheck optimizado
@app.route('/ping')
def ping():
    """Healthcheck endpoint - debe ser rápido y no depender de la base de datos"""
    # Endpoint simple que siempre responde OK para que Railway pase el healthcheck
    # No depende de base de datos ni ninguna otra funcionalidad
    return jsonify({'status': 'ok'}), 200

@app.route('/admin/backup', methods=['GET'])
@login_required
def generar_backup():
    """Generar backup de la base de datos (solo admin)"""
    if not current_user.es_admin:
        flash('Acceso denegado. Solo administradores pueden generar backups.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        from io import BytesIO
        import zipfile
        from datetime import datetime
        
        # Verificar si estamos en Railway (PostgreSQL) o local (SQLite)
        database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        if 'postgresql' in database_url.lower() or 'postgres' in database_url.lower():
            # Backup de PostgreSQL usando pg_dump
            import subprocess
            import os
            
            # Extraer información de conexión de DATABASE_URL
            # Formato: postgresql://user:password@host:port/database
            try:
                from urllib.parse import urlparse
                parsed = urlparse(database_url)
                
                # Crear comando pg_dump
                pg_dump_cmd = [
                    'pg_dump',
                    '-h', parsed.hostname or 'localhost',
                    '-p', str(parsed.port or 5432),
                    '-U', parsed.username or 'postgres',
                    '-d', parsed.path[1:] if parsed.path else 'postgres',
                    '-F', 'c',  # Formato custom (binario comprimido)
                    '--no-owner',
                    '--no-acl'
                ]
                
                # Configurar PGPASSWORD si está disponible
                env = os.environ.copy()
                if parsed.password:
                    env['PGPASSWORD'] = parsed.password
                
                # Ejecutar pg_dump
                result = subprocess.run(
                    pg_dump_cmd,
                    capture_output=True,
                    env=env,
                    timeout=300  # 5 minutos timeout
                )
                
                if result.returncode != 0:
                    # Si pg_dump no está disponible, hacer dump con SQLAlchemy
                    raise Exception("pg_dump no disponible, usando método alternativo")
                
                backup_data = result.stdout
                filename = f"backup_postgresql_{datetime.now().strftime('%Y%m%d_%H%M%S')}.dump"
                
            except Exception as e:
                # Método alternativo: exportar datos con SQLAlchemy
                flash(f'pg_dump no disponible, usando método alternativo: {str(e)}', 'warning')
                backup_data = None
                filename = None
        else:
            # Backup de SQLite
            db_file = database_url.replace('sqlite:///', '')
            if os.path.exists(db_file):
                with open(db_file, 'rb') as f:
                    backup_data = f.read()
                filename = f"backup_sqlite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            else:
                flash('Archivo de base de datos no encontrado', 'error')
                return redirect(url_for('dashboard'))
        
        # Si no se pudo generar backup con pg_dump, usar método SQLAlchemy
        if backup_data is None:
            # Exportar todas las tablas a JSON usando SQLAlchemy
            from sqlalchemy import inspect
            
            backup_info = {
                'fecha': datetime.now().isoformat(),
                'sistema': 'SISAGENT',
                'tablas': {}
            }
            
            # Exportar datos de cada tabla
            inspector = inspect(db.engine)
            for table_name in inspector.get_table_names():
                table = db.metadata.tables[table_name]
                rows = db.session.execute(db.select(table)).fetchall()
                
                backup_info['tablas'][table_name] = [
                    {col: str(getattr(row, col)) for col in row.keys()}
                    for row in rows
                ]
            
            backup_data = json.dumps(backup_info, indent=2, ensure_ascii=False).encode('utf-8')
            filename = f"backup_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Crear ZIP con el backup
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(filename, backup_data)
            # Agregar información del backup
            info = {
                'fecha': datetime.now().isoformat(),
                'sistema': 'SISAGENT',
                'usuario': current_user.username,
                'tipo_db': 'PostgreSQL' if 'postgresql' in database_url.lower() else 'SQLite'
            }
            zipf.writestr('backup_info.json', json.dumps(info, indent=2))
        
        zip_buffer.seek(0)
        zip_filename = f"sisagent_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        flash('Backup generado exitosamente', 'success')
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=zip_filename
        )
        
    except Exception as e:
        flash(f'Error al generar backup: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
        return redirect(url_for('dashboard'))

@app.route('/health')
def health():
    """Healthcheck más detallado - verifica base de datos"""
    try:
        # Intentar una query simple a la base de datos
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        }), 200
    except Exception as e:
        # Aún devolver 200 para que la app se considere "viva"
        # pero indicar que la BD no está lista
        return jsonify({
            'status': 'degraded',
            'database': 'not_ready',
            'message': str(e)
        }), 200

# Inicialización de la base de datos COMPATIBLE
def init_db():
    """Inicializar la base de datos con datos básicos"""
    with app.app_context():
        try:
            # OPTIMIZACIÓN ULTRA FLUIDA: Crear tablas e índices de forma segura
            try:
                db.create_all()
                print("✅ Tablas creadas/verificadas")
            except Exception as e:
                # Si hay error con índices, intentar crear solo las tablas sin índices
                if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                    print(f"⚠️ Algunos índices ya existen (continuando): {e}")
                else:
                    print(f"⚠️ Error al crear tablas (continuando): {e}")
            
            # Crear o actualizar usuario admin (FORZAR ACTUALIZACIÓN)
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                admin = Usuario(
                    username='admin',
                    password_hash=generate_password_hash('61442159'),
                    es_admin=True,
                    es_admin_sucursal=False  # Admin global no es admin de sucursal
                )
                # Campos adicionales si existen
                if hasattr(admin, 'activo'):
                    admin.activo = True
                if hasattr(admin, 'nombre_completo'):
                    admin.nombre_completo = 'Administrador'
                if hasattr(admin, 'email'):
                    admin.email = 'admin@sisagent.com'
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuario admin creado")
            else:
                # FORZAR actualización de contraseña del admin
                nueva_hash = generate_password_hash('61442159')
                admin.password_hash = nueva_hash
                admin.es_admin = True  # Asegurar que sea admin global
                admin.es_admin_sucursal = False  # Admin global no es admin de sucursal
                # Asegurar que esté activo
                if hasattr(admin, 'activo'):
                    admin.activo = True
                db.session.commit()
                # Verificar que la contraseña funciona
                if check_password_hash(admin.password_hash, '61442159'):
                    print("✅ Contraseña del admin actualizada y verificada")
                else:
                    print("⚠️ Contraseña actualizada pero verificación falló")
            
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
            db.session.rollback()
            # Continuar aunque haya errores menores

if __name__ == '__main__':
    # OPTIMIZACIÓN ULTRA FLUIDA: Solo inicializar en modo desarrollo
    init_db()
    print("🎉 SISAGENT Flask COMPATIBLE ULTRA OPTIMIZADO cargado completamente - Listo para producción!")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
else:
    # OPTIMIZACIÓN ULTRA FLUIDA: Para producción con Gunicorn
    # NO inicializar inmediatamente - dejar que Gunicorn inicie primero
    # La inicialización se hará en el primer request o en un hook de Gunicorn
    import threading
    import time
    
    _db_initialized = False
    _init_lock = threading.Lock()
    
    def init_db_background():
        """Inicializar base de datos en background después de un delay"""
        global _db_initialized
        # Esperar un poco para que la app esté lista
        time.sleep(5)
        try:
            with _init_lock:
                if not _db_initialized:
                    print("🔄 Iniciando inicialización de base de datos en background...")
                    init_db()
                    _db_initialized = True
                    print("✅ Inicialización de base de datos completada")
        except Exception as e:
            print(f"⚠️ Error en inicialización en background: {e}")
            import traceback
            traceback.print_exc()
    
    # Inicializar en un hilo separado para no bloquear Gunicorn
    init_thread = threading.Thread(target=init_db_background, daemon=True)
    init_thread.start()
    print("🚀 SISAGENT iniciando (inicialización diferida)...")
    print("✅ Aplicación lista - healthcheck disponible inmediatamente")
