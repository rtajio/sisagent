#!/usr/bin/env python3
"""
Debug version: Log all SQL queries and their execution time
to find which queries are slow
"""
import sys
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Add logging
logging.basicConfig()
logger = logging.getLogger('sqlalchemy.engine')
logger.setLevel(logging.INFO)

# Track query times
query_times = []

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    print(f"\n[SQL QUERY START]")

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)

    # Truncate statement for readability
    stmt = statement[:150] + "..." if len(statement) > 150 else statement

    if total_time > 0.1:  # Flag slow queries (>100ms)
        print(f"[SQL SLOW] {total_time:.3f}s - {stmt}")
    else:
        print(f"[SQL OK]   {total_time:.3f}s - {stmt}")

    query_times.append((stmt, total_time))

# Now import Flask app
sys.path.insert(0, '.')
from app_compatible_optimizado import app, db

def test_dashboard_queries():
    """Test dashboard with query logging"""
    with app.app_context():
        from app_compatible_optimizado import get_dashboard_stats_cache
        from flask_login import login_user
        from app_compatible_optimizado import Usuario

        # Get admin user
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            print("[ERROR] No admin user found")
            return

        print("\n" + "="*80)
        print("TESTING: get_dashboard_stats_cache(admin)")
        print("="*80)

        start = time.time()
        stats = get_dashboard_stats_cache(admin.id, True)
        total = time.time() - start

        print(f"\n[TOTAL TIME] {total:.3f}s")
        print(f"[RESULT] {stats}")

def print_summary():
    """Print query time summary"""
    print("\n" + "="*80)
    print("QUERY TIME SUMMARY")
    print("="*80)

    if not query_times:
        print("No queries executed")
        return

    slow_queries = [(s, t) for s, t in query_times if t > 0.1]
    if slow_queries:
        print(f"\nSLOW QUERIES ({len(slow_queries)}):")
        for stmt, t in sorted(slow_queries, key=lambda x: -x[1]):
            print(f"  {t:.3f}s - {stmt[:100]}")

    total_time = sum(t for _, t in query_times)
    print(f"\nTotal query time: {total_time:.3f}s across {len(query_times)} queries")

if __name__ == '__main__':
    try:
        test_dashboard_queries()
    finally:
        print_summary()
