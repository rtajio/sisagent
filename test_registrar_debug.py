#!/usr/bin/env python
"""Debug operation registration flow."""
import requests
import time

BASE_URL = 'http://localhost:5000'

# Login
session = requests.Session()
session.post(BASE_URL + '/login', data={
    'username': 'test_user',
    'password': 'test123'
})

# Obtener operaciones antes
resp = session.get(BASE_URL + '/api/operaciones/lista')
ops_before = len(resp.json().get('operaciones', []))
print(f'Operaciones antes: {ops_before}')

# Intentar registrar SIN seguir redirects
print(f'\nRegistrando operación...')
resp = session.post(
    BASE_URL + '/operaciones/registrar',
    data={
        'sucursal_id': '1',
        'monto': '100',
        'comision': '',
        'comision_manual': 'false',
        'motivo_descuento': '',
        'medio': 'BCP',
        'hora_automatica': 'true'
    },
    allow_redirects=False  # No seguir redirects
)

print(f'POST status: {resp.status_code}')
print(f'POST location: {resp.headers.get("Location", "N/A")}')
print(f'POST content-type: {resp.headers.get("content-type")}')

# Si es 302, siguió un redirect
if resp.status_code == 302:
    print('Redirigió, siguiendo...')
    location = resp.headers['Location']
    if not location.startswith('http'):
        location = BASE_URL + location
    resp = session.get(location)
    print(f'Después de redirect status: {resp.status_code}')

# Esperar y verificar
time.sleep(1)
resp = session.get(BASE_URL + '/api/operaciones/lista')
ops_after = len(resp.json().get('operaciones', []))
print(f'\nOperaciones después: {ops_after}')

if ops_after > ops_before:
    print(f'[OK] Se registró la operación')
else:
    print(f'[ERROR] No se registró la operación')
