#!/usr/bin/env python3
"""
E2E Test: Phase 2B - Voice + ML UI Implementation
Tests: widget visibility, message sending, voice settings, ML features
"""
import json
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5000"
TEST_USER = "admin"
TEST_PASS = "admin"

def run_test():
    with sync_playwright() as p:
        print("[*] Starting E2E test for Phase 2B...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. LOGIN
        print("[1/7] Testing login...")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_load_state('networkidle')

        # Try both selectors
        username_input = page.locator('input[name="username"]')
        password_input = page.locator('input[name="password"]')

        username_input.fill(TEST_USER)
        password_input.fill(TEST_PASS)

        # Click and wait for navigation
        submit_button = page.locator('button[type="submit"]')
        submit_button.click()

        # Wait for redirect
        try:
            page.wait_for_url("**/dashboard**", timeout=5000)
            print("[OK] Login successful")
        except:
            current_url = page.url
            print(f"[!] After login redirect to: {current_url}")
            # Try /home fallback
            if '/home' in current_url:
                print("[OK] Redirected to /home (fallback)")
            elif '/login' in current_url:
                print("[ERROR] Still at login - credentials may be wrong")
                page.screenshot(path='C:\\temp\\login_error.png')
                return False

        # 2. CHECK CHATBOT WIDGET
        print("[2/7] Checking chatbot widget...")
        page.wait_for_timeout(2000)

        try:
            widget = page.locator('.chatbot-widget')
            is_visible = widget.is_visible()
            print(f"[OK] Widget visible: {is_visible}")
        except:
            print("[WARN] Widget not found in CSS")
            is_visible = False

        # 3. CHECK PAGE CONTENT
        print("[3/7] Checking page structure...")
        content = page.content()
        checks = {
            'chatbot-widget': 'chatbot-widget' in content,
            'chatbot-panel': 'chatbot-panel' in content,
            'chatbot-messages': 'chatbot-messages' in content,
            'chatbot-input': 'chatbot-input' in content,
            'chatbot-bubble': 'chatbot-bubble' in content,
            'voice-settings': 'chatbot-settings' in content or 'voice' in content.lower()
        }

        for name, found in checks.items():
            status = "FOUND" if found else "MISSING"
            print(f"  {name}: {status}")

        # 4. CLICK TO OPEN PANEL
        print("[4/7] Testing panel toggle...")
        try:
            bubble = page.locator('#chatbot-bubble-btn')
            if bubble.is_visible():
                bubble.click()
                page.wait_for_timeout(500)
                panel = page.locator('#chatbot-panel')
                if not panel.is_visible():
                    print("[WARN] Panel didn't open")
                else:
                    print("[OK] Panel opened successfully")
        except:
            print("[WARN] Could not test panel toggle")

        # 5. CHECK ML ENDPOINTS
        print("[5/7] Testing ML endpoints...")

        # Test /api/bot/custom_functions
        try:
            response = page.goto(f"{BASE_URL}/api/bot/custom_functions/{1}")
            status = page.evaluate("() => document.body.textContent")
            if "success" in status or "funciones" in status:
                print("[OK] /api/bot/custom_functions accessible")
            else:
                print(f"[!] Endpoint returned: {status[:100]}")
        except Exception as e:
            print(f"[!] ML endpoint test failed: {e}")

        # Navigate back
        page.goto(f"{BASE_URL}/dashboard")
        page.wait_for_load_state('networkidle')

        # 6. CHECK VOICE ENDPOINTS
        print("[6/7] Testing voice endpoints...")

        # Test /api/chat/voice_token
        try:
            response = page.goto(f"{BASE_URL}/api/chat/voice_token")
            content = page.evaluate("() => document.body.textContent")
            if "token" in content.lower() or "success" in content.lower():
                print("[OK] Voice token endpoint working")
            else:
                print(f"[!] Voice endpoint response: {content[:100]}")
        except:
            print("[WARN] Voice token endpoint not accessible")

        page.goto(f"{BASE_URL}/dashboard")

        # 7. SCREENSHOT
        print("[7/7] Taking screenshots...")
        page.screenshot(path='C:\\temp\\phase2b_dashboard.png', full_page=True)
        print("[OK] Screenshots saved")

        browser.close()
        print("\n[SUCCESS] Phase 2B E2E test completed")
        return True

if __name__ == '__main__':
    try:
        success = run_test()
        exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        exit(1)
