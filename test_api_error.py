#!/usr/bin/env python
import requests

session = requests.Session()
resp = session.post('http://localhost:5000/login', data={
    'username': 'test_user',
    'password': 'test123'
})
print(f'Login: {resp.status_code}')

resp = session.get('http://localhost:5000/api/operaciones/lista')
print(f'API Status: {resp.status_code}')
print(f'Content-Type: {resp.headers.get("content-type")}')

if 'application/json' in resp.headers.get('content-type', ''):
    print(f'JSON Response: {resp.json()}')
else:
    print('HTML Response - looking for error:')
    if 'Traceback' in resp.text or 'Error' in resp.text:
        # Buscar la línea de error
        for line in resp.text.split('\n'):
            if any(x in line for x in ['Error', 'Exception', 'Traceback', 'error']):
                print(line)
    else:
        print(f'First 300 chars: {resp.text[:300]}')
