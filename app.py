#!/usr/bin/env python3
"""
SISAGENT - Sistema de Gestión de Operaciones Bancarias
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pytz

print("🚀 SISAGENT Flask arrancando...")

# Configuración de la aplicación Flask
app = Flask(__name__)

print("✅ Flask app creada")

# Configuración para Railway
if os.environ.get('DATABASE_URL'):
    # Para Railway con PostgreSQL
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Usando PostgreSQL en Railway: {database_url[:20]}...")
else:
    # Para desarrollo local y Railway sin DATABASE_URL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent_consolidada.db'
    print("✅ Usando SQLite para desarrollo local")

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("✅ Configuración de base de datos completada")

# Configurar CORS para permitir peticiones desde cualquier origen en producción
from flask_cors import CORS
CORS(app, origins=['*'])

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

print("✅ SQLAlchemy y LoginManager configurados")

# Configuración de zona horaria (UTC-5 para Perú)
peru_tz = pytz.timezone('America/Lima')

print("✅ Configuración de zona horaria completada")

# Medios de pago se obtienen dinámicamente de la base de datos

# Modelos de base de datos
class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    activa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    usuarios = db.relationship('Usuario', backref='sucursal', lazy=True)
    operaciones = db.relationship('Operacion', backref='sucursal', lazy=True)

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    operaciones = db.relationship('Operacion', backref='usuario', lazy=True)
    
    
class Operacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    comision = db.Column(db.Numeric(10, 2), nullable=False)
    medio = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.DateTime, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComisionDiaria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    total_comision = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComisionMensual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    total_comision = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MedioPago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_abreviado = db.Column(db.String(20), unique=True, nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    orden = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MedioSucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    medio_pago_id = db.Column(db.Integer, db.ForeignKey('medio_pago.id'), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    sucursal = db.relationship('Sucursal', backref='medios_sucursal')
    medio_pago = db.relationship('MedioPago', backref='sucursales_medio')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Health check endpoint para Railway
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'SISAGENT is running'}), 200

# Rutas de autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password) and user.activo:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales inválidas o usuario inactivo', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas principales
@app.route('/')
@login_required
def dashboard():
    if current_user.es_admin:
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    hoy = datetime.now(peru_tz).date()
    mes_actual = hoy.month
    año_actual = hoy.year

    # Optimizar consultas con una sola query por sucursal
    sucursales = Sucursal.query.filter_by(activa=True).all()
    comisiones_hoy = []
    comisiones_mes = {}
    
    # Obtener todas las comisiones diarias en una sola consulta
    comisiones_diarias = db.session.query(
        ComisionDiaria.sucursal_id,
        db.func.sum(ComisionDiaria.total_comision).label('total')
    ).filter(
        ComisionDiaria.fecha == hoy
    ).group_by(ComisionDiaria.sucursal_id).all()
    
    # Obtener todas las comisiones mensuales en una sola consulta
    comisiones_mensuales = db.session.query(
        Operacion.sucursal_id,
        db.func.sum(Operacion.comision).label('total')
    ).filter(
        db.extract('month', Operacion.hora) == mes_actual,
        db.extract('year', Operacion.hora) == año_actual
    ).group_by(Operacion.sucursal_id).all()
    
    # Crear diccionarios para acceso rápido
    comisiones_diarias_dict = {cd.sucursal_id: float(cd.total) for cd in comisiones_diarias}
    comisiones_mensuales_dict = {cm.sucursal_id: float(cm.total) for cm in comisiones_mensuales}
    
    for suc in sucursales:
        total_hoy = comisiones_diarias_dict.get(suc.id, 0.0)
        total_mes = comisiones_mensuales_dict.get(suc.id, 0.0)
        comisiones_hoy.append((suc.id, suc.nombre, total_hoy))
        comisiones_mes[suc.id] = total_mes
    total_sucursales = len(sucursales)
    total_usuarios = Usuario.query.filter_by(activo=True).count()
    return render_template('admin_dashboard.html',
        total_sucursales=total_sucursales,
        total_usuarios=total_usuarios,
        comisiones_hoy=comisiones_hoy,
        comisiones_mes=comisiones_mes
    )

@app.route('/user')
@login_required
def user_dashboard():
    if current_user.es_admin:
        return redirect(url_for('admin_dashboard'))
    
    hoy = datetime.now(peru_tz).date()
    # Calcular la comisión diaria SOLO de las operaciones del usuario actual
    total_comision_hoy = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0)).filter(
        Operacion.usuario_id == current_user.id,
        db.func.date(Operacion.hora) == hoy
    ).scalar() or 0
    
    operaciones_hoy = Operacion.query.filter_by(
        usuario_id=current_user.id
    ).filter(
        db.func.date(Operacion.hora) == hoy
    ).order_by(Operacion.hora.desc()).limit(10).all()
    
    return render_template('user_dashboard.html',
                         total_comision_hoy=total_comision_hoy,
                         operaciones_hoy=operaciones_hoy)

# Gestión de sucursales (solo admin)
@app.route('/admin/sucursales')
@login_required
def admin_sucursales():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    sucursales = Sucursal.query.all()
    return render_template('admin_sucursales.html', sucursales=sucursales)

@app.route('/admin/sucursales/crear', methods=['GET', 'POST'])
@login_required
def crear_sucursal():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medios = MedioPago.query.order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        sucursal = Sucursal(nombre=nombre, direccion=direccion)
        db.session.add(sucursal)
        db.session.commit()
        # Asociar medios seleccionados
        medios_ids = request.form.getlist('medios')
        for medio_id in medios_ids:
            ms = MedioSucursal(sucursal_id=sucursal.id, medio_pago_id=int(medio_id), activo=True)
            db.session.add(ms)
        db.session.commit()
        flash('Sucursal agregada exitosamente', 'success')
        return redirect(url_for('admin_sucursales'))
    return render_template('crear_sucursal.html', medios=medios)

@app.route('/admin/sucursales/<int:sucursal_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_sucursal(sucursal_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    sucursal = Sucursal.query.get_or_404(sucursal_id)
    medios = MedioPago.query.order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    medios_activos = {ms.medio_pago_id for ms in sucursal.medios_sucursal if ms.activo}
    if request.method == 'POST':
        sucursal.nombre = request.form['nombre']
        sucursal.direccion = request.form['direccion']
        db.session.commit()
        # Actualizar medios
        nuevos_ids = set(map(int, request.form.getlist('medios')))
        # Desactivar los que ya no están
        for ms in sucursal.medios_sucursal:
            ms.activo = ms.medio_pago_id in nuevos_ids
        # Agregar nuevos
        existentes = {ms.medio_pago_id for ms in sucursal.medios_sucursal}
        for medio_id in nuevos_ids - existentes:
            db.session.add(MedioSucursal(sucursal_id=sucursal.id, medio_pago_id=medio_id, activo=True))
        db.session.commit()
        flash('Sucursal editada exitosamente', 'success')
        return redirect(url_for('admin_sucursales'))
    return render_template('editar_sucursal.html', sucursal=sucursal, medios=medios, medios_activos=medios_activos)

@app.route('/admin/sucursales/<int:sucursal_id>/eliminar', methods=['POST'])
@login_required
def eliminar_sucursal(sucursal_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    sucursal = Sucursal.query.get_or_404(sucursal_id)
    
    # Verificar si hay usuarios asignados a esta sucursal
    if Usuario.query.filter_by(sucursal_id=sucursal_id).first():
        flash('No se puede eliminar una sucursal que tiene usuarios asignados', 'error')
        return redirect(url_for('admin_sucursales'))
    
    # Verificar si hay operaciones en esta sucursal
    if Operacion.query.filter_by(sucursal_id=sucursal_id).first():
        flash('No se puede eliminar una sucursal que tiene operaciones registradas', 'error')
        return redirect(url_for('admin_sucursales'))
    
    db.session.delete(sucursal)
    db.session.commit()
    flash('Sucursal eliminada exitosamente', 'error')
    return redirect(url_for('admin_sucursales'))

# Gestión de usuarios (solo admin)
@app.route('/admin/usuarios')
@login_required
def admin_usuarios():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    usuarios = Usuario.query.all()
    return render_template('admin_usuarios.html', usuarios=usuarios)

@app.route('/admin/usuarios/crear', methods=['GET', 'POST'])
@login_required
def crear_usuario():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        nombre_completo = request.form['nombre_completo']
        sucursal_id = request.form['sucursal_id'] if request.form['sucursal_id'] else None
        es_admin = 'es_admin' in request.form
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return render_template('crear_usuario.html', sucursales=Sucursal.query.all())
        
        nuevo_usuario = Usuario(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            nombre_completo=nombre_completo,
            sucursal_id=sucursal_id,
            es_admin=es_admin
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Usuario agregado exitosamente', 'success')
        return redirect(url_for('admin_usuarios'))
    
    return render_template('crear_usuario.html', sucursales=Sucursal.query.all())

@app.route('/admin/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_usuario(usuario_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if request.method == 'POST':
        usuario.email = request.form['email']
        usuario.nombre_completo = request.form['nombre_completo']
        usuario.sucursal_id = request.form['sucursal_id'] if request.form['sucursal_id'] else None
        usuario.es_admin = 'es_admin' in request.form
        usuario.activo = 'activo' in request.form
        
        # Cambiar contraseña si se proporciona
        if request.form['password']:
            usuario.password_hash = generate_password_hash(request.form['password'])
        
        db.session.commit()
        flash('Usuario modificado exitosamente', 'warning')
        return redirect(url_for('admin_usuarios'))
    
    return render_template('editar_usuario.html', usuario=usuario, sucursales=Sucursal.query.all())

@app.route('/admin/usuarios/<int:usuario_id>/eliminar', methods=['POST'])
@login_required
def eliminar_usuario(usuario_id):
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # No permitir eliminar al admin principal
    if usuario.username == 'admin':
        flash('No se puede eliminar al administrador principal', 'error')
        return redirect(url_for('admin_usuarios'))
    
    # No permitir que un admin se elimine a sí mismo
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propia cuenta', 'error')
        return redirect(url_for('admin_usuarios'))
    
    try:
        # Primero eliminar todas las operaciones asociadas al usuario usando SQL directo
        db.session.execute(db.text("DELETE FROM operacion WHERE usuario_id = :user_id"), 
                          {"user_id": usuario.id})
        
        # Luego eliminar el usuario
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuario eliminado exitosamente junto con todas sus operaciones', 'error')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar usuario: {str(e)}', 'error')
    
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/usuarios/<int:usuario_id>/cambiar-rol', methods=['POST'])
@login_required
def admin_cambiar_rol_usuario(usuario_id):
    if not current_user.es_admin:
        return jsonify({'success': False, 'message': 'Acceso denegado. Solo los administradores pueden cambiar roles.'})
    
    usuario = Usuario.query.get_or_404(usuario_id)
    
    # No permitir cambiar el rol del usuario admin principal
    if usuario.username == 'admin':
        return jsonify({'success': False, 'message': 'No se puede cambiar el rol del usuario administrador principal.'})
    
    # No permitir cambiar su propio rol
    if usuario.id == current_user.id:
        return jsonify({'success': False, 'message': 'No puedes cambiar tu propio rol.'})
    
    data = request.get_json()
    nuevo_rol = data.get('rol')
    
    if nuevo_rol not in ['usuario']:
        return jsonify({'success': False, 'message': 'Rol no válido'})
    
    try:
        usuario.es_admin = False
        db.session.commit()
        return jsonify({'success': True, 'message': f'Usuario convertido a {nuevo_rol} exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error al cambiar el rol del usuario'})

@app.route('/admin/perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil_admin():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        current_user.email = request.form['email']
        current_user.nombre_completo = request.form['nombre_completo']
        
        # Cambiar contraseña si se proporciona
        if request.form['password']:
            current_user.password_hash = generate_password_hash(request.form['password'])
        
        db.session.commit()
        flash('Perfil modificado exitosamente', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('editar_perfil_admin.html', usuario=current_user)

# Operaciones bancarias
@app.route('/operaciones')
@login_required
def operaciones():
    fecha = request.args.get('fecha')
    medio = request.args.get('medio')
    hora_inicio = request.args.get('hora_inicio')
    hora_fin = request.args.get('hora_fin')

    if current_user.es_admin:
        query = Operacion.query
        if request.args.get('sucursal_id'):
            query = query.filter_by(sucursal_id=request.args.get('sucursal_id'))
            # Si se accede desde dashboard admin con sucursal_id, mostrar todas las operaciones sin filtrar por fecha
            fecha = None
    elif False:  # Supervisor eliminado
        
        query = Operacion.query.filter_by(sucursal_id=current_user.sucursal_id)
    else:
        query = Operacion.query.filter(Operacion.usuario_id == current_user.id)

    hoy = datetime.now(peru_tz).date()

    if fecha:
        fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d').date()
        if not current_user.es_admin and fecha_objeto != hoy:
            flash('Solo los administradores pueden consultar operaciones de otros días', 'warning')
            fecha = None
        if fecha:
            query = query.filter(db.func.date(Operacion.hora) == fecha)
    
    # Solo aplicar filtro de fecha si no es admin accediendo desde dashboard con sucursal_id
    if (not fecha and not current_user.es_admin) or (fecha and not (current_user.es_admin and request.args.get('sucursal_id'))):
        query = query.filter(db.func.date(Operacion.hora) == hoy)
    if medio:
        query = query.filter(Operacion.medio == medio)
    if hora_inicio:
        query = query.filter(Operacion.hora >= hora_inicio)
    if hora_fin:
        query = query.filter(Operacion.hora <= hora_fin)

    # Usar left join para incluir operaciones sin sucursal asignada
    operaciones = query.outerjoin(Usuario).outerjoin(Sucursal).order_by(Operacion.hora.desc()).all()
    
    filtros_aplicados = bool(fecha or medio or hora_inicio or hora_fin or (current_user.es_admin and request.args.get('sucursal_id')))
    
    # Calcular comisión del día si se accede desde dashboard admin
    comision_dia = 0.0
    sucursal_nombre = None
    if current_user.es_admin and request.args.get('sucursal_id'):
        sucursal_id = int(request.args.get('sucursal_id'))
        sucursal = Sucursal.query.get(sucursal_id)
        if sucursal:
            sucursal_nombre = sucursal.nombre
            # Calcular comisión del día para esta sucursal
            comision_diaria = ComisionDiaria.query.filter_by(
                fecha=hoy,
                sucursal_id=sucursal_id
            ).first()
            if comision_diaria:
                comision_dia = float(comision_diaria.total_comision)
    

    
    # Medios activos para todos los usuarios
    medios_pago = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    return render_template('operaciones.html',
                         operaciones=operaciones,
                         fecha_actual=fecha or datetime.now(peru_tz).strftime('%Y-%m-%d'),
                         fecha_hoy=datetime.now(peru_tz).strftime('%Y-%m-%d'),
                         filtros_aplicados=filtros_aplicados,
                         sucursales=Sucursal.query.all() if current_user.es_admin else [],
                         medios_pago=medios_pago,
                         comision_dia=comision_dia,
                         sucursal_nombre=sucursal_nombre)

@app.route('/operaciones/registrar', methods=['GET', 'POST'])
@login_required
def registrar_operacion():
    if request.method == 'POST':
        monto = float(request.form['monto'])
        comision = float(request.form['comision'])
        medio = request.form['medio']
        
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
        
        # Obtener hora actual en UTC-5 (Perú)
        hora_actual = datetime.now(peru_tz)
        
        nueva_operacion = Operacion(
            monto=monto,
            comision=comision,
            medio=medio,
            hora=hora_actual,
            usuario_id=current_user.id,
            sucursal_id=sucursal_id
        )
        
        db.session.add(nueva_operacion)
        
        # Actualizar comisión diaria
        fecha_hoy = hora_actual.date()
        comision_diaria = ComisionDiaria.query.filter_by(
            fecha=fecha_hoy,
            sucursal_id=sucursal_id
        ).first()
        
        if comision_diaria:
            comision_diaria.total_comision = float(comision_diaria.total_comision) + float(comision)
        else:
            comision_diaria = ComisionDiaria(
                fecha=fecha_hoy,
                sucursal_id=sucursal_id,
                total_comision=comision
            )
            db.session.add(comision_diaria)
        
        # Actualizar comisión mensual
        año_actual = hora_actual.year
        mes_actual = hora_actual.month
        comision_mensual = ComisionMensual.query.filter_by(
            año=año_actual,
            mes=mes_actual,
            sucursal_id=sucursal_id
        ).first()
        
        if comision_mensual:
            comision_mensual.total_comision = float(comision_mensual.total_comision) + float(comision)
        else:
            comision_mensual = ComisionMensual(
                año=año_actual,
                mes=mes_actual,
                sucursal_id=sucursal_id,
                total_comision=comision
            )
            db.session.add(comision_mensual)
        
        db.session.commit()
        flash('Operación bancaria registrada exitosamente', 'success')
        return redirect(url_for('operaciones'))
    
    # Pasar sucursales solo si es administrador
    sucursales = Sucursal.query.filter_by(activa=True).all() if current_user.es_admin else None
    return render_template('registrar_operacion.html', sucursales=sucursales)

# Editar operación
@app.route('/operaciones/<int:operacion_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_operacion(operacion_id):
    operacion = Operacion.query.get_or_404(operacion_id)
    
    # Verificar permisos
    if not current_user.es_admin and operacion.usuario_id != current_user.id:
        flash('No tienes permisos para editar esta operación', 'error')
        return redirect(url_for('operaciones'))
    
    if request.method == 'POST':
        monto_anterior = float(operacion.comision)
        sucursal_anterior = operacion.sucursal_id
        monto = float(request.form['monto'])
        comision = float(request.form['comision'])
        medio = request.form['medio']
        
        # Determinar la nueva sucursal
        if current_user.es_admin:
            nueva_sucursal_id = int(request.form.get('sucursal_id'))
        else:
            nueva_sucursal_id = operacion.sucursal_id
        
        # Actualizar operación
        operacion.monto = monto
        operacion.comision = comision
        operacion.medio = medio
        operacion.sucursal_id = nueva_sucursal_id
        
        # Actualizar comisiones diarias y mensuales
        fecha_operacion = operacion.hora.date()
        año_operacion = operacion.hora.year
        mes_operacion = operacion.hora.month
        
        # Si cambió la sucursal, actualizar ambas sucursales
        if current_user.es_admin and nueva_sucursal_id != sucursal_anterior:
            # Restar de la sucursal anterior
            comision_diaria_anterior = ComisionDiaria.query.filter_by(
                fecha=fecha_operacion,
                sucursal_id=sucursal_anterior
            ).first()
            
            if comision_diaria_anterior:
                comision_diaria_anterior.total_comision = float(comision_diaria_anterior.total_comision) - float(monto_anterior)
            
            comision_mensual_anterior = ComisionMensual.query.filter_by(
                año=año_operacion,
                mes=mes_operacion,
                sucursal_id=sucursal_anterior
            ).first()
            
            if comision_mensual_anterior:
                comision_mensual_anterior.total_comision = float(comision_mensual_anterior.total_comision) - float(monto_anterior)
            
            # Sumar a la nueva sucursal
            comision_diaria_nueva = ComisionDiaria.query.filter_by(
                fecha=fecha_operacion,
                sucursal_id=nueva_sucursal_id
            ).first()
            
            if comision_diaria_nueva:
                comision_diaria_nueva.total_comision = float(comision_diaria_nueva.total_comision) + float(comision)
            else:
                comision_diaria_nueva = ComisionDiaria(
                    fecha=fecha_operacion,
                    sucursal_id=nueva_sucursal_id,
                    total_comision=comision
                )
                db.session.add(comision_diaria_nueva)
            
            comision_mensual_nueva = ComisionMensual.query.filter_by(
                año=año_operacion,
                mes=mes_operacion,
                sucursal_id=nueva_sucursal_id
            ).first()
            
            if comision_mensual_nueva:
                comision_mensual_nueva.total_comision = float(comision_mensual_nueva.total_comision) + float(comision)
            else:
                comision_mensual_nueva = ComisionMensual(
                    año=año_operacion,
                    mes=mes_operacion,
                    sucursal_id=nueva_sucursal_id,
                    total_comision=comision
                )
                db.session.add(comision_mensual_nueva)
        else:
            # Solo actualizar la sucursal actual
            comision_diaria = ComisionDiaria.query.filter_by(
                fecha=fecha_operacion,
                sucursal_id=operacion.sucursal_id
            ).first()
            
            if comision_diaria:
                comision_diaria.total_comision = float(comision_diaria.total_comision) - float(monto_anterior) + float(comision)
            
            comision_mensual = ComisionMensual.query.filter_by(
                año=año_operacion,
                mes=mes_operacion,
                sucursal_id=operacion.sucursal_id
            ).first()
            
            if comision_mensual:
                comision_mensual.total_comision = float(comision_mensual.total_comision) - float(monto_anterior) + float(comision)
        
        db.session.commit()
        flash('Operación bancaria modificada exitosamente', 'warning')
        return redirect(url_for('operaciones'))
    
    # Pasar sucursales solo si es administrador
    sucursales = Sucursal.query.filter_by(activa=True).all() if current_user.es_admin else None
    # Obtener medios de pago activos
    medios_pago = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    
    # DEBUG TEMPORAL
    print(f"🔍 DEBUG - Función editar_operacion()")
    print(f"🔍 DEBUG - Medios obtenidos: {len(medios_pago)}")
    for medio in medios_pago:
        print(f"🔍 DEBUG - Medio: {medio.nombre_abreviado} (orden: {medio.orden})")
    
    return render_template('editar_operacion.html', operacion=operacion, medios_pago=medios_pago, sucursales=sucursales, version="v4")

# Eliminar operación
@app.route('/operaciones/<int:operacion_id>/eliminar', methods=['POST'])
@login_required
def eliminar_operacion(operacion_id):
    operacion = Operacion.query.get_or_404(operacion_id)
    
    # Verificar permisos
    if not current_user.es_admin and operacion.usuario_id != current_user.id:
        flash('No tienes permisos para eliminar esta operación', 'error')
        return redirect(url_for('operaciones'))
    
    monto_comision = float(operacion.comision)
    fecha_operacion = operacion.hora.date()
    año_operacion = operacion.hora.year
    mes_operacion = operacion.hora.month
    sucursal_id = operacion.sucursal_id
    
    # Eliminar operación
    db.session.delete(operacion)
    
    # Actualizar comisiones diarias y mensuales
    comision_diaria = ComisionDiaria.query.filter_by(
        fecha=fecha_operacion,
        sucursal_id=sucursal_id
    ).first()
    
    if comision_diaria:
        comision_diaria.total_comision = float(comision_diaria.total_comision) - float(monto_comision)
    
    comision_mensual = ComisionMensual.query.filter_by(
        año=año_operacion,
        mes=mes_operacion,
        sucursal_id=sucursal_id
    ).first()
    
    if comision_mensual:
        comision_mensual.total_comision = float(comision_mensual.total_comision) - float(monto_comision)
    
    db.session.commit()
    flash('Operación bancaria eliminada exitosamente', 'error')
    return redirect(url_for('operaciones'))

# API para obtener comisiones (solo admin puede ver comisiones mensuales)
@app.route('/api/comisiones')
@login_required
def api_comisiones():
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
        fecha = request.args.get('fecha', datetime.now(peru_tz).strftime('%Y-%m-%d'))
        comision = ComisionDiaria.query.filter_by(
            fecha=fecha,
            sucursal_id=sucursal_id
        ).first()
        
        return jsonify({
            'fecha': fecha,
            'total_comision': float(comision.total_comision) if comision else 0
        })
    
    elif tipo == 'mensual' and current_user.es_admin:
        año = request.args.get('año', datetime.now(peru_tz).year)
        mes = request.args.get('mes', datetime.now(peru_tz).month)
        
        comision = ComisionMensual.query.filter_by(
            año=año,
            mes=mes,
            sucursal_id=sucursal_id
        ).first()
        
        return jsonify({
            'año': año,
            'mes': mes,
            'total_comision': float(comision.total_comision) if comision else 0
        })
    
    else:
        return jsonify({'error': 'Acceso denegado'}), 403

# Rutas de reportes (solo para administradores)
@app.route('/reportes')
@login_required
def reportes():
    if not current_user.es_admin:
        flash('Acceso denegado. Solo los administradores pueden generar reportes.', 'error')
        return redirect(url_for('dashboard'))
    
    # Obtener medios de pago y sucursales
    medios_pago = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    
    if current_user.es_admin:
        sucursales = Sucursal.query.all()
    else:
        sucursales = [current_user.sucursal] if current_user.sucursal else []
    
    return render_template('reportes.html', sucursales=sucursales, medios_pago=medios_pago)



@app.route('/api/reportes/operaciones')
@login_required
def api_reportes_operaciones():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    sucursal_id = request.args.get('sucursal_id')
    medio = request.args.get('medio')
    query = Operacion.query
    if fecha_inicio:
        query = query.filter(Operacion.hora >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Operacion.hora <= fecha_fin + ' 23:59:59')
    if sucursal_id:
        query = query.filter(Operacion.sucursal_id == sucursal_id)
    if medio:
        query = query.filter(Operacion.medio == medio)
    operaciones = query.order_by(Operacion.hora.desc()).all()
    
    # Preparar datos para el reporte
    datos = []
    for op in operaciones:
        # Obtener el nombre completo del medio
        medio_obj = MedioPago.query.filter_by(nombre_abreviado=op.medio).first()
        medio_nombre = medio_obj.nombre_completo if medio_obj else op.medio
        
        datos.append({
            'id': op.id,
            'fecha': op.hora.strftime('%d/%m/%Y'),
            'hora': op.hora.strftime('%H:%M:%S'),
            'monto': float(op.monto),
            'comision': float(op.comision),
            'medio': medio_nombre,
            'usuario': op.usuario.nombre_completo,
            'sucursal': op.sucursal.nombre if op.sucursal else 'Sin sucursal'
        })
    
    return jsonify({
        'operaciones': datos,
        'total_operaciones': len(datos),
        'total_monto': sum(op['monto'] for op in datos),
        'total_comision': sum(op['comision'] for op in datos)
    })

@app.route('/api/reportes/exportar/<formato>')
@login_required
def exportar_reporte(formato):
    if not current_user.es_admin:
        return 'Acceso denegado: solo administradores pueden exportar reportes.', 403
    
    try:
        # Obtener parámetros de filtro
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        sucursal_id = request.args.get('sucursal_id')
        medio = request.args.get('medio')
        
        # Query base
        query = Operacion.query
        
        # Aplicar filtros
        if fecha_inicio:
            query = query.filter(Operacion.hora >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Operacion.hora <= fecha_fin + ' 23:59:59')
        if sucursal_id:
            query = query.filter(Operacion.sucursal_id == sucursal_id)
        if medio:
            query = query.filter(Operacion.medio == medio)
        
        operaciones = query.order_by(Operacion.hora.desc()).all()
        
        # Función para obtener el nombre completo del medio
        def get_medio_nombre(medio_abreviado):
            medio_obj = MedioPago.query.filter_by(nombre_abreviado=medio_abreviado).first()
            return medio_obj.nombre_completo if medio_obj else medio_abreviado
        
        if formato == 'csv':
            import csv
            from io import StringIO
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['N°', 'Fecha', 'Hora', 'Monto', 'Comisión', 'Medio', 'Usuario', 'Sucursal'])
            for idx, op in enumerate(operaciones, 1):
                writer.writerow([
                    idx,
                    op.hora.strftime('%d/%m/%Y'),
                    op.hora.strftime('%H:%M:%S'),
                    float(op.monto),
                    float(op.comision),
                    get_medio_nombre(op.medio),
                    op.usuario.nombre_completo,
                    op.sucursal.nombre if op.sucursal else 'Sin sucursal'
                ])
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=reporte_operaciones.csv'}
            )
        elif formato == 'xlsx':
            import openpyxl
            from openpyxl import Workbook
            from io import BytesIO
            wb = Workbook()
            ws = wb.active
            ws.title = "Operaciones"
            headers = ['N°', 'Fecha', 'Hora', 'Monto', 'Comisión', 'Medio', 'Usuario', 'Sucursal']
            for col, header in enumerate(headers, 1):
                ws.cell(row=1, column=col, value=header)
            for idx, op in enumerate(operaciones, 1):
                row = idx + 1
                ws.cell(row=row, column=1, value=idx)
                ws.cell(row=row, column=2, value=op.hora.strftime('%d/%m/%Y'))
                ws.cell(row=row, column=3, value=op.hora.strftime('%H:%M:%S'))
                ws.cell(row=row, column=4, value=float(op.monto))
                ws.cell(row=row, column=5, value=float(op.comision))
                ws.cell(row=row, column=6, value=get_medio_nombre(op.medio))
                ws.cell(row=row, column=7, value=op.usuario.nombre_completo)
                ws.cell(row=row, column=8, value=op.sucursal.nombre if op.sucursal else 'Sin sucursal')
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': 'attachment; filename=reporte_operaciones.xlsx'}
            )
        elif formato == 'pdf':
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib import colors
            from io import BytesIO
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            # Texto de prueba para verificar actualización
            elements.append(Paragraph('REPORTE ACTUALIZADO - PRUEBA DE NUMERACIÓN CONSECUTIVA', styles['Title']))
            elements.append(Spacer(1, 12))
            data = [['N°', 'Fecha', 'Hora', 'Monto', 'Comisión', 'Medio', 'Usuario', 'Sucursal']]
            for idx, op in enumerate(operaciones, 1):
                data.append([
                    str(idx),
                    op.hora.strftime('%d/%m/%Y'),
                    op.hora.strftime('%H:%M:%S'),
                    f'S/. {float(op.monto):.2f}',
                    f'S/. {float(op.comision):.2f}',
                    get_medio_nombre(op.medio),
                    op.usuario.nombre_completo,
                    op.sucursal.nombre if op.sucursal else 'Sin sucursal'
                ])
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            doc.build(elements)
            output.seek(0)
            from flask import Response
            return Response(
                output.getvalue(),
                mimetype='application/pdf',
                headers={'Content-Disposition': 'attachment; filename=reporte_operaciones.pdf'}
            )
        else:
            return 'Formato no soportado', 400
    except Exception as e:
        return f'Error al generar reporte: {str(e)}', 500


# API para actualizar operaciones (edición inline)
@app.route('/api/operaciones/<int:operacion_id>', methods=['PUT'])
@login_required
def api_actualizar_operacion(operacion_id):
    try:
        # Obtener la operación
        operacion = Operacion.query.get_or_404(operacion_id)
        
        # Verificar permisos: solo el usuario que creó la operación o admin puede editarla
        if not current_user.es_admin and operacion.usuario_id != current_user.id:
            return jsonify({'success': False, 'message': 'No tienes permisos para editar esta operación'}), 403
        
        # Obtener datos del JSON
        data = request.get_json()
        monto = data.get('monto')
        comision = data.get('comision')
        medio = data.get('medio')
        
        # Validar datos
        if not monto or not comision or not medio:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400
        
        try:
            monto = float(monto)
            comision = float(comision)
        except ValueError:
            return jsonify({'success': False, 'message': 'Monto y comisión deben ser números válidos'}), 400
        
        if monto <= 0:
            return jsonify({'success': False, 'message': 'El monto debe ser mayor a 0'}), 400
        
        if comision < 0:
            return jsonify({'success': False, 'message': 'La comisión no puede ser negativa'}), 400
        
        # Validar medio de pago contra la base de datos
        medio_valido = MedioPago.query.filter_by(nombre_abreviado=medio, activo=True).first()
        if not medio_valido:
            return jsonify({'success': False, 'message': 'Medio de pago no válido'}), 400
        
        # Guardar valores originales para actualizar comisiones
        monto_original = float(operacion.monto)
        comision_original = float(operacion.comision)
        fecha_operacion = operacion.hora.date()
        año_operacion = operacion.hora.year
        mes_operacion = operacion.hora.month
        sucursal_id = operacion.sucursal_id
        
        # Actualizar operación
        operacion.monto = monto
        operacion.comision = comision
        operacion.medio = medio
        
        # Actualizar comisiones diarias
        comision_diaria = ComisionDiaria.query.filter_by(
            fecha=fecha_operacion,
            sucursal_id=sucursal_id
        ).first()
        
        if comision_diaria:
            # Restar comisión original y sumar nueva
            comision_diaria.total_comision = float(comision_diaria.total_comision) - comision_original + comision
        
        # Actualizar comisiones mensuales
        comision_mensual = ComisionMensual.query.filter_by(
            año=año_operacion,
            mes=mes_operacion,
            sucursal_id=sucursal_id
        ).first()
        
        if comision_mensual:
            # Restar comisión original y sumar nueva
            comision_mensual.total_comision = float(comision_mensual.total_comision) - comision_original + comision
        
        db.session.commit()
        
        # No flash aquí para evitar duplicados en AJAX
        response_data = {
            'success': True,
            'message': 'Operación actualizada exitosamente',
            'monto': monto,
            'comision': comision,
            'medio': medio
        }
        
        print(f"✅ Respuesta: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error al actualizar la operación: {str(e)}'}), 500

# API para registrar operación (POST)
@app.route('/api/operaciones', methods=['POST'])
@login_required
def api_registrar_operacion():
    data = request.get_json()
    monto = data.get('monto')
    comision = data.get('comision')
    medio = data.get('medio')
    if not monto or not comision or not medio:
        return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400
    try:
        monto = float(monto)
        comision = float(comision)
    except ValueError:
        return jsonify({'success': False, 'message': 'Monto y comisión deben ser números válidos'}), 400
    if monto <= 0:
        return jsonify({'success': False, 'message': 'El monto debe ser mayor a 0'}), 400
    if comision < 0:
        return jsonify({'success': False, 'message': 'La comisión no puede ser negativa'}), 400
    medios_validos = ['BCP', 'KS', 'IBK', 'BN', 'AQP', 'NIUBIZ', 'CONFIANZA', 'BBVA', 'ICA', 'IZIPAY', 'CULQI', 'BIM', 'Interbank', 'Scotiabank', 'Efectivo', 'Yape', 'Plin']
    if medio not in medios_validos:
        return jsonify({'success': False, 'message': 'Medio de pago no válido'}), 400
    if current_user.es_admin:
        sucursal_id = data.get('sucursal_id')
        if not sucursal_id:
            return jsonify({'success': False, 'message': 'Debe seleccionar una sucursal'}), 400
        sucursal_id = int(sucursal_id)
    else:
        if not current_user.sucursal_id:
            return jsonify({'success': False, 'message': 'Debe tener una sucursal asignada'}), 400
        sucursal_id = current_user.sucursal_id
    hora_actual = datetime.now(peru_tz)
    nueva_operacion = Operacion(
        monto=monto,
        comision=comision,
        medio=medio,
        hora=hora_actual,
        usuario_id=current_user.id,
        sucursal_id=sucursal_id
    )
    db.session.add(nueva_operacion)
    # Actualizar comisión diaria
    fecha_hoy = hora_actual.date()
    comision_diaria = ComisionDiaria.query.filter_by(
        fecha=fecha_hoy,
        sucursal_id=sucursal_id
    ).first()
    if comision_diaria:
        comision_diaria.total_comision = float(comision_diaria.total_comision) + float(comision)
    else:
        comision_diaria = ComisionDiaria(
            fecha=fecha_hoy,
            sucursal_id=sucursal_id,
            total_comision=comision
        )
        db.session.add(comision_diaria)
    # Actualizar comisión mensual
    año_actual = hora_actual.year
    mes_actual = hora_actual.month
    comision_mensual = ComisionMensual.query.filter_by(
        año=año_actual,
        mes=mes_actual,
        sucursal_id=sucursal_id
    ).first()
    if comision_mensual:
        comision_mensual.total_comision = float(comision_mensual.total_comision) + float(comision)
    else:
        comision_mensual = ComisionMensual(
            año=año_actual,
            mes=mes_actual,
            sucursal_id=sucursal_id,
            total_comision=comision
        )
        db.session.add(comision_mensual)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Operación registrada exitosamente'})

# API para eliminar operación (DELETE)
@app.route('/api/operaciones/<int:operacion_id>', methods=['DELETE'])
@login_required
def api_eliminar_operacion(operacion_id):
    operacion = Operacion.query.get_or_404(operacion_id)
    if not current_user.es_admin and operacion.usuario_id != current_user.id:
        return jsonify({'success': False, 'message': 'No tienes permisos para eliminar esta operación'}), 403
    monto_comision = float(operacion.comision)
    fecha_operacion = operacion.hora.date()
    año_operacion = operacion.hora.year
    mes_operacion = operacion.hora.month
    sucursal_id = operacion.sucursal_id
    db.session.delete(operacion)
    # Actualizar comisiones diarias y mensuales
    comision_diaria = ComisionDiaria.query.filter_by(
        fecha=fecha_operacion,
        sucursal_id=sucursal_id
    ).first()
    if comision_diaria:
        comision_diaria.total_comision = float(comision_diaria.total_comision) - float(monto_comision)
    comision_mensual = ComisionMensual.query.filter_by(
        año=año_operacion,
        mes=mes_operacion,
        sucursal_id=sucursal_id
    ).first()
    if comision_mensual:
        comision_mensual.total_comision = float(comision_mensual.total_comision) - float(monto_comision)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Operación eliminada exitosamente'})

@app.route('/admin/medios', methods=['GET', 'POST'])
@login_required
def admin_medios():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        nombre_abreviado = request.form['nombre_abreviado'].strip()
        nombre_completo = request.form['nombre_completo'].strip()
        if nombre_abreviado and nombre_completo:
            if not MedioPago.query.filter_by(nombre_abreviado=nombre_abreviado).first():
                medio = MedioPago(nombre_abreviado=nombre_abreviado, nombre_completo=nombre_completo)
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
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    if request.method == 'POST':
        nombre_abreviado = request.form['nombre_abreviado'].strip()
        nombre_completo = request.form['nombre_completo'].strip()
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
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))
    medio = MedioPago.query.get_or_404(medio_id)
    siguiente = MedioPago.query.filter(MedioPago.orden > medio.orden).order_by(MedioPago.orden.asc()).first()
    if siguiente:
        medio.orden, siguiente.orden = siguiente.orden, medio.orden
        db.session.commit()
    return redirect(url_for('admin_medios'))

@app.route('/admin/sucursales/<int:sucursal_id>/toggle_medio', methods=['POST'])
@login_required
def toggle_medio_sucursal(sucursal_id):
    if not current_user.es_admin:
        return jsonify({'success': False, 'error': 'Acceso denegado'}), 403
    medio_id = int(request.form['medio_id'])
    estado = request.form.get('activo') == 'true'
    ms = MedioSucursal.query.filter_by(sucursal_id=sucursal_id, medio_pago_id=medio_id).first()
    if ms:
        ms.activo = estado
    else:
        ms = MedioSucursal(sucursal_id=sucursal_id, medio_pago_id=medio_id, activo=estado)
        db.session.add(ms)
    db.session.commit()
    return jsonify({'success': True, 'activo': ms.activo})




if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
            # Crear usuario admin por defecto si no existe
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                admin = Usuario(
                    username='admin',
                    email='admin@sisagent.com',
                    password_hash=generate_password_hash('61442159'),
                    nombre_completo='Administrador SISAGENT',
                    es_admin=True,
                    sucursal_id=None  # El admin no tiene sucursal asignada inicialmente
                )
                db.session.add(admin)
                db.session.commit()
    except Exception as e:
        print(f"Error durante la inicialización: {e}")
    
    import os
    port = int(os.environ.get("PORT", 5000))
    # En producción, no usar debug mode
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', debug=debug_mode, use_reloader=False, port=port)

print("🎉 SISAGENT Flask cargado completamente - Listo para producción!") 