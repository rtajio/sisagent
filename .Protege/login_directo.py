#!/usr/bin/env python3
"""
Servidor Flask simple con login directo
"""

from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'tu-clave-secreta-aqui'

# HTML simple para el login
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - SISAGENT</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 400px;
            width: 100%;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 12px;
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        .alert {
            border-radius: 10px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="text-center mb-4">
            <i class="fas fa-university fa-3x text-primary mb-3"></i>
            <h2 class="fw-bold">SISAGENT</h2>
            <p class="text-muted">Inicia sesión para continuar</p>
        </div>
        
        {% if error %}
        <div class="alert alert-danger">
            <i class="fas fa-exclamation-triangle me-2"></i>
            {{ error }}
        </div>
        {% endif %}
        
        <form method="POST">
            <div class="mb-3">
                <label for="username" class="form-label">Usuario</label>
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="fas fa-user"></i>
                    </span>
                    <input type="text" class="form-control" id="username" name="username" required>
                </div>
            </div>
            
            <div class="mb-4">
                <label for="password" class="form-label">Contraseña</label>
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="fas fa-lock"></i>
                    </span>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
            </div>
            
            <button type="submit" class="btn btn-primary w-100 py-2">
                <i class="fas fa-sign-in-alt me-2"></i>
                Iniciar Sesión
            </button>
        </form>
        
        <div class="text-center mt-3">
            <small class="text-muted">
                <strong>Credenciales de prueba:</strong><br>
                Admin: admin / admin123<br>
                Usuario: usuario1 / password123
            </small>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# HTML simple para el dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - SISAGENT</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
        }
        .navbar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .card {
            border: none;
            box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            border-radius: 0.75rem;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-university me-2"></i>
                SISAGENT
            </a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">
                    <i class="fas fa-user me-1"></i>
                    {{ username }}
                </span>
                <a class="nav-link" href="/logout">
                    <i class="fas fa-sign-out-alt me-1"></i>
                    Cerrar Sesión
                </a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-body">
                        <h4 class="card-title">
                            <i class="fas fa-tachometer-alt me-2"></i>
                            Dashboard
                        </h4>
                        <p class="card-text">
                            ¡Bienvenido al sistema SISAGENT!
                        </p>
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle me-2"></i>
                            Has iniciado sesión correctamente como <strong>{{ username }}</strong>
                        </div>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="card bg-primary text-white">
                                    <div class="card-body text-center">
                                        <i class="fas fa-list fa-2x mb-2"></i>
                                        <h5>Operaciones</h5>
                                        <p class="mb-0">Gestionar operaciones</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-success text-white">
                                    <div class="card-body text-center">
                                        <i class="fas fa-plus fa-2x mb-2"></i>
                                        <h5>Nueva Operación</h5>
                                        <p class="mb-0">Registrar operación</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card bg-info text-white">
                                    <div class="card-body text-center">
                                        <i class="fas fa-chart-bar fa-2x mb-2"></i>
                                        <h5>Reportes</h5>
                                        <p class="mb-0">Ver reportes</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

def init_db():
    """Inicializar base de datos simple"""
    conn = sqlite3.connect('simple_sisagent.db')
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            es_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # Verificar si ya hay usuarios
    cursor.execute('SELECT COUNT(*) FROM usuarios')
    if cursor.fetchone()[0] == 0:
        # Crear usuarios de prueba
        admin_hash = generate_password_hash('admin123')
        user_hash = generate_password_hash('password123')
        
        cursor.execute('''
            INSERT INTO usuarios (username, password_hash, nombre_completo, es_admin)
            VALUES (?, ?, ?, ?)
        ''', ('admin', admin_hash, 'Administrador SISAGENT', True))
        
        cursor.execute('''
            INSERT INTO usuarios (username, password_hash, nombre_completo, es_admin)
            VALUES (?, ?, ?, ?)
        ''', ('usuario1', user_hash, 'Usuario Normal', False))
        
        print("✅ Usuarios de prueba creados")
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('simple_sisagent.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM usuarios WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['nombre_completo'] = user[3]
            session['es_admin'] = user[4]
            return redirect(url_for('dashboard'))
        else:
            return render_template_string(LOGIN_HTML, error='Credenciales inválidas')
    
    return render_template_string(LOGIN_HTML)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template_string(DASHBOARD_HTML, username=session['nombre_completo'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("🚀 Iniciando servidor simple...")
    init_db()
    print("✅ Base de datos inicializada")
    print("🌐 Servidor ejecutándose en: http://127.0.0.1:5000")
    print("👤 Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    app.run(debug=True, host='127.0.0.1', port=5000) 