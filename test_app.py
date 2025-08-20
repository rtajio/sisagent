#!/usr/bin/env python3
"""
Test mínimo para verificar que la aplicación funciona
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def root():
    return "TEST - SISAGENT funcionando", 200

@app.route('/ping')
def ping():
    return "pong", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
