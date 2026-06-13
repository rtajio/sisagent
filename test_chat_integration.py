#!/usr/bin/env python
"""Test script to verify chat functionality works without false errors."""
import requests
import json
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:5000"
SESSION = requests.Session()

# Test credentials (estos usuarios deben existir en la BD)
test_user = "test_user"
test_pass = "test123"

def test_login():
    """Test login to get authenticated session."""
    print("[TEST] Intentando login...")

    # Obtener CSRF token del login form
    resp = SESSION.get(f"{BASE_URL}/login")
    if resp.status_code != 200:
        print(f"[ERROR] No se pudo acceder al login: {resp.status_code}")
        return False

    # Hacer login
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
    if "Dashboard" not in resp.text:
        print("[ERROR] No se pudo autenticar")
        return False

    print("[OK] Login exitoso")
    return True

def test_chat_mensaje():
    """Test sending a chat message to register an operation."""
    print("\n[TEST] Enviando mensaje de chat para registrar operación...")

    # Datos del mensaje
    mensaje_data = {
        "mensaje": "registra una operación de 100 soles vía BCP",
        "historial": []
    }

    resp = SESSION.post(
        f"{BASE_URL}/api/chat/mensaje",
        json=mensaje_data,
        headers={"Content-Type": "application/json"}
    )

    if resp.status_code != 200:
        print(f"[ERROR] Chat falló: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
        return False

    response_json = resp.json()
    print(f"[OK] Chat respondió: {json.dumps(response_json, indent=2)[:500]}")

    # Verificar que no hay error
    if response_json.get("success") == False:
        print(f"[ERROR] Chat reportó error: {response_json.get('message')}")
        return False

    return True

def main():
    print("=" * 60)
    print("TEST: Chat Integration - Sin Falsos Errores")
    print("=" * 60)

    if not test_login():
        print("\n[FAIL] Login falló - no se puede continuar")
        return

    if not test_chat_mensaje():
        print("\n[FAIL] Chat test falló")
        return

    print("\n[SUCCESS] Chat funciona sin falsos errores!")

if __name__ == "__main__":
    main()
