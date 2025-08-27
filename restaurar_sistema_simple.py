#!/usr/bin/env python3
"""
Script de Restauración Simple del Sistema
"""

import os
import shutil
import sys
from datetime import datetime

def restaurar_sistema():
    """Restaurar el sistema al estado funcional anterior"""
    
    print("🔄 Iniciando restauración del sistema...")
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        # 1. Restaurar app.py desde el backup
        backup_app = "backup_pre_vouchers_20250824_131706/app.py"
        if os.path.exists(backup_app):
            shutil.copy2(backup_app, "app.py")
            print("✅ app.py restaurado desde backup")
        else:
            print("⚠️ No se encontró app.py en backup, usando versión básica")
            # Crear app.py básico
            app_basico = '''#!/usr/bin/env python3
"""
SISAGENT - Sistema de Gestión de Operaciones
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///sisagent.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelos
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    es_admin = db.Column(db.Boolean, default=False)

class Sucursal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))

class Operacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    monto = db.Column(db.Float, nullable=False)
    metodo_pago = db.Column(db.String(50), nullable=False)
    comision = db.Column(db.Float, default=0.0)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    sucursal_id = db.Column(db.Integer, db.ForeignKey('sucursal.id'), nullable=False)
    
    usuario = db.relationship('Usuario', backref='operaciones')
    sucursal = db.relationship('Sucursal', backref='operaciones')

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Rutas básicas
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('user_dashboard.html')

@app.route('/operaciones')
@login_required
def operaciones():
    operaciones_list = Operacion.query.all()
    return render_template('operaciones.html', operaciones=operaciones_list)

# Healthcheck para Railway
@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/health')
def health():
    return "OK", 200

@app.route('/railway-health')
def railway_health():
    return "OK", 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
'''
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(app_basico)
            print("✅ app.py básico creado")
        
        # 2. Restaurar requirements.txt básico
        requirements_basico = '''Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
gunicorn==21.2.0
psycopg2-binary==2.9.7
pytz==2023.3'''
        
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements_basico)
        print("✅ requirements.txt restaurado")
        
        # 3. Restaurar Procfile básico
        procfile_basico = '''web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120'''
        
        with open('Procfile', 'w', encoding='utf-8') as f:
            f.write(procfile_basico)
        print("✅ Procfile restaurado")
        
        # 4. Restaurar railway.json básico
        railway_json = '''{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "healthcheckPath": "/ping",
    "healthcheckTimeout": 180,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}'''
        
        with open('railway.json', 'w', encoding='utf-8') as f:
            f.write(railway_json)
        print("✅ railway.json restaurado")
        
        # 5. Eliminar archivos de corrección que pueden causar problemas
        archivos_a_eliminar = [
            'init_db_railway.py',
            'verificar_estructura_db.py',
            'verificar_deploy_vouchers.py',
            'start.sh',
            'wsgi.py',
            'railway.toml'
        ]
        
        for archivo in archivos_a_eliminar:
            if os.path.exists(archivo):
                os.remove(archivo)
                print(f"🗑️ {archivo} eliminado")
        
        print("\n✅ Restauración completada exitosamente")
        print("🔄 El sistema ha sido restaurado al estado funcional básico")
        print("📋 Próximos pasos:")
        print("   1. Hacer commit y push de los cambios")
        print("   2. Railway detectará los cambios automáticamente")
        print("   3. El sistema estará funcional")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la restauración: {e}")
        return False

if __name__ == '__main__':
    restaurar_sistema()
