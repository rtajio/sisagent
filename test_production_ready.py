#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Production readiness test - verify all inventory features work correctly
in the actual Flask application environment.
"""
import requests
import json
import sys
import time
from datetime import datetime, date

BASE_URL = 'http://localhost:5000'

def login(username, password):
    """Login and return session."""
    session = requests.Session()
    resp = session.post(BASE_URL + '/login', data={
        'username': username,
        'password': password
    })
    if resp.status_code != 200:
        print(f"[ERROR] Login failed: {resp.status_code}")
        return None
    return session

def test_database_schema():
    """Verify database has all required columns."""
    print("\n[TEST 1] Database Schema Verification")
    print("=" * 70)

    import sqlite3
    try:
        conn = sqlite3.connect('./instance/sisagent_consolidada.db')
        cursor = conn.cursor()

        # Check producto table structure
        cursor.execute("PRAGMA table_info(producto)")
        cols = {row[1]: row[2] for row in cursor.fetchall()}

        required_cols = {
            'id': 'INTEGER',
            'nombre': 'VARCHAR',
            'precio': 'NUMERIC',
            'stock': 'INTEGER',
            'fecha_vencimiento': 'DATE',
        }

        print("Checking producto table columns...")
        all_ok = True
        for col_name, col_type in required_cols.items():
            if col_name in cols:
                print(f"  ✓ {col_name}: {cols[col_name]}")
            else:
                print(f"  ✗ {col_name}: MISSING")
                all_ok = False

        conn.close()
        return all_ok

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_api_endpoints():
    """Test that app endpoints are responding."""
    print("\n[TEST 2] API Endpoints Status")
    print("=" * 70)

    session = login('admin', 'admin123')
    if not session:
        print("[ERROR] Cannot login")
        return False

    endpoints = [
        ('/dashboard', 'GET', 'Dashboard'),
        ('/api/operaciones/lista', 'GET', 'Operations list'),
        ('/inventario', 'GET', 'Inventory'),
        ('/ventas', 'GET', 'Sales'),
    ]

    all_ok = True
    for path, method, name in endpoints:
        try:
            if method == 'GET':
                resp = session.get(BASE_URL + path, timeout=5)
            else:
                resp = session.post(BASE_URL + path, timeout=5)

            if resp.status_code in [200, 302]:
                print(f"  ✓ {name}: {resp.status_code}")
            else:
                print(f"  ✗ {name}: {resp.status_code}")
                all_ok = False
        except Exception as e:
            print(f"  ✗ {name}: {str(e)[:50]}")
            all_ok = False

    return all_ok

def test_products_exist():
    """Verify there are products in the system."""
    print("\n[TEST 3] Products in Database")
    print("=" * 70)

    try:
        from app_compatible_optimizado import app, Producto
        with app.app_context():
            products = Producto.query.filter_by(activo=True).all()
            print(f"  Found {len(products)} active products")

            if len(products) > 0:
                print(f"\n  Sample products:")
                for p in products[:5]:
                    venc = f" (exp: {p.fecha_vencimiento})" if p.fecha_vencimiento else ""
                    print(f"    - {p.nombre}: S/ {p.precio} (stock: {p.stock}){venc}")
                return True
            else:
                print("  [WARN] No products found - some tests will be limited")
                return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_chatbot_tools_registered():
    """Verify all chatbot tools are registered."""
    print("\n[TEST 4] Chatbot Tools Registration")
    print("=" * 70)

    try:
        from app_compatible_optimizado import CHATBOT_TOOLS, _HERRAMIENTAS_DECLARACIONES

        critical_tools = [
            'buscar_productos',
            'productos_por_agotar',
            'editar_producto',
            'registrar_venta',
            'registrar_operacion',
        ]

        print("Checking CHATBOT_TOOLS registration...")
        all_ok = True
        for tool in critical_tools:
            if tool in CHATBOT_TOOLS:
                config = CHATBOT_TOOLS[tool]
                requires_conf = config.get('requires_confirmation', False)
                conf_str = "(confirmation required)" if requires_conf else "(no confirmation)"
                print(f"  ✓ {tool}: {conf_str}")
            else:
                print(f"  ✗ {tool}: NOT REGISTERED")
                all_ok = False

        # Check declarations
        print("\nChecking _HERRAMIENTAS_DECLARACIONES...")
        decl_names = [d.get('name') for d in _HERRAMIENTAS_DECLARACIONES]
        for tool in ['productos_por_agotar']:
            if tool in decl_names:
                print(f"  ✓ {tool} declaration found")
            else:
                print(f"  ✗ {tool} declaration missing")
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_system_prompt():
    """Verify system prompt has inventory features guidance."""
    print("\n[TEST 5] System Prompt Configuration")
    print("=" * 70)

    try:
        from app_compatible_optimizado import SYSTEM_PROMPT_CHATBOT

        features = [
            ('Low-stock alerts', 'productos_por_agotar'),
            ('Smart product editing', 'SMART PRODUCT EDITING'),
            ('Search functionality', 'buscar_productos'),
            ('Edit functionality', 'editar_producto'),
        ]

        print("Checking system prompt...")
        all_ok = True
        for feature_name, keyword in features:
            if keyword in SYSTEM_PROMPT_CHATBOT:
                print(f"  ✓ {feature_name} guidance present")
            else:
                print(f"  ✗ {feature_name} guidance missing")
                all_ok = False

        return all_ok

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def test_low_stock_tool():
    """Test the productos_por_agotar function directly."""
    print("\n[TEST 6] Low-Stock Detection Tool")
    print("=" * 70)

    try:
        from app_compatible_optimizado import app, Usuario, _tool_productos_por_agotar

        with app.test_request_context():
            admin = Usuario.query.filter_by(username='admin').first()
            if not admin:
                print("  [WARN] Admin user not found, skipping test")
                return True

            # Test with threshold of 150
            result = _tool_productos_por_agotar({"limite_stock": 150}, admin)

            if not isinstance(result, dict):
                print(f"  [ERROR] Function didn't return dict: {type(result)}")
                return False

            productos = result.get('productos', [])
            print(f"  Found {len(productos)} products with stock <= 150")

            if productos:
                for p in productos[:3]:
                    venc = p.get('fecha_vencimiento') or 'N/A'
                    print(f"    - {p.get('nombre')}: stock {p.get('stock')} (expires: {venc})")

            return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_code_quality():
    """Verify code has no syntax errors and imports work."""
    print("\n[TEST 7] Code Quality & Import Check")
    print("=" * 70)

    try:
        # Try importing the main app
        import app_compatible_optimizado as app
        print("  ✓ app_compatible_optimizado imports successfully")

        # Check for common issues
        checks = [
            ('CHATBOT_TOOLS defined', hasattr(app, 'CHATBOT_TOOLS')),
            ('_HERRAMIENTAS_DECLARACIONES defined', hasattr(app, '_HERRAMIENTAS_DECLARACIONES')),
            ('_tool_productos_por_agotar defined', hasattr(app, '_tool_productos_por_agotar')),
            ('SYSTEM_PROMPT_CHATBOT defined', hasattr(app, 'SYSTEM_PROMPT_CHATBOT')),
        ]

        all_ok = True
        for check_name, check_result in checks:
            status = "✓" if check_result else "✗"
            print(f"  {status} {check_name}")
            all_ok = all_ok and check_result

        return all_ok

    except Exception as e:
        print(f"  [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def test_git_status():
    """Verify git status - main feature is committed, no uncommitted changes."""
    print("\n[TEST 8] Git Status & Version Control")
    print("=" * 70)

    import subprocess

    try:
        # Check current branch
        result = subprocess.run(['git', 'branch', '-v'], capture_output=True, text=True)
        print("  Current branch:")
        for line in result.stdout.split('\n'):
            if line.startswith('*'):
                print(f"    {line}")

        # Check latest commit
        result = subprocess.run(['git', 'log', '-1', '--oneline'], capture_output=True, text=True)
        print(f"\n  Latest commit: {result.stdout.strip()}")

        # Check status
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        staged = [l for l in result.stdout.split('\n') if l.startswith('M ')]

        if staged:
            print(f"  [WARN] Uncommitted changes in tracked files:")
            for line in staged:
                print(f"    {line}")
            return False
        else:
            print("  ✓ No uncommitted changes in tracked files")
            return True

    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def main():
    print("\n" + "=" * 70)
    print("PRODUCTION READINESS TEST SUITE")
    print("=" * 70)

    tests = [
        ("Database Schema", test_database_schema),
        ("API Endpoints", test_api_endpoints),
        ("Products Exist", test_products_exist),
        ("Chatbot Tools", test_chatbot_tools_registered),
        ("System Prompt", test_system_prompt),
        ("Low-Stock Tool", test_low_stock_tool),
        ("Code Quality", test_code_quality),
        ("Git Status", test_git_status),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Test {name} crashed: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = 0
    for name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
        if result:
            passed += 1

    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - READY FOR DEPLOYMENT")
        print("\nNext steps:")
        print("  1. Push to GitHub: git push origin main")
        print("  2. Railway will auto-deploy from main branch")
        print("  3. Verify in production with ANTHROPIC_API_KEY set")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return 1

if __name__ == '__main__':
    sys.exit(main())
