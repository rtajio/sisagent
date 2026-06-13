#!/usr/bin/env python3
"""
Test script to verify chatbot accuracy against dashboard data.

Checks if the chatbot correctly identifies which branches have operations today
and matches that against the commission data shown in the dashboard.
"""

import asyncio
import json
from playwright.async_api import async_playwright
from datetime import datetime

BASE_URL = "http://localhost:5000"
TEST_USER = "testuser"
TEST_PASSWORD = "test123"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Step 1: Login
            print("[1] Logging in as testuser...")
            await page.goto(f"{BASE_URL}/login")
            await page.wait_for_load_state("networkidle")

            # Check what inputs are available
            username_input = await page.query_selector('input[name="username"]')
            password_input = await page.query_selector('input[name="password"]')
            print(f"   Username input found: {username_input is not None}")
            print(f"   Password input found: {password_input is not None}")

            if username_input and password_input:
                await page.fill('input[name="username"]', TEST_USER)
                await page.fill('input[name="password"]', TEST_PASSWORD)

                # Try submitting the form
                print("   Submitting form...")
                await page.press('input[name="password"]', 'Enter')

                # Wait for redirect
                await page.wait_for_timeout(2000)

                # Check if still on login page
                try:
                    await page.wait_for_url(lambda url: "/login" not in url, timeout=3000)
                    print("   Successfully redirected from login page")
                except:
                    print("   Still on login page or redirect took too long")

            # Verify we're logged in
            current_url = page.url
            print(f"   Current URL after login: {current_url}")

            # Step 2: Go to dashboard
            print("[2] Navigating to dashboard...")
            await page.goto(f"{BASE_URL}/dashboard")
            await page.wait_for_load_state("networkidle")

            # Step 3: Screenshot dashboard and get commission data
            print("[3] Capturing dashboard commission data...")
            dashboard_screenshot = await page.screenshot(path="/tmp/dashboard.png")

            # Get the commission API data - use context's request to preserve session
            commission_response = await context.request.get(f"{BASE_URL}/api/dashboard_comisiones")
            response_text = await commission_response.text()
            print(f"   API Response status: {commission_response.status}")

            try:
                commission_data = json.loads(response_text)
            except json.JSONDecodeError:
                print("   Failed to parse JSON response")
                print(f"   Response (first 200 chars): {response_text[:200]}")
                commission_data = {}

            if commission_data.get('success'):
                print("\n=== DASHBOARD COMMISSION DATA ===")
                print(f"Timestamp: {commission_data.get('timestamp')}")
                print(f"Total comision hoy: S/ {commission_data.get('total_comision_hoy', 0):.2f}")
                print("\nComisiones por sucursal:")

                branches_with_ops_today = {}
                for sucursal in commission_data.get('comisiones_hoy', []):
                    comision = sucursal['comision_hoy']
                    if comision > 0:
                        print(f"  - {sucursal['nombre']}: S/ {comision:.2f}")
                        branches_with_ops_today[sucursal['nombre']] = comision
                    else:
                        print(f"  - {sucursal['nombre']}: S/ 0.00")

            # Step 4: Open chatbot and ask about operations
            print("\n[4] Opening chatbot...")
            chatbot_toggle = await page.query_selector('#chatbot-toggle')
            if chatbot_toggle:
                await chatbot_toggle.click()
                await page.wait_for_timeout(1000)  # Wait for animation

            # Step 5: Ask about operations by branch
            print("[5] Asking chatbot about operations...")

            # Check if message input exists
            message_input = await page.query_selector('.chatbot-input')
            if message_input:
                print("  → Querying: '¿Qué sucursales tienen operaciones hoy?'")
                await message_input.fill("¿Qué sucursales tienen operaciones hoy?")
                await page.click('.chatbot-send')

                # Wait for response
                await page.wait_for_timeout(3000)

                # Get chatbot response
                responses = await page.query_selector_all('.chatbot-message.bot')
                if responses:
                    last_response = responses[-1]
                    response_text = await last_response.text_content()
                    print(f"  ← Chatbot response: {response_text}")

                    # Analyze response
                    print("\n=== RESPONSE ANALYSIS ===")

                    # Check for specific branches mentioned in user's complaint
                    if "Santa Rosa" in response_text or "Santa rosa" in response_text:
                        print("✓ Chatbot mentions 'Santa Rosa'")
                        if "no" in response_text.lower() and ("opera" in response_text.lower() or "registr" in response_text.lower()):
                            if "Santa Rosa" in branches_with_ops_today:
                                print(f"⚠ CONTRADICTION: Chatbot says Santa Rosa has NO operations, but dashboard shows S/ {branches_with_ops_today['Santa Rosa']:.2f}")
                            else:
                                print("✓ Consistent: Santa Rosa has no operations (dashboard also shows 0)")

                    if "La Unión" in response_text or "la union" in response_text.lower():
                        print("✓ Chatbot mentions 'La Unión'")
                        if "no" in response_text.lower() and ("opera" in response_text.lower() or "registr" in response_text.lower()):
                            if "La Unión" in branches_with_ops_today:
                                print(f"⚠ CONTRADICTION: Chatbot says La Unión has NO operations, but dashboard shows S/ {branches_with_ops_today['La Unión']:.2f}")
                            else:
                                print("✓ Consistent: La Unión has no operations (dashboard also shows 0)")

                # Step 6: Ask for operations list
                print("\n[6] Asking for detailed operations...")
                if message_input:
                    await message_input.fill("Muéstrame las operaciones de hoy")
                    await page.click('.chatbot-send')
                    await page.wait_for_timeout(3000)

                    responses = await page.query_selector_all('.chatbot-message.bot')
                    if responses:
                        last_response = responses[-1]
                        response_text = await last_response.text_content()
                        print(f"Chatbot response: {response_text[:500]}...")

            # Step 7: Check operations table
            print("\n[7] Checking operations table...")
            await page.goto(f"{BASE_URL}/operaciones")
            await page.wait_for_load_state("networkidle")

            # Count rows in table
            rows = await page.query_selector_all('table tbody tr')
            print(f"Operations table shows {len(rows)} operations today")

            if len(rows) > 0:
                print("Operations found (sample):")
                for i, row in enumerate(rows[:3]):
                    cells = await row.query_selector_all('td')
                    if cells:
                        text_content = []
                        for cell in cells[:5]:  # First 5 columns
                            text = await cell.text_content()
                            text_content.append(text.strip())
                        print(f"  Row {i+1}: {', '.join(text_content)}")

            print("\n=== TEST COMPLETE ===")

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
