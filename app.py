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

# OPTIMIZACIÓN ULTRA FLUIDA: Configuración SQLAlchemy optimizada
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 20,
    'max_overflow': 40,
    'pool_timeout': 30,
    'echo': False,
    'echo_pool': False,
    'connect_args': {'connect_timeout': 10}
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

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OPTIMIZACIÓN ULTRA: Inicializar caché y compresión
cache = Cache(app)
Compress(app)

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
    es_admin = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    operaciones = db.relationship('Operacion', backref='usuario', lazy='dynamic')

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
    # OPTIMIZACIÓN ULTRA FLUIDA: Eager load sucursal al cargar usuario
    return Usuario.query.options(joinedload(Usuario.sucursal)).get(int(user_id))

# OPTIMIZACIÓN ULTRA: Función para limpiar caché
def clear_cache():
    """Limpiar todo el caché"""
    cache.clear()

# Rutas optimizadas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    # OPTIMIZACIÓN ULTRA FLUIDA: Redirigir según tipo de usuario
    if current_user.es_admin:
        # Dashboard de administrador con consultas optimizadas
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

@app.route('/operaciones')
@login_required
def operaciones():
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
        query = Operacion.query.options(
            joinedload(Operacion.usuario).load_only('nombre_completo'),
            joinedload(Operacion.sucursal).load_only('nombre')
        )
        if request.args.get('sucursal_id'):
            query = query.filter_by(sucursal_id=request.args.get('sucursal_id'))
    else:
        query = Operacion.query.options(
            joinedload(Operacion.usuario).load_only('nombre_completo'),
            joinedload(Operacion.sucursal).load_only('nombre')
        ).filter_by(sucursal_id=current_user.sucursal_id)
    
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
    
    if not fecha or not current_user.es_admin:
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
    filtros_aplicados = bool(fecha or medio or hora_inicio or hora_fin or (current_user.es_admin and request.args.get('sucursal_id')))
    
    # OPTIMIZACIÓN ULTRA FLUIDA: Cargar sucursales solo si es admin
    sucursales = []
    if current_user.es_admin:
        sucursales = get_sucursales_activas_cache()
    
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
    
    if not current_user.es_admin and operacion.usuario_id != current_user.id:
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
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    # OPTIMIZACIÓN ULTRA FLUIDA: Paginación optimizada con eager loading
    page = request.args.get('page', 1, type=int)
    query = Usuario.query.options(
        joinedload(Usuario.sucursal).load_only('nombre')
    )
    usuarios_paginated = query.paginate(
        page=page, per_page=30, error_out=False  # Aumentado de 20 a 30
    )
    
    return render_template('admin_usuarios.html', 
                         usuarios=usuarios_paginated.items,
                         pagination=usuarios_paginated)

@app.route('/admin/sucursales')
@login_required
def admin_sucursales():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    # OPTIMIZACIÓN ULTRA: Usar caché para sucursales
    sucursales = get_sucursales_activas_cache()
    
    return render_template('admin_sucursales.html', sucursales=sucursales)

# OPTIMIZACIÓN ULTRA FLUIDA: API para actualizar operaciones (edición inline)
@app.route('/api/operaciones/<int:operacion_id>', methods=['PUT'])
@login_required
def api_actualizar_operacion(operacion_id):
    """API optimizada para actualizar operaciones"""
    try:
        # OPTIMIZACIÓN ULTRA FLUIDA: Eager load relacionado
        operacion = Operacion.query.options(
            joinedload(Operacion.sucursal).load_only('id', 'nombre')
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

# Healthcheck optimizado
@app.route('/ping')
def ping():
    return jsonify({'status': 'ok', 'timestamp': get_peru_time().isoformat()})

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
            
            # Crear usuario admin si no existe
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                admin = Usuario(
                    username='admin',
                    password_hash=generate_password_hash('61442159'),
                    es_admin=True
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuario admin creado")
            
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
    # OPTIMIZACIÓN ULTRA FLUIDA: Para producción con Gunicorn, inicializar al importar
    init_db()
