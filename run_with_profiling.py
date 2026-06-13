#!/usr/bin/env python3
"""
Run Flask with request profiling to see where time is spent
"""
import sys
import cProfile
import pstats
import io
import time
from functools import wraps

# Monkey-patch Flask to profile requests
original_wsgi_app = None

def profile_request(environ, start_response):
    """Profile a single WSGI request"""
    pr = cProfile.Profile()
    pr.enable()

    start_time = time.time()
    result = original_wsgi_app(environ, start_response)
    elapsed = time.time() - start_time

    pr.disable()

    # Print slow requests
    if elapsed > 0.5:
        print(f"\n{'='*80}")
        print(f"[PROFILE] Request took {elapsed:.3f}s (SLOW!)")
        print(f"PATH: {environ.get('PATH_INFO')}")
        print(f"{'='*80}")

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats(15)  # Top 15 functions
        print(s.getvalue())
        print(f"{'='*80}\n")

    return result

sys.path.insert(0, '.')
from app_compatible_optimizado import app

# Patch WSGI app
original_wsgi_app = app.wsgi_app
app.wsgi_app = profile_request

if __name__ == '__main__':
    print("\n[START] Flask with request profiling")
    print("[INFO] Look for [PROFILE] messages showing slow requests")
    print("[INFO] Navigate to http://localhost:5000 to test\n")

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,  # disable debug for cleaner profiling
        use_reloader=False,
        use_debugger=False,
        threaded=True
    )
