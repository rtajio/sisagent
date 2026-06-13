#!/usr/bin/env python3
"""
Deep diagnostic: measure request time breakdown
"""
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create a custom session that logs request timing
class TimingAdapter(HTTPAdapter):
    def __init__(self):
        super().__init__()
        self.start_time = None

    def send(self, request, **kwargs):
        self.start_time = time.time()
        print(f"[REQUEST] {request.method} {request.url}")
        response = super().send(request, **kwargs)
        elapsed = time.time() - self.start_time
        print(f"[RESPONSE] {response.status_code} - {elapsed:.3f}s")
        return response

def test_simple_api():
    """Test a very simple API endpoint"""
    session = requests.Session()
    session.mount('http://', TimingAdapter())

    print("\n[TEST] Simple API call - /ping")
    start = time.time()
    resp = session.get('http://localhost:5000/ping', timeout=30)
    total = time.time() - start
    print(f"[TOTAL] {total:.3f}s")
    print(f"[RESPONSE] {resp.json()}\n")

def test_login():
    """Test login"""
    session = requests.Session()
    session.mount('http://', TimingAdapter())

    print("\n[TEST] Login")
    start = time.time()
    resp = session.post('http://localhost:5000/login', data={
        'username': 'admin',
        'password': 'admin'
    }, allow_redirects=False, timeout=30)
    total = time.time() - start
    print(f"[TOTAL] {total:.3f}s\n")
    return session

def test_dashboard(session):
    """Test dashboard after login"""
    session.mount('http://', TimingAdapter())

    print("\n[TEST] Dashboard")
    start = time.time()
    resp = session.get('http://localhost:5000/dashboard', timeout=30)
    total = time.time() - start
    print(f"[TOTAL] {total:.3f}s")
    print(f"[STATUS] {resp.status_code}\n")

def test_api_endpoint(session):
    """Test API endpoint"""
    session.mount('http://', TimingAdapter())

    print("\n[TEST] API /api/operaciones/lista")
    start = time.time()
    resp = session.get('http://localhost:5000/api/operaciones/lista', timeout=30)
    total = time.time() - start
    print(f"[TOTAL] {total:.3f}s")
    print(f"[RESPONSE] {resp.json() if resp.status_code == 200 else resp.text[:100]}\n")

def main():
    print("\n" + "="*60)
    print("DETAILED REQUEST TIMING DIAGNOSTIC")
    print("="*60)

    # Test 1: Ping (simplest possible)
    test_simple_api()
    time.sleep(1)

    # Test 2: Login
    session = test_login()
    time.sleep(1)

    # Test 3: Dashboard
    test_dashboard(session)
    time.sleep(1)

    # Test 4: API
    test_api_endpoint(session)

    print("="*60)
    print("If all requests take ~5s, the delay is in Flask itself")
    print("If only certain endpoints are slow, check those endpoints")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
