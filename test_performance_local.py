#!/usr/bin/env python3
"""
Local performance testing - diagnose where the lag is
"""
import time
import requests
import json

def test_server_startup():
    """Check if server is responding"""
    for i in range(10):
        try:
            resp = requests.get('http://localhost:5000/login', timeout=5)
            if resp.status_code in [200, 302]:
                print("[OK] Server is up")
                return True
        except:
            print(f"[WAIT] Server starting... ({i}/10)")
            time.sleep(1)
    print("[FAIL] Server not responding")
    return False

def test_page_load_time(url, description):
    """Measure page load time"""
    try:
        start = time.time()
        resp = requests.get(url, timeout=30)
        elapsed = time.time() - start

        status = "[OK]" if elapsed < 2 else "[SLOW]" if elapsed < 5 else "[VERY SLOW]"
        print(f"{status} {description}: {elapsed:.2f}s")
        return elapsed
    except Exception as e:
        print(f"[ERROR] {description}: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("LOCAL PERFORMANCE DIAGNOSTIC")
    print("="*60 + "\n")

    # Check server
    if not test_server_startup():
        print("\n[FAIL] Cannot connect to server. Is it running?")
        print("Start with: python app_compatible_optimizado.py")
        return 1

    time.sleep(1)

    # Login first
    print("\n[TEST] Logging in...")
    try:
        session = requests.Session()
        resp = session.post('http://localhost:5000/login', data={
            'username': 'admin',
            'password': 'admin'
        }, allow_redirects=True, timeout=10)
        print(f"[OK] Login completed")
    except Exception as e:
        print(f"[ERROR] Login failed: {e}")
        return 1

    # Test page loads
    print("\n[TEST] Page load times:")
    tests = [
        ('http://localhost:5000/dashboard', 'Dashboard'),
        ('http://localhost:5000/operaciones', 'Operaciones'),
        ('http://localhost:5000/ventas', 'Ventas'),
        ('http://localhost:5000/inventario', 'Inventario'),
    ]

    times = []
    for url, desc in tests:
        elapsed = test_page_load_time(url, desc)
        if elapsed:
            times.append(elapsed)
        time.sleep(0.5)

    # Test API calls
    print("\n[TEST] API response times:")
    apis = [
        ('http://localhost:5000/api/operaciones/lista', 'Operaciones API'),
        ('http://localhost:5000/api/comisiones', 'Comisiones API'),
    ]

    for url, desc in apis:
        try:
            start = time.time()
            resp = session.get(url, timeout=10)
            elapsed = time.time() - start

            status = "[OK]" if elapsed < 0.5 else "[SLOW]" if elapsed < 2 else "[VERY SLOW]"
            print(f"{status} {desc}: {elapsed:.3f}s ({resp.status_code})")
        except Exception as e:
            print(f"[ERROR] {desc}: {e}")
        time.sleep(0.5)

    # Summary
    print("\n" + "="*60)
    if times:
        avg = sum(times) / len(times)
        max_time = max(times)
        if avg < 1:
            print("[DIAGNOSIS] Pages load FAST (< 1s average)")
        elif avg < 3:
            print("[DIAGNOSIS] Pages load SLOWLY (1-3s average)")
        else:
            print("[DIAGNOSIS] Pages load VERY SLOWLY (> 3s average)")
        print(f"Average: {avg:.2f}s, Max: {max_time:.2f}s")
    print("="*60 + "\n")

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
