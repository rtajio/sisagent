from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv
from sqlalchemy import extract
from flask_cors import CORS
from flask_compress import Compress
from flask_caching import Cache

load_dotenv()

app = Flask(__name__)

# Configuración optimizada
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'tu-clave-secreta-aqui')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///sisagent.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 10,
    'max_overflow': 20
}

# Configuraciones de caché
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# Configuraciones de compresión
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app, origins=['http://127.0.0.1:5000', 'http://localhost:5000'])
Compress(app)
cache = Cache(app)

# Configuración de zona horaria (UTC-5 para Perú)
peru_tz = pytz.timezone('America/Lima')

# Modelos de base de datos (optimizados)
class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, index=True)
    direccion = db.Column(db.String(200))
    activa = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    usuarios = db.relationship('Usuario', backref='sucursal', lazy='select')
    operaciones = db.relationship('Operacion', backref='sucursal', lazy='select')

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre_completo = db.Column(db.String(100), nullable=False)
    es_admin = db.Column(db.Boolean, default=False, index=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=True, index=True)
    activo = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    operaciones = db.relationship('Operacion', backref='usuario', lazy='select')

class Operacion(db.Model):
    __tablename__ = 'operacion'
    id = db.Column(db.Integer, primary_key=True)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    comision = db.Column(db.Numeric(10, 2), nullable=False)
    medio = db.Column(db.String(20), nullable=False, index=True)
    hora = db.Column(db.DateTime, nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False, index=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComisionDiaria(db.Model):
    __tablename__ = 'comision_diaria'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, index=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False, index=True)
    total_comision = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ComisionMensual(db.Model):
    __tablename__ = 'comision_mensual'
    id = db.Column(db.Integer, primary_key=True)
    año = db.Column(db.Integer, nullable=False, index=True)
    mes = db.Column(db.Integer, nullable=False, index=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False, index=True)
    total_comision = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MedioPago(db.Model):
    __tablename__ = 'medio_pago'
    id = db.Column(db.Integer, primary_key=True)
    nombre_abreviado = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre_completo = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True, index=True)
    orden = db.Column(db.Integer, default=0, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MedioSucursal(db.Model):
    __tablename__ = 'medio_sucursal'
    id = db.Column(db.Integer, primary_key=True)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False, index=True)
    medio_pago_id = db.Column(db.Integer, db.ForeignKey('medio_pago.id'), nullable=False, index=True)
    activo = db.Column(db.Boolean, default=True, index=True)
    sucursal = db.relationship('Sucursal', backref='medios_sucursal')
    medio_pago = db.relationship('MedioPago', backref='sucursales_medio')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas optimizadas con caché
@app.route('/admin')
@login_required
@cache.cached(timeout=60)  # Cache por 1 minuto
def admin_dashboard():
    if not current_user.es_admin:
        flash('Acceso denegado', 'error')
        return redirect(url_for('dashboard'))

    hoy = datetime.now(peru_tz).date()
    mes_actual = hoy.month
    año_actual = hoy.year

    # Consultas optimizadas
    sucursales = Sucursal.query.filter_by(activa=True).all()
    
    # Obtener todas las comisiones en consultas únicas
    comisiones_diarias = db.session.query(
        ComisionDiaria.sucursal_id,
        db.func.sum(ComisionDiaria.total_comision).label('total')
    ).filter(ComisionDiaria.fecha == hoy).group_by(ComisionDiaria.sucursal_id).all()
    
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
    
    comisiones_hoy = []
    comisiones_mes = {}
    
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=5000) 