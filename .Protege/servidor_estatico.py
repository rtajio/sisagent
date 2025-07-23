#!/usr/bin/env python3
"""
Servidor Flask completamente estático sin JavaScript
"""

from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'clave-secreta-123'

# HTML completamente estático sin JavaScript
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - SISAGENT</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: #667eea;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .login-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            padding: 30px;
            max-width: 400px;
            width: 100%;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header h1 {
            color: #333;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .login-header p {
            color: #666;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #333;
            font-weight: bold;
        }
        
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        
        .login-btn {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .credentials {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        
        .credentials h3 {
            color: #333;
            font-size: 16px;
            margin-bottom: 10px;
        }
        
        .credentials p {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        
        .error {
            background: #ff6b6b;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .status {
            background: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>SISAGENT</h1>
            <p>Sistema de Gestión de Operaciones</p>
        </div>
        
        <div class="status">
            ✅ Página cargada correctamente - Sin JavaScript
        </div>
        
        {% if error %}
        <div class="error">
            {{ error }}
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
            
            <button type="submit" class="login-btn">Iniciar Sesión</button>
        </form>
        
        <div class="credentials">
            <h3>Credenciales de Prueba:</h3>
            <p><strong>Admin:</strong> admin / admin123</p>
            <p><strong>Usuario:</strong> usuario1 / password123</p>
        </div>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - SISAGENT</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }
        
        .header {
            background: #667eea;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .user-info {
            font-size: 16px;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .welcome-card {
            background: white;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .welcome-card h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 15px;
        }
        
        .welcome-card p {
            color: #666;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        
        .logout-btn {
            background: #ff6b6b;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
        }
        
        .success-message {
            background: #28a745;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>¡Bienvenido a SISAGENT!</h1>
        <div class="user-info">
            Usuario: {{ username }} | Tipo: {{ user_type }}
        </div>
    </div>
    
    <div class="container">
        <div class="success-message">
            ✅ Login Exitoso - Página funcionando correctamente
        </div>
        
        <div class="welcome-card">
            <h2>Login Exitoso</h2>
            <p>Has iniciado sesión correctamente en el sistema SISAGENT.</p>
            <p>El servidor está funcionando perfectamente y la página se carga correctamente.</p>
            <p>No hay JavaScript que pueda causar problemas de carga.</p>
            <a href="/logout" class="logout-btn">Cerrar Sesión</a>
        </div>
    </div>
</body>
</html>
"""

def init_db():
    """Inicializar base de datos simple"""
    conn = sqlite3.connect('estatico.db')
    cursor = conn.cursor()
    
    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            es_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # Insertar usuarios de prueba
    try:
        cursor.execute('INSERT INTO usuarios (username, password, es_admin) VALUES (?, ?, ?)',
                      ('admin', 'admin123', True))
        cursor.execute('INSERT INTO usuarios (username, password, es_admin) VALUES (?, ?, ?)',
                      ('usuario1', 'password123', False))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Los usuarios ya existen
    
    conn.close()

def check_user(username, password):
    """Verificar credenciales de usuario"""
    conn = sqlite3.connect('estatico.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?',
                  (username, password))
    user = cursor.fetchone()
    
    conn.close()
    return user

@app.route('/')
def index():
    """Redirigir a login"""
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    error = None
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = check_user(username, password)
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['es_admin'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            error = 'Credenciales incorrectas. Intenta de nuevo.'
    
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_type = "Administrador" if session['es_admin'] else "Usuario"
    
    return render_template_string(DASHBOARD_HTML, 
                                username=session['username'],
                                user_type=user_type)

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("🚀 INICIANDO SERVIDOR ESTÁTICO")
    print("=" * 40)
    
    # Inicializar base de datos
    init_db()
    print("✅ Base de datos inicializada")
    
    print("🌐 Servidor ejecutándose en: http://127.0.0.1:5000")
    print("👤 Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("📝 Características:")
    print("   - Sin JavaScript")
    print("   - CSS simple")
    print("   - HTML estático")
    
    app.run(debug=False, host='127.0.0.1', port=5000) 