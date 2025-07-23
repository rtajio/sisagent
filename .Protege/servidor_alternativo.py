#!/usr/bin/env python3
"""
Servidor alternativo en puerto diferente
"""

import http.server
import socketserver
import sqlite3
import urllib.parse
import os
from http import HTTPStatus

# Configuración del servidor - PUERTO DIFERENTE
PORT = 8080
DIRECTORY = os.getcwd()

# Base de datos simple
DB_FILE = 'alternativo.db'

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

# HTML completamente básico sin CSS complejo
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
        }
        .container {
            background: white;
            padding: 30px;
            border: 1px solid #ccc;
            max-width: 400px;
            margin: 50px auto;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 10px;
            background: #007bff;
            color: white;
            border: none;
            font-size: 16px;
            cursor: pointer;
        }
        .credentials {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
        }
        .status {
            background: #28a745;
            color: white;
            padding: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .error {
            background: #dc3545;
            color: white;
            padding: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SISAGENT</h1>
        
        <div class="status">
            ✅ Servidor Alternativo Puerto 8080
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
            margin-bottom: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            background: white;
            padding: 30px;
            border: 1px solid #ccc;
            text-align: center;
        }
        .success {
            background: #28a745;
            color: white;
            padding: 15px;
            margin-bottom: 20px;
        }
        .logout {
            background: #dc3545;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            display: inline-block;
            margin-top: 20px;
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
            ✅ Login Exitoso - Puerto 8080 Funcionando
        </div>
        
        <div class="card">
            <h2>Login Exitoso</h2>
            <p>Has iniciado sesión correctamente en el sistema SISAGENT.</p>
            <p>El servidor alternativo en puerto 8080 está funcionando.</p>
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
    print("🚀 INICIANDO SERVIDOR ALTERNATIVO")
    print("=" * 40)
    
    # Inicializar base de datos
    init_db()
    print("✅ Base de datos inicializada")
    
    print(f"🌐 Servidor ejecutándose en: http://127.0.0.1:{PORT}")
    print("👤 Credenciales:")
    print("   - Admin: admin / admin123")
    print("   - Usuario: usuario1 / password123")
    print("📝 Características:")
    print("   - Puerto alternativo 8080")
    print("   - HTML completamente básico")
    print("   - Sin JavaScript")
    print("   - CSS simple")
    
    # Crear y ejecutar servidor
    with socketserver.TCPServer(("", PORT), SISAGENTHandler) as httpd:
        print(f"\n🎉 Servidor iniciado en puerto {PORT}")
        print("💡 Presiona Ctrl+C para detener")
        httpd.serve_forever()

if __name__ == '__main__':
    main() 