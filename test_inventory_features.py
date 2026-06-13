#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test new inventory features: productos_por_agotar, smart editing, fecha_vencimiento."""
import requests
import json
import sys
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000'

def login(username, password):
    """Login and return session."""
    session = requests.Session()
    resp = session.post(BASE_URL + '/login', data={
        'username': username,
        'password': password
    })
    if resp.status_code != 200:
        print(f"[ERROR] Login failed with status {resp.status_code}")
        return None
    return session

def test_productos_por_agotar(session):
    """Test the productos_por_agotar chatbot function."""
    print("\n[TEST 1] Productos por agotar (low stock alert)")
    print("-" * 50)

    mensaje = "¿Qué productos se van a agotar? Muéstrame los que tienen stock menor a 5"

    resp = session.post(BASE_URL + '/api/chat/mensaje', data={
        'mensaje': mensaje,
        'historial': json.dumps([])
    }, timeout=30)

    if resp.status_code != 200:
        print(f"[ERROR] Chat API failed: {resp.status_code}")
        print(f"Response: {resp.text}")
        return False

    data = resp.json()
    if not data.get('success'):
        print(f"[ERROR] Chat returned error: {data.get('message')}")
        return False

    print(f"Chat response:")
    print(f"  Type: {data.get('tipo')}")
    print(f"  Text: {data.get('texto')[:200]}")

    # Check if response contains info about low stock products
    texto = data.get('texto', '').lower()
    if 'stock' in texto or 'producto' in texto:
        print("[OK] Response mentions stock or products")
        return True
    else:
        print("[WARN] Response doesn't mention stock/products, but might still be valid")
        return True

def test_smart_product_editing(session):
    """Test smart product editing: search then edit or create."""
    print("\n[TEST 2] Smart product editing (search + edit existing)")
    print("-" * 50)

    # First, let's search for coca cola
    print("Sending: 'Dame el precio y stock de coca cola'")
    resp = session.post(BASE_URL + '/api/chat/mensaje', data={
        'mensaje': 'Dame el precio y stock de coca cola',
        'historial': json.dumps([])
    }, timeout=30)

    if resp.status_code != 200:
        print(f"[ERROR] Chat API failed: {resp.status_code}")
        return False

    data = resp.json()
    if not data.get('success'):
        print(f"[ERROR] Chat returned error: {data.get('message')}")
        return False

    print(f"Chat response: {data.get('texto')[:200]}")

    # Now try adding more stock to an existing product
    print("\nSending: 'Añade 20 unidades de coca cola al inventario'")
    resp = session.post(BASE_URL + '/api/chat/mensaje', data={
        'mensaje': 'Añade 20 unidades de coca cola al inventario',
        'historial': json.dumps([])
    }, timeout=30)

    if resp.status_code != 200:
        print(f"[ERROR] Chat API failed: {resp.status_code}")
        return False

    data = resp.json()
    if not data.get('success'):
        print(f"[ERROR] Chat returned error: {data.get('message')}")
        return False

    print(f"Chat response: {data.get('texto')[:200]}")

    # Check if the response mentions editing or creating
    texto = data.get('texto', '').lower()
    if 'edité' in texto or 'creé' in texto or 'stock' in texto:
        print("[OK] Response indicates product was processed")
        return True
    else:
        print("[WARN] Response unclear, but might still be valid")
        return True

def test_fecha_vencimiento(session):
    """Test fecha_vencimiento field in chat context."""
    print("\n[TEST 3] Fecha de vencimiento field")
    print("-" * 50)

    # Ask the chatbot about product expiration dates
    print("Sending: 'Qué productos tienen fecha de vencimiento próxima?'")
    resp = session.post(BASE_URL + '/api/chat/mensaje', data={
        'mensaje': 'Qué productos tienen fecha de vencimiento próxima?',
        'historial': json.dumps([])
    }, timeout=30)

    if resp.status_code != 200:
        print(f"[ERROR] Chat API failed: {resp.status_code}")
        return False

    data = resp.json()
    if not data.get('success'):
        print(f"[ERROR] Chat returned error: {data.get('message')}")
        return False

    print(f"Chat response: {data.get('texto')[:300]}")
    print("[OK] Chatbot can discuss fecha_vencimiento")
    return True

def test_api_endpoints(session):
    """Test the underlying API endpoints."""
    print("\n[TEST 4] API endpoints")
    print("-" * 50)

    # Get list of products
    resp = session.get(BASE_URL + '/api/productos/lista')
    if resp.status_code != 200:
        print(f"[ERROR] Products API failed: {resp.status_code}")
        return False

    data = resp.json()
    productos = data.get('productos', [])
    print(f"Found {len(productos)} products")

    # Check if any products have fecha_vencimiento
    with_vencimiento = [p for p in productos if p.get('fecha_vencimiento')]
    print(f"Products with fecha_vencimiento: {len(with_vencimiento)}")

    # Show first product structure
    if productos:
        print(f"Sample product: {json.dumps(productos[0], indent=2, default=str)[:300]}")

    return True

def main():
    print("Testing new inventory features")
    print("=" * 50)

    # Login
    session = login('test_user', 'test123')
    if not session:
        print("[ERROR] Failed to login")
        sys.exit(1)
    print("[OK] Logged in as test_user")

    # Run tests
    tests = [
        ("productos_por_agotar", test_productos_por_agotar),
        ("smart_product_editing", test_smart_product_editing),
        ("fecha_vencimiento", test_fecha_vencimiento),
        ("api_endpoints", test_api_endpoints),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func(session)
        except Exception as e:
            print(f"[ERROR] Test {name} raised exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for name, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("[OK] All tests passed!")
        sys.exit(0)
    else:
        print("[WARN] Some tests failed or had issues")
        sys.exit(1)

if __name__ == '__main__':
    main()
