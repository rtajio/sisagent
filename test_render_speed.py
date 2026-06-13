#!/usr/bin/env python3
"""
Test: Where does the 2-second delay come from?
Breakdown:
1. Query time
2. Template render time
3. Response serialization time
"""
import sys
import time
import requests
from requests.adapters import HTTPAdapter

sys.path.insert(0, '.')
from app_compatible_optimizado import app, db, Usuario, Sucursal, MedioPago

def test_template_render():
    """Test template rendering speed locally"""
    with app.app_context():
        from app_compatible_optimizado import get_dashboard_stats_cache
        from flask import render_template

        # Get admin
        admin = Usuario.query.filter_by(username='admin').first()

        print("\n" + "="*80)
        print("TEMPLATE RENDER TEST")
        print("="*80)

        # Step 1: Get data
        print("\n[1] Getting dashboard stats...")
        start = time.time()
        stats = get_dashboard_stats_cache(admin.id, True)
        query_time = time.time() - start
        print(f"    Query time: {query_time:.3f}s")

        # Step 2: Get sucursales
        print("\n[2] Getting sucursales...")
        start = time.time()
        sucursales_activas = Sucursal.query.filter_by(activa=True).all()
        sucursal_time = time.time() - start
        print(f"    Query time: {sucursal_time:.3f}s")

        # Step 3: Render template
        print("\n[3] Rendering template...")
        start = time.time()
        context = {
            'total_sucursales': len(sucursales_activas),
            'total_usuarios': 9,
            **stats,
        }
        html = render_template('admin_dashboard.html', **context)
        render_time = time.time() - start
        print(f"    Render time: {render_time:.3f}s")
        print(f"    HTML size: {len(html) / 1024:.1f} KB")

        # Step 4: Compress response
        print("\n[4] Compressing response...")
        import gzip
        start = time.time()
        compressed = gzip.compress(html.encode('utf-8'), compresslevel=6)
        compress_time = time.time() - start
        print(f"    Compress time: {compress_time:.3f}s")
        print(f"    Compressed size: {len(compressed) / 1024:.1f} KB")

        # Summary
        print("\n" + "="*80)
        total = query_time + sucursal_time + render_time + compress_time
        print(f"BREAKDOWN:")
        print(f"  Queries:     {query_time:.3f}s ({query_time/total*100:.0f}%)")
        print(f"  Sucursales:  {sucursal_time:.3f}s ({sucursal_time/total*100:.0f}%)")
        print(f"  Render HTML: {render_time:.3f}s ({render_time/total*100:.0f}%)")
        print(f"  Compress:    {compress_time:.3f}s ({compress_time/total*100:.0f}%)")
        print(f"  TOTAL:       {total:.3f}s")
        print("="*80 + "\n")

if __name__ == '__main__':
    try:
        test_template_render()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
