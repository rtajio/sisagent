#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test registering an operation through the chat interface."""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'

# 1. Login
print("[1] Logging in...")
session = requests.Session()
resp = session.post(BASE_URL + '/login', data={
    'username': 'test_user',
    'password': 'test123'
})
print(f"    Login status: {resp.status_code}")

# 2. Get operations count before
print("\n[2] Getting operations count BEFORE...")
resp = session.get(BASE_URL + '/api/operaciones/lista')
ops_before = len(resp.json().get('operaciones', []))
print(f"    Operations before: {ops_before}")

# 3. Send a message to chat asking to register an operation
print("\n[3] Sending chat message (register operation)...")
mensaje = "Registra una operación de S/ 100 por BCP"

resp = session.post(BASE_URL + '/api/chat/mensaje',
    data={
        'mensaje': mensaje,
        'historial': json.dumps([])
    },
    timeout=30
)

print(f"    Chat response status: {resp.status_code}")
print(f"    Chat response: {resp.json()}")

chat_response = resp.json()

if not chat_response.get('success'):
    print(f"\n[ERROR] Chat returned error: {chat_response.get('message')}")
else:
    print(f"    Response type: {chat_response.get('tipo')}")
    print(f"    Response text: {chat_response.get('texto')}")

    # 4. Check if operation was registered
    time.sleep(1)
    print("\n[4] Getting operations count AFTER...")
    resp = session.get(BASE_URL + '/api/operaciones/lista')
    ops_data = resp.json()
    ops_after = len(ops_data.get('operaciones', []))
    print(f"    Operations after: {ops_after}")

    if ops_after > ops_before:
        print(f"\n[OK] Operation registered! (+{ops_after - ops_before} operation)")
        if ops_data.get('operaciones'):
            latest = ops_data['operaciones'][0]
            print(f"    Latest: ID {latest['id']}, Monto: S/ {latest['monto']}, Medio: {latest['medio']}")
    else:
        print(f"\n[ERROR] Operation was NOT registered")

    # 5. Check if chat reported error
    if 'error' in chat_response.get('texto', '').lower():
        print(f"\n[ERROR] Chat reported an error despite registration!")
    else:
        print(f"\n[OK] Chat reported success")

print("\nTest complete!")
