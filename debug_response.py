#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

session = requests.Session()
session.post('http://localhost:5000/login', data={
    'username': 'test_user',
    'password': 'test123'
})

resp = session.get('http://localhost:5000/api/operaciones/lista')

with open('/tmp/api_response.html', 'w', encoding='utf-8') as f:
    f.write(resp.text)

print(f'Status: {resp.status_code}')
print(f'Content-Type: {resp.headers.get("content-type")}')
print(f'Response length: {len(resp.text)} bytes')

# Check if it's the dashboard or an error
if '<title>' in resp.text:
    start = resp.text.find('<title>') + 7
    end = resp.text.find('</title>')
    title = resp.text[start:end]
    print(f'Page title: {title}')

# Buscar si es una respuesta JSON escondida en HTML
if '{' in resp.text[:500]:
    print('Found JSON in first 500 chars')
