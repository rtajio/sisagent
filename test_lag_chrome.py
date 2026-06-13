#!/usr/bin/env python3
"""
Test sisagent in Chrome: capture lag, console errors, and DevTools issues
"""
import asyncio
from playwright.async_api import async_playwright
import json
import time

async def test_sisagent_lag():
    async with async_playwright() as p:
        # Launch Chrome (headless=False to see real rendering)
        browser = await p.chromium.launch(headless=False, args=[
            '--enable-logging',
            '--v=1',
        ])

        context = await browser.new_context(
            record_video_dir="./videos/"  # Record video of lag
        )

        page = await context.new_page()

        # Listen to ALL console messages
        console_messages = []
        def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text,
                'args': [str(arg) for arg in msg.args]
            })
            print(f"[CONSOLE {msg.type.upper()}] {msg.text}")

        page.on('console', handle_console)

        # Listen to errors
        errors = []
        def handle_error(error):
            errors.append(str(error))
            print(f"[ERROR] {error}")

        page.on('pageerror', handle_error)

        print("\n" + "="*80)
        print("TEST 1: LOAD LOGIN PAGE")
        print("="*80)

        start = time.time()
        await page.goto('https://sisagent.org/login', wait_until='networkidle', timeout=30000)
        load_time = time.time() - start
        print(f"✓ Login page loaded in {load_time:.2f}s")

        print("\n" + "="*80)
        print("TEST 2: LOGIN AS ADMIN")
        print("="*80)

        # Fill username
        await page.fill('input[type="text"]', 'admin')
        await page.wait_for_timeout(100)

        # Fill password
        await page.fill('input[type="password"]', 'admin')
        await page.wait_for_timeout(100)

        # Click login
        start = time.time()
        await page.click('button:has-text("Iniciar Sesión")')
        await page.wait_for_load_state('networkidle', timeout=30000)
        login_time = time.time() - start
        print(f"✓ Login completed in {login_time:.2f}s")

        print("\n" + "="*80)
        print("TEST 3: NAVIGATE TO OPERACIONES (TABLE PAGE WITH LAG)")
        print("="*80)

        # Go to operaciones
        start = time.time()
        await page.goto('https://sisagent.org/operaciones', wait_until='load', timeout=30000)

        # Wait extra for JS to finish
        await page.wait_for_load_state('networkidle', timeout=30000)
        page_load_time = time.time() - start
        print(f"✓ Operaciones page loaded in {page_load_time:.2f}s")

        # Wait a bit for any JS errors to fire
        await page.wait_for_timeout(2000)

        # Capture screenshot
        await page.screenshot(path='/tmp/operaciones_page.png')
        print("✓ Screenshot saved: /tmp/operaciones_page.png")

        print("\n" + "="*80)
        print("TEST 4: MEASURE SCROLL LAG")
        print("="*80)

        # Scroll down (this triggers the lag)
        print("Scrolling down rapidly...")
        start = time.time()
        for i in range(10):
            await page.evaluate('window.scrollBy(0, 200)')
            await page.wait_for_timeout(50)
        scroll_time = time.time() - start
        print(f"✓ 10 scroll events in {scroll_time:.2f}s")

        # Wait for any errors after scroll
        await page.wait_for_timeout(1000)

        print("\n" + "="*80)
        print("TEST 5: CHECK DEVTOOLS METRICS")
        print("="*80)

        # Get performance metrics
        metrics = await page.evaluate("""() => {
            const perfEntries = performance.getEntriesByType('navigation')[0];
            return {
                'domContentLoaded': perfEntries?.domContentLoadedEventEnd - perfEntries?.domContentLoadedEventStart,
                'loadComplete': perfEntries?.loadEventEnd - perfEntries?.loadEventStart,
                'domInteractive': perfEntries?.domInteractive - perfEntries?.fetchStart,
                'resourceCount': performance.getEntriesByType('resource').length
            };
        }""")

        print(f"DOM Content Loaded: {metrics['domContentLoaded']}ms")
        print(f"Load Complete: {metrics['loadComplete']}ms")
        print(f"DOM Interactive: {metrics['domInteractive']}ms")
        print(f"Resources loaded: {metrics['resourceCount']}")

        print("\n" + "="*80)
        print("TEST 6: CHECK FOR MUTATION OBSERVER SPAM")
        print("="*80)

        # Check how many DOM mutations are happening
        mutation_count = await page.evaluate("""() => {
            let count = 0;
            const observer = new MutationObserver(() => {
                count++;
            });
            observer.observe(document.body, {
                subtree: true,
                childList: true,
                attributes: true,
                characterData: true
            });

            // Simulate scroll and measure mutations
            window.scrollBy(0, 100);

            return new Promise(resolve => {
                setTimeout(() => {
                    observer.disconnect();
                    resolve(count);
                }, 500);
            });
        }""")

        print(f"Mutations in 500ms during scroll: {mutation_count}")
        if mutation_count > 100:
            print("⚠️  WARNING: Excessive mutations detected (possible MutationObserver spam)")

        print("\n" + "="*80)
        print("TEST 7: SCROLL BACK UP (TEST THE FREEZE SCENARIO)")
        print("="*80)

        # Scroll back to top quickly
        print("Scrolling back up rapidly...")
        start = time.time()
        for i in range(10):
            await page.evaluate('window.scrollBy(0, -200)')
            await page.wait_for_timeout(50)
        scroll_up_time = time.time() - start
        print(f"✓ Scroll up in {scroll_up_time:.2f}s")

        await page.wait_for_timeout(1000)

        # Take final screenshot
        await page.screenshot(path='/tmp/operaciones_final.png')
        print("✓ Final screenshot saved: /tmp/operaciones_final.png")

        print("\n" + "="*80)
        print("CONSOLE MESSAGES & ERRORS CAPTURED")
        print("="*80)

        print(f"\nTotal console messages: {len(console_messages)}")
        print(f"Total page errors: {len(errors)}")

        if console_messages:
            print("\n--- CONSOLE MESSAGES ---")
            for msg in console_messages[-20:]:  # Last 20
                print(f"[{msg['type']}] {msg['text']}")

        if errors:
            print("\n--- PAGE ERRORS ---")
            for err in errors[-10:]:  # Last 10
                print(f"ERROR: {err}")

        # Save detailed report
        report = {
            'login_time_s': login_time,
            'page_load_time_s': page_load_time,
            'scroll_time_s': scroll_time,
            'scroll_up_time_s': scroll_up_time,
            'mutations_per_500ms': mutation_count,
            'console_messages': len(console_messages),
            'page_errors': len(errors),
            'performance_metrics': metrics,
            'all_console': console_messages,
            'all_errors': errors
        }

        with open('/tmp/lag_report.json', 'w') as f:
            json.dump(report, f, indent=2)

        print("\n✓ Full report saved to /tmp/lag_report.json")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_sisagent_lag())
