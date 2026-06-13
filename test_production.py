#!/usr/bin/env python3
"""
Test production deployment at https://sisagent.up.railway.app
"""
import time
import requests
import json

PROD_URL = "https://sisagent.up.railway.app"

def test_deployment_status():
    """Check if app is deployed and running"""
    print("\n" + "="*80)
    print("PRODUCTION DEPLOYMENT TEST")
    print("="*80 + "\n")

    print("[TEST 1] Is app deployed and responsive?")
    try:
        start = time.time()
        resp = requests.get(f"{PROD_URL}/login", timeout=10)
        elapsed = time.time() - start

        if resp.status_code == 200:
            print(f"[PASS] App is live! ({elapsed:.2f}s)")
            return True
        else:
            print(f"[FAIL] Got status {resp.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("[FAIL] Request timeout (app not responding)")
        return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] Connection error (app not deployed yet?)")
        return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

def test_login_and_performance(session):
    """Test login and measure response time"""
    print("\n[TEST 2] Login performance")
    try:
        start = time.time()
        resp = session.post(f"{PROD_URL}/login", data={
            'username': 'admin',
            'password': 'admin'
        }, allow_redirects=True, timeout=15)
        elapsed = time.time() - start

        if resp.status_code == 200:
            status = "[PASS]" if elapsed < 3 else "[SLOW]"
            print(f"{status} Login: {elapsed:.2f}s (target: <3s)")
            return True
        else:
            print(f"[FAIL] Login returned {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

def test_dashboard(session):
    """Test dashboard load and response time"""
    print("\n[TEST 3] Dashboard performance")
    try:
        start = time.time()
        resp = session.get(f"{PROD_URL}/dashboard", timeout=15)
        elapsed = time.time() - start

        if resp.status_code == 200:
            status = "[PASS]" if elapsed < 2 else "[SLOW]"
            print(f"{status} Dashboard: {elapsed:.2f}s (target: <2s)")
            return True
        else:
            print(f"[FAIL] Dashboard returned {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

def test_api_performance(session):
    """Test API response times"""
    print("\n[TEST 4] API performance")

    apis = [
        ('/api/operaciones/lista', 'Operations'),
        ('/api/comisiones', 'Commissions'),
    ]

    all_pass = True
    for endpoint, name in apis:
        try:
            start = time.time()
            resp = session.get(f"{PROD_URL}{endpoint}", timeout=15)
            elapsed = time.time() - start

            if resp.status_code == 200:
                status = "[OK]" if elapsed < 2 else "[SLOW]"
                print(f"  {status} {name}: {elapsed:.2f}s")
            else:
                print(f"  [FAIL] {name}: {resp.status_code}")
                all_pass = False
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            all_pass = False

    return all_pass

def test_functionality(session):
    """Test basic CRUD operations"""
    print("\n[TEST 5] Functionality check")

    try:
        # Try to access operaciones page
        resp = session.get(f"{PROD_URL}/operaciones", timeout=15)
        if resp.status_code == 200:
            print("  [OK] Can access operaciones page")
        else:
            print(f"  [FAIL] Operaciones page returned {resp.status_code}")
            return False

        # Try to access inventario
        resp = session.get(f"{PROD_URL}/inventario", timeout=15)
        if resp.status_code == 200:
            print("  [OK] Can access inventario page")
        else:
            print(f"  [FAIL] Inventario page returned {resp.status_code}")
            return False

        # Try to access ventas
        resp = session.get(f"{PROD_URL}/ventas", timeout=15)
        if resp.status_code == 200:
            print("  [OK] Can access ventas page")
        else:
            print(f"  [FAIL] Ventas page returned {resp.status_code}")
            return False

        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False

def main():
    print("\nTesting production deployment...")
    print(f"URL: {PROD_URL}\n")

    # Check if deployed
    if not test_deployment_status():
        print("\n[WAIT] App not deployed yet. Waiting 60 seconds...")
        time.sleep(60)
        print("[RETRY] Checking again...")
        if not test_deployment_status():
            print("\n[ERROR] DEPLOYMENT FAILED - App not responding")
            return False

    # Create session for authenticated tests
    session = requests.Session()

    # Run performance tests
    time.sleep(1)
    login_ok = test_login_and_performance(session)
    time.sleep(1)
    dashboard_ok = test_dashboard(session)
    time.sleep(1)
    api_ok = test_api_performance(session)
    time.sleep(1)
    func_ok = test_functionality(session)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    results = [
        ("Login", login_ok),
        ("Dashboard", dashboard_ok),
        ("APIs", api_ok),
        ("Functionality", func_ok),
    ]

    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        status = "[PASS]" if ok else "[FAIL]"
        print(f"{status} - {name}")

    print(f"\nOverall: {passed}/{total} passed")

    if passed == total:
        print("\n[SUCCESS] PRODUCTION DEPLOYMENT SUCCESSFUL!")
        print("All tests passed. System is operational.")
        return True
    else:
        print(f"\n[WARNING] Some tests failed. Check details above.")
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
