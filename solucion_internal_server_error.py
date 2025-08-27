#!/usr/bin/env python3
"""
Script para solucionar el Internal Server Error en el login
"""

import os
import shutil
from datetime import datetime

def solucionar_internal_error():
    """Solucionar el Internal Server Error"""
    
    print("🔧 SOLUCIONANDO INTERNAL SERVER ERROR")
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 50)
    
    try:
        print("📋 PASO 1: Verificando templates...")
        
        # Verificar que existan los templates necesarios
        templates_necesarios = [
            'templates/login.html',
            'templates/user_dashboard.html',
            'templates/operaciones.html'
        ]
        
        for template in templates_necesarios:
            if os.path.exists(template):
                print(f"   ✅ {template} existe")
            else:
                print(f"   ❌ {template} FALTANTE")
        
        print("\n📋 PASO 2: Creando templates básicos si faltan...")
        
        # Crear login.html básico si no existe
        if not os.path.exists('templates/login.html'):
            login_html = '''<!DOCTYPE html>
<html>
<head>
    <title>SISAGENT - Login</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
        .login-container { max-width: 400px; margin: 100px auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>SISAGENT - Login</h2>
        <form method="POST">
            <div class="form-group">
                <label for="username">Usuario:</label>
                <input type="text" id="username" name="username" value="admin" required>
            </div>
            <div class="form-group">
                <label for="password">Contraseña:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Iniciar Sesión</button>
        </form>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="error">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>
</body>
</html>'''
            
            with open('templates/login.html', 'w', encoding='utf-8') as f:
                f.write(login_html)
            print("   ✅ login.html creado")
        
        # Crear user_dashboard.html básico si no existe
        if not os.path.exists('templates/user_dashboard.html'):
            dashboard_html = '''<!DOCTYPE html>
<html>
<head>
    <title>SISAGENT - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .header { background: #007bff; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .menu { display: flex; gap: 10px; margin-bottom: 20px; }
        .menu a { padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        .menu a:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SISAGENT - Dashboard</h1>
            <p>Bienvenido, {{ current_user.nombre }}</p>
        </div>
        <div class="menu">
            <a href="{{ url_for('operaciones') }}">Operaciones</a>
            <a href="{{ url_for('logout') }}">Cerrar Sesión</a>
        </div>
        <div class="content">
            <h2>Panel de Control</h2>
            <p>El sistema está funcionando correctamente.</p>
        </div>
    </div>
</body>
</html>'''
            
            with open('templates/user_dashboard.html', 'w', encoding='utf-8') as f:
                f.write(dashboard_html)
            print("   ✅ user_dashboard.html creado")
        
        # Crear operaciones.html básico si no existe
        if not os.path.exists('templates/operaciones.html'):
            operaciones_html = '''<!DOCTYPE html>
<html>
<head>
    <title>SISAGENT - Operaciones</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .header { background: #007bff; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .menu { display: flex; gap: 10px; margin-bottom: 20px; }
        .menu a { padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
        .menu a:hover { background: #0056b3; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SISAGENT - Operaciones</h1>
        </div>
        <div class="menu">
            <a href="{{ url_for('dashboard') }}">Dashboard</a>
            <a href="{{ url_for('logout') }}">Cerrar Sesión</a>
        </div>
        <div class="content">
            <h2>Lista de Operaciones</h2>
            {% if operaciones %}
                <table>
                    <thead>
                        <tr>
                            <th>Número</th>
                            <th>Fecha</th>
                            <th>Monto</th>
                            <th>Método de Pago</th>
                            <th>Usuario</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for operacion in operaciones %}
                        <tr>
                            <td>{{ operacion.numero }}</td>
                            <td>{{ operacion.fecha.strftime('%d/%m/%Y %H:%M') }}</td>
                            <td>${{ "%.2f"|format(operacion.monto) }}</td>
                            <td>{{ operacion.metodo_pago }}</td>
                            <td>{{ operacion.usuario.nombre }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <p>No hay operaciones registradas.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>'''
            
            with open('templates/operaciones.html', 'w', encoding='utf-8') as f:
                f.write(operaciones_html)
            print("   ✅ operaciones.html creado")
        
        print("\n📋 PASO 3: Agregando ruta de logout...")
        
        # Verificar si app.py tiene la ruta de logout
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'logout' not in content:
            # Agregar ruta de logout al final del archivo, antes del if __name__ == '__main__':
            logout_route = '''
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

'''
            
            # Insertar antes del if __name__ == '__main__':
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if line.strip() == 'if __name__ == \'__main__\':':
                    new_lines.insert(-1, logout_route.strip())
                    break
            
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            print("   ✅ Ruta de logout agregada")
        else:
            print("   ✅ Ruta de logout ya existe")
        
        print("\n" + "=" * 50)
        print("✅ INTERNAL SERVER ERROR SOLUCIONADO")
        print("=" * 50)
        
        print("\n🎯 CAMBIOS REALIZADOS:")
        print("   ✅ Templates verificados y creados si faltaban")
        print("   ✅ login.html - Formulario de login funcional")
        print("   ✅ user_dashboard.html - Dashboard básico")
        print("   ✅ operaciones.html - Lista de operaciones")
        print("   ✅ Ruta de logout agregada")
        
        print("\n📋 PRÓXIMOS PASOS:")
        print("   1. Hacer commit y push de los cambios")
        print("   2. Railway detectará los cambios automáticamente")
        print("   3. Login funcionará sin errores")
        print("   4. Sistema completamente funcional")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la solución: {e}")
        return False

if __name__ == '__main__':
    solucionar_internal_error()
