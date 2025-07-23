from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuración de zona horaria (UTC-5 para Perú)
peru_tz = pytz.timezone('America/Lima')

# Medios de pago disponibles
MEDIOS_PAGO = ['BCP', 'KS', 'IBK', 'BN', 'AQP', 'NIUBIZ', 'CONFIANZA', 'BBVA', 'ICA', 'IZIPAY', 'CULQI', 'BIM']

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

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

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
    
    # Estadísticas para admin
    total_sucursales = Sucursal.query.filter_by(activa=True).count()
    total_usuarios = Usuario.query.filter_by(activo=True).count()
    
    # Comisiones del día actual
    hoy = datetime.now(peru_tz).date()
    comisiones_hoy = db.session.query(
        Sucursal.nombre,
        db.func.coalesce(db.func.sum(ComisionDiaria.total_comision), 0).label('total')
    ).outerjoin(ComisionDiaria, 
                (Sucursal.id == ComisionDiaria.sucursal_id) & 
                (ComisionDiaria.fecha == hoy)
    ).group_by(Sucursal.id, Sucursal.nombre).all()
    
    return render_template('admin_dashboard.html', 
                         total_sucursales=total_sucursales,
                         total_usuarios=total_usuarios,
                         comisiones_hoy=comisiones_hoy)

@app.route('/user')
@login_required
def user_dashboard():
    if current_user.es_admin:
        return redirect(url_for('admin_dashboard'))
    
    # Obtener comisión diaria del usuario
    hoy = datetime.now(peru_tz).date()
    comision_diaria = ComisionDiaria.query.filter_by(
        fecha=hoy, 
        sucursal_id=current_user.sucursal_id
    ).first()
    
    total_comision_hoy = comision_diaria.total_comision if comision_diaria else 0
    
    # Operaciones del día
    operaciones_hoy = Operacion.query.filter_by(
        sucursal_id=current_user.sucursal_id
    ).filter(
        db.func.date(Operacion.hora) == hoy
    ).order_by(Operacion.hora.desc()).limit(10).all()
    
    return render_template('user_dashboard.html',
                         total_comision_hoy=total_comision_hoy,
                         operaciones_hoy=operaciones_hoy)

# Gestión de operaciones
@app.route('/operaciones')
@login_required
def operaciones():
    # Obtener parámetros de filtro
    sucursal_id = request.args.get('sucursal_id', type=int)
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    medio = request.args.get('medio')
    
    # Construir query base
    query = Operacion.query
    
    # Aplicar filtros según permisos
    if current_user.es_admin:
        if sucursal_id:
            query = query.filter_by(sucursal_id=sucursal_id)
    else:
        query = query.filter_by(sucursal_id=current_user.sucursal_id)
    
    # Filtros de fecha
    if fecha_inicio:
        query = query.filter(Operacion.hora >= datetime.strptime(fecha_inicio, '%Y-%m-%d'))
    if fecha_fin:
        query = query.filter(Operacion.hora <= datetime.strptime(fecha_fin + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
    
    # Filtro de medio de pago
    if medio:
        query = query.filter_by(medio=medio)
    
    # Ordenar por fecha más reciente
    operaciones = query.order_by(Operacion.hora.desc()).all()
    
    # Obtener sucursales para el filtro (solo admin)
    sucursales = []
    if current_user.es_admin:
        sucursales = Sucursal.query.filter_by(activa=True).all()
    
    return render_template('operaciones.html', 
                         operaciones=operaciones,
                         sucursales=sucursales,
                         medios_pago=MEDIOS_PAGO)

@app.route('/operaciones/registrar', methods=['GET', 'POST'])
@login_required
def registrar_operacion():
    if request.method == 'POST':
        try:
            monto = float(request.form['monto'])
            comision = float(request.form['comision'])
            medio = request.form['medio']
            hora_str = request.form['hora']
            
            # Convertir hora a datetime
            hora = datetime.strptime(hora_str, '%Y-%m-%dT%H:%M')
            
            # Crear operación
            nueva_operacion = Operacion(
                monto=monto,
                comision=comision,
                medio=medio,
                hora=hora,
                usuario_id=current_user.id,
                sucursal_id=current_user.sucursal_id
            )
            
            db.session.add(nueva_operacion)
            
            # Actualizar comisión diaria
            fecha_operacion = hora.date()
            comision_diaria = ComisionDiaria.query.filter_by(
                fecha=fecha_operacion,
                sucursal_id=current_user.sucursal_id
            ).first()
            
            if comision_diaria:
                comision_diaria.total_comision += comision
            else:
                comision_diaria = ComisionDiaria(
                    fecha=fecha_operacion,
                    sucursal_id=current_user.sucursal_id,
                    total_comision=comision
                )
                db.session.add(comision_diaria)
            
            db.session.commit()
            flash('Operación registrada exitosamente', 'success')
            return redirect(url_for('operaciones'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar operación: {str(e)}', 'error')
    
    return render_template('registrar_operacion.html', medios_pago=MEDIOS_PAGO)

@app.route('/operaciones/<int:operacion_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_operacion(operacion_id):
    operacion = Operacion.query.get_or_404(operacion_id)
    
    # Verificar permisos
    if not current_user.es_admin and operacion.usuario_id != current_user.id:
        flash('No tienes permisos para editar esta operación', 'error')
        return redirect(url_for('operaciones'))
    
    if request.method == 'POST':
        try:
            # Obtener comisión anterior para actualizar comisión diaria
            comision_anterior = float(operacion.comision)
            
            # Actualizar operación
            operacion.monto = float(request.form['monto'])
            operacion.comision = float(request.form['comision'])
            operacion.medio = request.form['medio']
            operacion.hora = datetime.strptime(request.form['hora'], '%Y-%m-%dT%H:%M')
            
            # Actualizar comisión diaria
            fecha_operacion = operacion.hora.date()
            comision_diaria = ComisionDiaria.query.filter_by(
                fecha=fecha_operacion,
                sucursal_id=operacion.sucursal_id
            ).first()
            
            if comision_diaria:
                comision_diaria.total_comision = comision_diaria.total_comision - comision_anterior + float(operacion.comision)
            
            db.session.commit()
            flash('Operación actualizada exitosamente', 'success')
            return redirect(url_for('operaciones'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar operación: {str(e)}', 'error')
    
    return render_template('editar_operacion.html', 
                         operacion=operacion,
                         medios_pago=MEDIOS_PAGO)

@app.route('/operaciones/<int:operacion_id>/eliminar', methods=['POST'])
@login_required
def eliminar_operacion(operacion_id):
    operacion = Operacion.query.get_or_404(operacion_id)
    
    # Verificar permisos
    if not current_user.es_admin and operacion.usuario_id != current_user.id:
        flash('No tienes permisos para eliminar esta operación', 'error')
        return redirect(url_for('operaciones'))
    
    try:
        # Actualizar comisión diaria
        comision_diaria = ComisionDiaria.query.filter_by(
            fecha=operacion.hora.date(),
            sucursal_id=operacion.sucursal_id
        ).first()
        
        if comision_diaria:
            comision_diaria.total_comision -= float(operacion.comision)
            if comision_diaria.total_comision <= 0:
                db.session.delete(comision_diaria)
        
        db.session.delete(operacion)
        db.session.commit()
        flash('Operación eliminada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar operación: {str(e)}', 'error')
    
    return redirect(url_for('operaciones'))

# API para obtener comisiones
@app.route('/api/comisiones')
@login_required
def api_comisiones():
    try:
        # Obtener parámetros
        sucursal_id = request.args.get('sucursal_id', type=int)
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        # Construir query
        query = db.session.query(
            Operacion.medio,
            db.func.sum(Operacion.comision).label('total_comision'),
            db.func.count(Operacion.id).label('total_operaciones')
        )
        
        # Aplicar filtros
        if current_user.es_admin:
            if sucursal_id:
                query = query.filter_by(sucursal_id=sucursal_id)
        else:
            query = query.filter_by(sucursal_id=current_user.sucursal_id)
        
        if fecha_inicio:
            query = query.filter(Operacion.hora >= datetime.strptime(fecha_inicio, '%Y-%m-%d'))
        if fecha_fin:
            query = query.filter(Operacion.hora <= datetime.strptime(fecha_fin + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))
        
        # Agrupar por medio de pago
        resultados = query.group_by(Operacion.medio).all()
        
        # Formatear datos
        datos = []
        for medio, total_comision, total_operaciones in resultados:
            datos.append({
                'medio': medio,
                'total_comision': float(total_comision),
                'total_operaciones': total_operaciones
            })
        
        return jsonify({'success': True, 'data': datos})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Inicialización de la base de datos
def init_db():
    with app.app_context():
        db.create_all()
        
        # Crear sucursal por defecto si no existe
        if not Sucursal.query.first():
            sucursal_default = Sucursal(
                nombre="Sucursal Principal",
                direccion="Dirección Principal"
            )
            db.session.add(sucursal_default)
            db.session.commit()
        
        # Crear usuario admin si no existe
        if not Usuario.query.filter_by(username='admin').first():
            admin = Usuario(
                username='admin',
                email='admin@sisagent.com',
                password_hash=generate_password_hash('admin123'),
                nombre_completo='Administrador SISAGENT',
                es_admin=True,
                sucursal_id=1,
                activo=True
            )
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    print("INICIANDO SISAGENT - VERSION RESTAURADA")
    print("=" * 50)
    
    # Inicializar base de datos
    init_db()
    print("Base de datos inicializada")
    
    print("Servidor ejecutandose en: http://127.0.0.1:5000")
    print("Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("Caracteristicas:")
    print("   - Version restaurada y funcional")
    print("   - Base de datos SQLite")
    print("   - Mejoras en UI mantenidas")
    print("   - Notificaciones funcionando")
    
    app.run(debug=True, host='127.0.0.1', port=5000) 