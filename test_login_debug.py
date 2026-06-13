#!/usr/bin/env python
import requests

BASE_URL = 'http://localhost:5000'
session = requests.Session()

resp = session.post(BASE_URL + '/login', data={
    'username': 'test_user',
    'password': 'test123'
}, allow_redirects=True)

print(f'Login status: {resp.status_code}')
print(f'Cookies count: {len(session.cookies)}')

resp = session.get(BASE_URL + '/api/operaciones/lista')
print(f'API status: {resp.status_code}')
print(f'Content-Type: {resp.headers.get("content-type")}')

if 'application/json' in resp.headers.get('content-type', ''):
    data = resp.json()
    print(f'Success: {data.get("success")}')
    print(f'Operaciones: {len(data.get("operaciones", []))}')
else:
    print('ERROR: Respuesta no es JSON')
    print(f'Response: {resp.text[:200]}')
