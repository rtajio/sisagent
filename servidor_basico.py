#!/usr/bin/env python3
"""
Servidor HTTP básico de Python sin Flask
"""

import http.server
import socketserver
import sqlite3
import urllib.parse
import os
import json
from http import HTTPStatus

# Configuración del servidor
PORT = 5000
DIRECTORY = os.getcwd()

# Base de datos simple
DB_FILE = 'basico.db'

def init_db():
    """Inicializar base de datos"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            es_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    try:
        cursor.execute('INSERT INTO usuarios (username, password, es_admin) VALUES (?, ?, ?)',
                      ('admin', 'admin123', True))
        cursor.execute('INSERT INTO usuarios (username, password, es_admin) VALUES (?, ?, ?)',
                      ('usuario1', 'password123', False))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    
    conn.close()

def check_user(username, password):
    """Verificar credenciales"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM usuarios WHERE username = ? AND password = ?',
                  (username, password))
    user = cursor.fetchone()
    
    conn.close()
    return user

# HTML completamente básico
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
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
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 400px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
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
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
        .credentials {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            border-left: 4px solid #007bff;
        }
        .status {
            background: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        .error {
            background: #dc3545;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SISAGENT</h1>
        
        <div class="status">
            ✅ Servidor HTTP Básico - Sin Flask
        </div>
        
        {error_message}
        
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
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
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
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .success {
            background: #28a745;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .logout {
            background: #dc3545;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin-top: 20px;
        }
        .logout:hover {
            background: #c82333;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>¡Bienvenido a SISAGENT!</h1>
            <p>Usuario: {username} | Tipo: {user_type}</p>
        </div>
        
        <div class="success">
            ✅ Login Exitoso - Servidor HTTP Básico Funcionando
        </div>
        
        <div class="card">
            <h2>Login Exitoso</h2>
            <p>Has iniciado sesión correctamente en el sistema SISAGENT.</p>
            <p>El servidor HTTP básico está funcionando perfectamente.</p>
            <p>No hay JavaScript ni dependencias complejas.</p>
            <a href="/logout" class="logout">Cerrar Sesión</a>
        </div>
    </div>
</body>
</html>
"""

class SISAGENTHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Manejar peticiones GET"""
        if self.path == '/':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = LOGIN_HTML.format(error_message="")
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/dashboard':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Verificar si hay datos de sesión (simulado)
            html = DASHBOARD_HTML.format(
                username="Usuario",
                user_type="Normal"
            )
            self.wfile.write(html.encode('utf-8'))
            
        elif self.path == '/logout':
            self.send_response(HTTPStatus.FOUND)
            self.send_header('Location', '/')
            self.end_headers()
            
        else:
            super().do_GET()
    
    def do_POST(self):
        """Manejar peticiones POST"""
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Parsear datos del formulario
            form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            # Verificar credenciales
            user = check_user(username, password)
            
            if user:
                # Login exitoso
                self.send_response(HTTPStatus.FOUND)
                self.send_header('Location', '/dashboard')
                self.end_headers()
            else:
                # Login fallido
                self.send_response(HTTPStatus.OK)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                error_message = '<div class="error">❌ Credenciales incorrectas</div>'
                html = LOGIN_HTML.format(error_message=error_message)
                self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()

def main():
    """Función principal"""
    print("🚀 INICIANDO SERVIDOR HTTP BÁSICO")
    print("=" * 40)
    
    # Inicializar base de datos
    init_db()
    print("✅ Base de datos inicializada")
    
    print(f"🌐 Servidor ejecutándose en: http://127.0.0.1:{PORT}")
    print("👤 Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("📝 Características:")
    print("   - Servidor HTTP básico de Python")
    print("   - Sin Flask ni dependencias externas")
    print("   - HTML completamente estático")
    print("   - Sin JavaScript")
    
    # Crear y ejecutar servidor
    with socketserver.TCPServer(("", PORT), SISAGENTHandler) as httpd:
        print(f"\n🎉 Servidor iniciado en puerto {PORT}")
        print("💡 Presiona Ctrl+C para detener")
        httpd.serve_forever()

if __name__ == '__main__':
    main() 