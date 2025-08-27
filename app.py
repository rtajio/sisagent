#!/usr/bin/env python3
"""
SISAGENT - Adaptado a estructura BD real
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
import os

# Configuración básica
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'vivalavida')

# Configuración de base de datos
if os.environ.get('DATABASE_URL'):
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"✅ Usando PostgreSQL en Railway")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sisagent.db'
    print("✅ Usando SQLite para desarrollo local")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Estabilización de conexión (evita conexiones colgadas en Railway)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 30,
    'pool_size': 5,
    'max_overflow': 10,
}

# Inicializar extensiones
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Utilidad para templates: formatear hora (tolerante a None y strings)
def format_peru_time(value):
    try:
        if not value:
            return "--:--"
        # Si ya es datetime o time
        if hasattr(value, 'strftime'):
            return value.strftime('%H:%M')
        # Si viene como string, intentar parseos comunes
        text = str(value).strip()
        # Formatos posibles: HH:MM:SS, HH:MM
        if len(text) >= 5 and ':' in text:
            return text[:5]
        return text
    except Exception:
        return "--:--"

@app.context_processor
def inject_utils():
    return dict(format_peru_time=format_peru_time)

# Utilidad: detectar columna temporal disponible en Operacion
def get_operacion_datetime_column():
    possible_names = ['hora', 'fecha', 'created_at', 'timestamp', 'fecha_creacion']
    try:
        columns = {c.name: c for c in Operacion.__table__.columns}
        for name in possible_names:
            if name in columns:
                return getattr(Operacion, name)
    except Exception:
        pass
    return None

# Modelo que se adapta a la estructura real de la BD
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Agregar atributos que pueden faltar
    es_admin = db.Column(db.Boolean, default=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    
    # Relaciones
    sucursal = db.relationship('Sucursal', backref='usuarios')
    
    @property
    def nombre_completo(self):
        return self.username
    
    def check_password(self, password):
        # Usar username como contraseña temporal
        return self.username == password

class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class Operacion(db.Model):
    __tablename__ = 'operacion'
    id = db.Column(db.Integer, primary_key=True)
    # Solo usar columnas básicas que seguramente existen
    monto = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, default=0.0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref='operaciones')
    sucursal = db.relationship('Sucursal', backref='operaciones')

@login_manager.user_loader
def load_user(user_id):
    try:
        return Usuario.query.get(int(user_id))
    except:
        return None

# Rutas básicas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            
            if not username or not password:
                flash('Usuario y contraseña son requeridos')
                return render_template('login.html')
            
            user = Usuario.query.filter_by(username=username).first()

            # Acceso de emergencia para administrador (sin columna password en BD)
            if username.lower() == 'admin' and password == ADMIN_PASSWORD:
                if not user:
                    # Crear admin si no existe
                    user = Usuario(username='admin', es_admin=True)
                    try:
                        db.session.add(user)
                        db.session.commit()
                    except Exception:
                        db.session.rollback()
                else:
                    # Asegurar flag de admin
                    try:
                        if not user.es_admin:
                            user.es_admin = True
                            db.session.commit()
                    except Exception:
                        db.session.rollback()
                login_user(user)
                return redirect(url_for('dashboard'))

            # Intentar autenticación con password_hash si existe en la BD (modo retrocompatibilidad)
            if user:
                try:
                    result = db.session.execute(
                        db.text("SELECT password_hash FROM usuario WHERE id = :uid"),
                        {"uid": user.id}
                    ).mappings().first()
                    if result and result.get('password_hash'):
                        if check_password_hash(result['password_hash'], password):
                            login_user(user)
                            return redirect(url_for('dashboard'))
                except Exception:
                    # La columna no existe o no es accesible: continuar con los otros métodos
                    pass
            
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos')
        
        return render_template('login.html')
    except Exception as e:
        print(f"Error en login: {e}")
        return f"Error en login: {str(e)}", 500

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Calcular estadísticas básicas
        total_operaciones = Operacion.query.count()
        total_comision_hoy = 0.0
        total_monto_hoy = 0.0
        
        # Intentar calcular por día y mes si hay columna temporal
        dt_col = get_operacion_datetime_column()
        if dt_col is not None:
            hoy = datetime.utcnow().date()
            operaciones_hoy = Operacion.query.filter(db.func.date(dt_col) == hoy).all()

            # Comisiones por sucursal (hoy)
            comisiones_hoy = db.session.query(
                Operacion.sucursal_id,
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
            ).filter(
                db.func.date(dt_col) == hoy
            ).group_by(Operacion.sucursal_id).all()

            # Comisiones del mes por sucursal
            mes = db.func.extract('month', dt_col)
            año = db.func.extract('year', dt_col)
            ahora = datetime.utcnow()
            comisiones_mes = db.session.query(
                Operacion.sucursal_id,
                db.func.coalesce(db.func.sum(Operacion.comision), 0.0)
            ).filter(
                año == ahora.year,
                mes == ahora.month
            ).group_by(Operacion.sucursal_id).all()
        else:
            # Sin columna temporal, mostrar recientes y totales globales
            operaciones_hoy = Operacion.query.limit(20).all()
            comisiones_hoy = []
            comisiones_mes = []
        
        for op in operaciones_hoy:
            total_comision_hoy += op.comision or 0.0
            total_monto_hoy += op.monto or 0.0
        
        # Preparar listado de sucursales y acumulados de mes si existen
        sucursales_info = []
        try:
            sucursales = db.session.query(Sucursal.id, Sucursal.nombre).all()
        except Exception:
            sucursales = []
        com_mes_dict = {sid: float(total) for sid, total in comisiones_mes} if comisiones_mes else {}
        for sid, nombre in sucursales:
            sucursales_info.append({
                'id': sid,
                'nombre': nombre,
                'acumulado_mes': com_mes_dict.get(sid, 0.0)
            })

        return render_template('user_dashboard.html', 
                             total_operaciones=total_operaciones,
                             total_comision_hoy=total_comision_hoy,
                             total_monto_hoy=total_monto_hoy,
                             operaciones_hoy=operaciones_hoy,
                             sucursales_info=sucursales_info)
    except Exception as e:
        return f"Error en dashboard: {str(e)}", 500

@app.route('/operaciones', methods=['GET', 'POST'])
@login_required
def operaciones():
    try:
        # Si llega un POST desde formularios antiguos, evitar caída
        if request.method == 'POST':
            flash('Registro temporalmente redirigido. Use Operaciones solo para consulta.')
            return redirect(url_for('operaciones'))

        operaciones_list = Operacion.query.limit(200).all()
        return render_template('operaciones.html', operaciones=operaciones_list)
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        return f"Error en operaciones: {str(e)}", 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Healthcheck simple para Railway
@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/test')
def test():
    return "SISAGENT funcionando correctamente", 200

# ---- Aliases/compat para rutas antiguas (evitan 404/crash) ----
@app.route('/reportes', endpoint='reportes')
@login_required
def reportes_alias():
    return redirect(url_for('operaciones'))

@app.route('/user_dashboard')
def user_dashboard_alias():
    return redirect(url_for('dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard_alias():
    return redirect(url_for('dashboard'))

@app.route('/admin_sucursales')
@app.route('/admin_usuarios')
@app.route('/admin_medios')
@app.route('/admin_tareos')
def admin_sections_alias():
    return redirect(url_for('operaciones'))

@app.route('/registrar_operacion', methods=['GET', 'POST'])
def registrar_operacion_alias():
    flash('Ruta antigua redirigida a Operaciones')
    return redirect(url_for('operaciones'))

@app.route('/api/comisiones')
@login_required
def api_comisiones():
    try:
        # Sin fecha, devolver totales globales simples
        total_comision = db.session.query(db.func.coalesce(db.func.sum(Operacion.comision), 0.0)).scalar() or 0.0
        total_monto = db.session.query(db.func.coalesce(db.func.sum(Operacion.monto), 0.0)).scalar() or 0.0
        return jsonify({
            'ok': True,
            'total_comision': float(total_comision),
            'total_monto': float(total_monto)
        })
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/seleccionar_voucher/<int:operacion_id>')
@login_required
def seleccionar_voucher_alias(operacion_id):
    # Alias temporal: redirige a operaciones
    return redirect(url_for('operaciones'))

@app.route('/tareos_usuario')
def tareos_usuario_alias():
    return redirect(url_for('operaciones'))

# ---- Manejadores de error para mayor estabilidad ----
@app.errorhandler(404)
def handle_404(_e):
    return "Ruta no encontrada", 404

@app.errorhandler(500)
def handle_500(_e):
    try:
        db.session.rollback()
    except Exception:
        pass
    return "Error interno del servidor", 500

if __name__ == '__main__':
    try:
        with app.app_context():
            # NO crear tablas - usar las existentes
            print("✅ Usando base de datos existente")
    except Exception as e:
        print(f"⚠️  Error conectando BD: {e}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
