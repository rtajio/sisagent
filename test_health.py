#!/usr/bin/env python3
"""
Script para probar el endpoint /health
"""

from app import app

print("🚀 Probando endpoint /health...")

with app.test_client() as client:
    response = client.get('/health')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.get_json()}")

print("✅ Prueba completada") 