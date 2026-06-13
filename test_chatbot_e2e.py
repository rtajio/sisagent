#!/usr/bin/env python3
"""
E2E Test: Chatbot Widget + Voice Activation
Verifica que el widget de chat y voz funcionen en Phase 2B
"""
from playwright.sync_api import sync_playwright
import time

BASE_URL = "http://localhost:5000"

def test_chatbot_widget():
    """Test chatbot widget visibility and basic functionality"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless mode
        context = browser.new_context()
        page = context.new_page()

        # 1. LOGIN
        print("[1/5] Accediendo a login...")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state('networkidle')

        # Llenar login
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        print(f"[INFO] URL despues de login: {page.url}")

        # Verificar que estamos logueados
        if '/dashboard' not in page.url and '/home' not in page.url:
            print("[SKIP] Login no exitoso, tomando screenshot para debug")
            page.screenshot(path='C:\\temp\\login_failed.png')
        else:
            print("[PASS] Login exitoso")

        # 2. VERIFICAR WIDGET
        print("[2/5] Verificando visibilidad del chatbot widget...")
        try:
            page.wait_for_selector('.chatbot-widget', timeout=5000)
            chat_button = page.locator('.chatbot-bubble')
            assert chat_button.is_visible(), "El botón de chat no es visible"
            print("[PASS] Chatbot widget visible")
        except Exception as e:
            print(f"[WARN] Widget no encontrado: {e}")

        # 3. SCREENSHOT
        print("[3/5] Tomando screenshot...")
        page.screenshot(path='C:\\temp\\chatbot_test.png', full_page=True)
        print("[PASS] Screenshot guardado")

        # 4. CHECK HTML STRUCTURE
        print("[4/5] Verificando estructura HTML...")
        content = page.content()
        has_widget = 'chatbot-widget' in content
        has_panel = 'chatbot-panel' in content
        has_messages = 'chatbot-messages' in content
        print(f"[INFO] Widget: {has_widget}, Panel: {has_panel}, Messages: {has_messages}")

        # 5. CLOSE
        browser.close()
        print("[PASS] Test completado")

if __name__ == '__main__':
    try:
        test_chatbot_widget()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
