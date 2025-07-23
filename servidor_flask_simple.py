#!/usr/bin/env python3
"""
Servidor Flask Simple que sirve archivos HTML estáticos
"""

from flask import Flask, render_template_string, request, redirect, url_for, send_file
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración de base de datos SQLite
DATABASE = 'sisagent.db'

def init_db():
    """Inicializar la base de datos"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT NOT NULL,
            es_admin BOOLEAN DEFAULT 0,
            activo BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla de sucursales
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sucursal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT,
            activo BOOLEAN DEFAULT 1
        )
    ''')
    
    # Crear tabla de operaciones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS operacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            monto DECIMAL(10,2) NOT NULL,
            descripcion TEXT,
            usuario_id INTEGER,
            sucursal_id INTEGER,
            fecha_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuario (id),
            FOREIGN KEY (sucursal_id) REFERENCES sucursal (id)
        )
    ''')
    
    # Insertar datos de prueba
    try:
        # Insertar sucursal por defecto
        cursor.execute('INSERT OR IGNORE INTO sucursal (id, nombre, direccion) VALUES (1, "Sucursal Principal", "Dirección Principal")')
        
        # Insertar usuarios de prueba
        cursor.execute('''
            INSERT OR IGNORE INTO usuario (username, email, password_hash, nombre_completo, es_admin, activo)
            VALUES 
            ('admin', 'admin@sisagent.com', 'admin123', 'Administrador SISAGENT', 1, 1),
            ('usuario1', 'usuario1@sisagent.com', 'password123', 'Usuario Prueba', 0, 1)
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Error al insertar datos de prueba: {e}")
    
    conn.close()

# HTML del login
LOGIN_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISAGENT - Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border: 1px solid #ccc;
            max-width: 400px;
            width: 100%;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #007bff;
            color: white;
            border: none;
            font-size: 16px;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        .credentials {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
        }
        .status {
            background: #28a745;
            color: white;
            padding: 10px;
            margin-bottom: 20px;
            text-align: center;
            border-radius: 5px;
        }
        .error {
            background: #dc3545;
            color: white;
            padding: 10px;
            margin-bottom: 20px;
            text-align: center;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SISAGENT</h1>
        
        <div class="status">
            ✅ Servidor Flask Funcionando
        </div>
        
        {% if error %}
        <div class="error">
            ❌ {{ error }}
        </div>
        {% endif %}
        
        <form method="POST" action="/login">
            <div class="form-group">
                <label for="username">Usuario:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit">Iniciar Sesión</button>
        </form>
        
        <div class="credentials">
            <h3>Credenciales de Prueba:</h3>
            <p><strong>Admin:</strong> admin / admin123</p>
            <p><strong>Usuario:</strong> usuario1 / password123</p>
        </div>
    </div>
</body>
</html>
'''

# HTML del dashboard
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SISAGENT - Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            margin: 0;
            padding: 20px;
        }
        .header {
            background: #007bff;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: white;
            padding: 30px;
            border: 1px solid #ccc;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .success {
            background: #28a745;
            color: white;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .logout {
            background: #dc3545;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
            border-radius: 5px;
        }
        .logout:hover {
            background: #c82333;
        }
        .btn {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            border-radius: 5px;
        }
        .btn:hover {
            background: #0056b3;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            text-align: center;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Bienvenido a SISAGENT!</h1>
            <p>Dashboard del Sistema de Gestión de Operaciones</p>
            <p>Usuario: {{ username }} | Rol: {{ 'Administrador' if es_admin else 'Usuario' }}</p>
        </div>
        
        <div class="success">
            ✅ Login Exitoso - Servidor Flask Funcionando
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ total_operaciones }}</div>
                <div>Total Operaciones</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_usuarios }}</div>
                <div>Usuarios Activos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ total_sucursales }}</div>
                <div>Sucursales</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Acciones Rápidas</h2>
            <a href="/operaciones" class="btn">Ver Operaciones</a>
            <a href="/nueva_operacion" class="btn">Nueva Operación</a>
            <a href="/usuarios" class="btn">Gestionar Usuarios</a>
            <a href="/logout" class="logout">Cerrar Sesión</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    """Página principal - Login"""
    return render_template_string(LOGIN_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Procesar login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar credenciales en la base de datos
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuario WHERE username = ? AND password_hash = ? AND activo = 1', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            # Login exitoso
            return redirect(url_for('dashboard', username=username))
        else:
            # Login fallido
            return render_template_string(LOGIN_HTML, error="Credenciales incorrectas")
    
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    username = request.args.get('username', 'Usuario')
    
    # Obtener estadísticas
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM operacion')
    total_operaciones = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM usuario WHERE activo = 1')
    total_usuarios = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sucursal WHERE activo = 1')
    total_sucursales = cursor.fetchone()[0]
    
    # Verificar si es admin
    cursor.execute('SELECT es_admin FROM usuario WHERE username = ?', (username,))
    user_data = cursor.fetchone()
    es_admin = user_data[0] if user_data else False
    
    conn.close()
    
    return render_template_string(DASHBOARD_HTML, 
                                username=username,
                                es_admin=es_admin,
                                total_operaciones=total_operaciones,
                                total_usuarios=total_usuarios,
                                total_sucursales=total_sucursales)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    return redirect(url_for('index'))

@app.route('/operaciones')
def operaciones():
    """Página de operaciones"""
    return "<h1>Página de Operaciones</h1><p>Funcionalidad en desarrollo...</p><a href='/dashboard'>Volver al Dashboard</a>"

@app.route('/nueva_operacion')
def nueva_operacion():
    """Página de nueva operación"""
    return "<h1>Nueva Operación</h1><p>Funcionalidad en desarrollo...</p><a href='/dashboard'>Volver al Dashboard</a>"

@app.route('/usuarios')
def usuarios():
    """Página de usuarios"""
    return "<h1>Gestionar Usuarios</h1><p>Funcionalidad en desarrollo...</p><a href='/dashboard'>Volver al Dashboard</a>"

if __name__ == '__main__':
    print("INICIANDO SERVIDOR FLASK SIMPLE")
    print("=" * 40)
    
    # Inicializar base de datos
    init_db()
    print("Base de datos inicializada")
    
    print("Servidor ejecutandose en: http://127.0.0.1:5000")
    print("Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("Caracteristicas:")
    print("   - Servidor Flask funcional")
    print("   - HTML embebido en Python")
    print("   - Base de datos SQLite")
    print("   - Sin dependencias externas de templates")
    
    app.run(debug=True, host='127.0.0.1', port=5000) 