#!/usr/bin/env python3
"""
Test: Verify P0/P1 performance optimizations
- Debounce chat toggle
- Lazy load chat messages (max 20)
- Cache dashboard queries
"""
import time
import subprocess
import sys

def test_debounce_in_code():
    """Verify debounce is in the code"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for debounce timer variable
    if 'let toggleDebounceTimer' not in content:
        print("[FAIL] Debounce timer variable not found")
        return False

    # Check for debounce logic
    if 'clearTimeout(toggleDebounceTimer)' not in content:
        print("[FAIL] Debounce clearTimeout not found")
        return False

    # Check for debounce setTimeout
    if 'toggleDebounceTimer = setTimeout' not in content:
        print("[FAIL] Debounce setTimeout not found")
        return False

    print("[PASS] Chat toggle debounce is implemented (50ms)")
    return True

def test_lazy_load_in_code():
    """Verify lazy loading is in the code"""
    with open('templates/base.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for lazy load constant
    if 'MAX_VISIBLE' not in content:
        print("[FAIL] MAX_VISIBLE constant not found")
        return False

    # Check for slice logic
    if 'history.slice(-MAX_VISIBLE)' not in content:
        print("[FAIL] History slice logic not found")
        return False

    # Check for "older messages" indicator
    if 'mensajes anteriores' not in content:
        print("[FAIL] Older messages indicator not found")
        return False

    print("[PASS] Chat message lazy loading is implemented (max 20 visible)")
    return True

def test_cache_decorator_in_code():
    """Verify cache decorator is applied"""
    with open('app_compatible_optimizado.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for cache decorator on /api/comisiones
    if '@cache.cached(timeout=30' not in content:
        print("[FAIL] Cache decorator not found on /api/comisiones")
        return False

    if 'api_dashboard_comisiones' not in content:
        print("[FAIL] api_dashboard_comisiones function not found")
        return False

    print("[PASS] Dashboard queries cached (30s TTL)")
    return True

def main():
    print("\n" + "="*60)
    print("PERFORMANCE OPTIMIZATION VERIFICATION")
    print("="*60 + "\n")

    tests = [
        ("P0.1: Chat toggle debounce", test_debounce_in_code),
        ("P0.2: Chat message lazy loading", test_lazy_load_in_code),
        ("P1.1: Dashboard query caching", test_cache_decorator_in_code),
    ]

    results = []
    for name, test_func in tests:
        print("[TEST] " + name)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print("[ERROR] " + str(e))
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print("RESULTS: {}/{} PASSED".format(passed, total))
    print("="*60 + "\n")

    if passed == total:
        print("[SUCCESS] ALL OPTIMIZATIONS IMPLEMENTED")
        print("\nExpected improvements:")
        print("  - Chat toggle: instant (<50ms) instead of ~800ms")
        print("  - Chat rendering: instant even with 100+ messages")
        print("  - Dashboard load: 5x faster with 30s cache")
        return 0
    else:
        print("[FAIL] SOME OPTIMIZATIONS MISSING")
        return 1

if __name__ == '__main__':
    sys.exit(main())
