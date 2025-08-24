#!/usr/bin/env python3
"""
Script para probar la plantilla de voucher preview
"""

import webbrowser
import os
from flask import Flask, render_template

# Crear una aplicación Flask simple para probar
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-key'

@app.route('/')
def preview():
    """Ruta para mostrar el preview del voucher"""
    return render_template('voucher_preview.html')

if __name__ == '__main__':
    print("🎫 Abriendo preview del voucher...")
    print("📏 Puedes cambiar entre 58mm y 80mm usando los botones")
    print("🖨️ Usa el botón 'Imprimir Voucher' para ver cómo se vería impreso")
    
    # Abrir en el navegador
    webbrowser.open('http://127.0.0.1:5001')
    
    # Ejecutar el servidor
    app.run(host='127.0.0.1', port=5001, debug=True)
