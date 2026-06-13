#!/usr/bin/env python
"""Test to understand permission issues with operations visibility."""
import requests
import time

BASE_URL = 'http://localhost:5000'

# Login como test_user
session = requests.Session()
session.post(BASE_URL + '/login', data={
    'username': 'test_user',
    'password': 'test123'
})

# Obtener info del usuario logueado
resp = session.get(BASE_URL + '/dashboard')
if 'test_user' in resp.text or 'Test User' in resp.text:
    print('[OK] Logueado como test_user')
else:
    print('[ERROR] No se verificó usuario')

# Obtener lista de operaciones
resp = session.get(BASE_URL + '/api/operaciones/lista')
data = resp.json()

print(f'\nAPI Response:')
print(f'  Success: {data.get("success")}')
print(f'  Operaciones count: {len(data.get("operaciones", []))}')

if data.get("operaciones"):
    print(f'\nPrimeras 3 operaciones:')
    for op in data.get("operaciones", [])[:3]:
        print(f'  - ID {op["id"]}: S/ {op["monto"]} via {op["medio"]} (usuario: {op.get("usuario", "N/A")})')
else:
    print('\nNo hay operaciones visibles para este usuario')

# Intentar crear una operación y ver si aparece
print(f'\nIntentando registrar operación...')
resp = session.post(BASE_URL + '/registrar_operacion', data={
    'monto': '100',
    'comision': '',
    'medio': 'BCP',
    'sucursal_id': '1'
}, allow_redirects=True)

print(f'Registro status: {resp.status_code}')

# Esperar un momento y luego verificar si aparece
time.sleep(1)

resp = session.get(BASE_URL + '/api/operaciones/lista')
data = resp.json()
print(f'\nOperaciones después de registro: {len(data.get("operaciones", []))}')

if data.get("operaciones"):
    print(f'Última operación: ID {data["operaciones"][0]["id"]}, S/ {data["operaciones"][0]["monto"]}')
