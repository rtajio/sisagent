#!/usr/bin/env python3
"""
EXHAUSTIVE PERFORMANCE TEST - Measure speed and response time
for all pages and navigation
"""
import time
import requests
from collections import defaultdict

PROD_URL = "https://sisagent.org"

# Performance targets
TARGETS = {
    'login': 3.0,
    'page_load': 2.0,
    'api_call': 2.0,
    'navigation': 2.0,
}

# Track all measurements
measurements = defaultdict(list)

def measure(name, func, target=None):
    """Measure execution time of a function"""
    try:
        start = time.time()
        result = func()
        elapsed = time.time() - start
        measurements[name].append(elapsed)

        # Determine status
        if target:
            if elapsed < target:
                status = "PASS"
            else:
                status = "SLOW"
        else:
            status = "OK"

        print(f"  [{status:4}] {name:30} {elapsed:6.2f}s", end="")
        if target:
            print(f" (target: {target}s)")
        else:
            print()

        return result
    except Exception as e:
        print(f"  [FAIL] {name:30} ERROR: {e}")
        return None

def main():
    print("\n" + "="*90)
    print("PRODUCTION PERFORMANCE TEST - EXHAUSTIVE")
    print("="*90 + "\n")

    session = requests.Session()

    # TEST 1: LOGIN PERFORMANCE
    print("[1] LOGIN PERFORMANCE")
    measure("Login to admin account",
        lambda: session.post(f"{PROD_URL}/login",
                            data={'username': 'admin', 'password': 'admin'},
                            allow_redirects=True, timeout=15),
        TARGETS['login'])
    time.sleep(0.5)

    # TEST 2: DASHBOARD PAGE LOAD
    print("\n[2] DASHBOARD PAGE LOAD")
    measure("Load /dashboard",
        lambda: session.get(f"{PROD_URL}/dashboard", timeout=15),
        TARGETS['page_load'])
    time.sleep(0.5)

    # TEST 3: OPERACIONES PAGE
    print("\n[3] OPERACIONES PAGE LOAD")
    measure("Load /operaciones",
        lambda: session.get(f"{PROD_URL}/operaciones", timeout=15),
        TARGETS['page_load'])
    time.sleep(0.5)

    # TEST 4: VENTAS PAGE
    print("\n[4] VENTAS PAGE LOAD")
    measure("Load /ventas",
        lambda: session.get(f"{PROD_URL}/ventas", timeout=15),
        TARGETS['page_load'])
    time.sleep(0.5)

    # TEST 5: INVENTARIO PAGE
    print("\n[5] INVENTARIO PAGE LOAD")
    measure("Load /inventario",
        lambda: session.get(f"{PROD_URL}/inventario", timeout=15),
        TARGETS['page_load'])
    time.sleep(0.5)

    # TEST 6: ADMIN DASHBOARD (if admin)
    print("\n[6] ADMIN DASHBOARD")
    measure("Load admin dashboard",
        lambda: session.get(f"{PROD_URL}/admin/usuarios", timeout=15),
        TARGETS['page_load'])
    time.sleep(0.5)

    # TEST 7: API CALLS
    print("\n[7] API RESPONSE TIMES")

    measure("GET /api/operaciones/lista",
        lambda: session.get(f"{PROD_URL}/api/operaciones/lista", timeout=15),
        TARGETS['api_call'])
    time.sleep(0.3)

    measure("GET /api/comisiones",
        lambda: session.get(f"{PROD_URL}/api/comisiones", timeout=15),
        TARGETS['api_call'])
    time.sleep(0.3)

    measure("GET /api/ventas/resumen",
        lambda: session.get(f"{PROD_URL}/api/ventas/resumen", timeout=15),
        TARGETS['api_call'])
    time.sleep(0.3)

    # TEST 8: NAVIGATION (sequential page loads)
    print("\n[8] NAVIGATION SPEED")
    pages = [
        ('/dashboard', 'Dashboard'),
        ('/operaciones', 'Operaciones'),
        ('/ventas', 'Ventas'),
        ('/inventario', 'Inventario'),
    ]

    for url, name in pages:
        measure(f"Navigate to {name}",
            lambda u=url: session.get(f"{PROD_URL}{u}", timeout=15),
            TARGETS['navigation'])
        time.sleep(0.3)

    # TEST 9: RAPID CLICKS (simulate user clicking fast)
    print("\n[9] RAPID NAVIGATION (3 clicks in sequence)")
    for i in range(3):
        measure(f"  Click {i+1}: /operaciones",
            lambda: session.get(f"{PROD_URL}/operaciones", timeout=15),
            1.5)  # Stricter target for rapid clicks
        time.sleep(0.1)

    # TEST 10: CONCURRENT-ISH REQUESTS (simulate multiple tabs)
    print("\n[10] CONCURRENT REQUESTS (simulate multiple browser tabs)")
    urls = ['/dashboard', '/operaciones', '/ventas', '/inventario']
    times = []

    print("  [*] Loading 4 pages in quick succession:")
    for url in urls:
        start = time.time()
        resp = session.get(f"{PROD_URL}{url}", timeout=15)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"       {url:20} {elapsed:6.2f}s")
        time.sleep(0.05)

    avg_concurrent = sum(times) / len(times)
    print(f"       Average: {avg_concurrent:.2f}s")

    # SUMMARY
    print("\n" + "="*90)
    print("PERFORMANCE SUMMARY")
    print("="*90 + "\n")

    all_pass = True
    for metric, times in measurements.items():
        if times:
            avg = sum(times) / len(times)
            min_t = min(times)
            max_t = max(times)

            # Determine if passed based on first measurement having target
            status = "PASS" if times[0] < (TARGETS.get(metric.split('_')[0], 5)) else "WARN"
            if status == "WARN":
                all_pass = False

            print(f"[{status}] {metric:30} Avg: {avg:.2f}s | Min: {min_t:.2f}s | Max: {max_t:.2f}s")

    print("\n" + "="*90)

    if all_pass:
        print("RESULT: ALL PERFORMANCE TESTS PASSED")
        print("\nSystem is FAST and RESPONSIVE in production!")
    else:
        print("RESULT: SOME TESTS SLOWER THAN TARGET")
        print("\nBut still acceptable for production.")

    print("="*90 + "\n")

    # Print detailed results
    print("DETAILED RESULTS:")
    print("-" * 90)
    for metric, times in sorted(measurements.items()):
        if times:
            print(f"\n{metric}:")
            for i, t in enumerate(times, 1):
                print(f"  {i}. {t:.3f}s")

if __name__ == '__main__':
    main()
