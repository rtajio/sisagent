#!/usr/bin/env python
"""Test script to verify operations work on Railway without false errors."""
import requests
import json

BASE_URL = "https://sisagent-production.up.railway.app"
SESSION = requests.Session()

# Test credentials - usar un usuario existente en Railway
test_user = "40619883"
test_pass = "1234"

def test_login():
    """Test login on Railway."""
    print("[TEST] Intentando login en Railway...")

    login_data = {
        "username": test_user,
        "password": test_pass,
        "remember_me": False
    }

    resp = SESSION.post(f"{BASE_URL}/login", data=login_data, allow_redirects=True)
    if resp.status_code != 200:
        print(f"[ERROR] Login falló: {resp.status_code}")
        return False

    # Verificar que estamos logged in navegando a dashboard
    resp = SESSION.get(f"{BASE_URL}/dashboard")
    if "Dashboard" not in resp.text and resp.status_code != 200:
        print("[ERROR] No se pudo autenticar en Railway")
        return False

    print("[OK] Login en Railway exitoso")
    return True

def test_operaciones_list():
    """Test that we can list operations on Railway."""
    print("\n[TEST] Obteniendo lista de operaciones...")

    resp = SESSION.get(f"{BASE_URL}/api/operaciones/lista")
    if resp.status_code != 200:
        print(f"[ERROR] No se pudo obtener lista: {resp.status_code}")
        return False

    try:
        data = resp.json()
        if not data.get("success"):
            print(f"[ERROR] API respondió con error: {data}")
            return False

        operaciones = data.get("operaciones", [])
        print(f"[OK] Obtenidas {len(operaciones)} operaciones")
        return True
    except json.JSONDecodeError:
        print(f"[ERROR] Respuesta no es JSON: {resp.text[:200]}")
        return False

def main():
    print("=" * 60)
    print("TEST: Railway Deployment - Operaciones sin Falsos Errores")
    print("=" * 60)

    if not test_login():
        print("\n[FAIL] Login en Railway falló")
        return

    if not test_operaciones_list():
        print("\n[FAIL] No se pudieron listar operaciones")
        return

    print("\n[SUCCESS] Railway está operacional y las operaciones funcionan!")

if __name__ == "__main__":
    main()
