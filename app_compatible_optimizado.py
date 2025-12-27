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
    return Usuario.query.get(int(user_id))

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
            return render_template('admin_dashboard.html', **base_ctx)
        else:
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
    
    # Query base optimizada
    if current_user.es_admin:
        query = Operacion.query
        if request.args.get('sucursal_id'):
            query = query.filter_by(sucursal_id=request.args.get('sucursal_id'))
    else:
        query = Operacion.query.filter_by(sucursal_id=current_user.sucursal_id)
    
    # Obtener fecha actual para comparación
    hoy = datetime.now(peru_tz).date()
    
    # Aplicar filtros
    if fecha:
        fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d').date()
        if not current_user.es_admin and fecha_objeto != hoy:
            flash('Solo los administradores pueden consultar operaciones de otros días', 'warning')
            fecha = None
        
        if fecha:
            query = query.filter(db.func.date(Operacion.hora) == fecha)
    
    if not fecha or not current_user.es_admin:
        query = query.filter(db.func.date(Operacion.hora) == hoy)
    
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
    
    # OPTIMIZACIÓN ULTRA: Cargar sucursales solo si es admin
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
    sucursales = []
    if current_user.es_admin:
        sucursales = get_sucursales_activas_cache()
    
    return render_template('editar_operacion.html', operacion=operacion, sucursales=sucursales)

# Rutas de administración optimizadas
@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    # OPTIMIZACIÓN ULTRA: Paginación para usuarios
    page = request.args.get('page', 1, type=int)
    usuarios_paginated = Usuario.query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin_usuarios.html', 
                         usuarios=usuarios_paginated.items,
                         pagination=usuarios_paginated)

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
    
    # Evitar eager-load sobre relaciones lazy='dynamic'
    sucursales = get_sucursales_activas_cache()
    # Precalcular conteos con len() sobre dynamic (hace count en BD)
    for s in sucursales:
        s._usuarios_count = s.usuarios.count() if hasattr(s, 'usuarios') else 0
        s._operaciones_count = s.operaciones.count() if hasattr(s, 'operaciones') else 0
    
    return render_template('admin_sucursales.html', sucursales=sucursales)

# Healthcheck optimizado
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
            
            # Crear usuario admin si no existe
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                admin = Usuario(
                    username='admin',
                    password_hash=generate_password_hash('admin123'),
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
            # Continuar aunque haya errores menores

if __name__ == '__main__':
    init_db()
    print("🎉 SISAGENT Flask COMPATIBLE ULTRA OPTIMIZADO cargado completamente - Listo para producción!")
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
