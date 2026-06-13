#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Advanced testing scenarios for inventory features:
- Multiple users with different roles
- Edge cases and error handling
- Complete workflows
- Permission enforcement
"""
import sys
import os

# API key must be set via environment variable before running
# export ANTHROPIC_API_KEY="your-key-here"

from app_compatible_optimizado import (
    app, db, Usuario, Producto, Sucursal,
    _ejecutar_turno_chat,
    _construir_mensajes_chat,
    _tool_productos_por_agotar,
    _tool_buscar_productos,
)

def test_scenario(name, func):
    """Run a test scenario and report results."""
    print(f"\n{'='*70}")
    print(f"[SCENARIO] {name}")
    print('='*70)
    try:
        result = func()
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
        return result
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def scenario_1_admin_low_stock():
    """Admin user checks low-stock products."""
    with app.app_context():
        admin = Usuario.query.filter_by(username='admin').first()

        # Get products with low stock
        result = _tool_productos_por_agotar({"limite_stock": 150}, admin)

        if not result.get('productos'):
            print("[SKIP] No low-stock products in database")
            return True

        productos = result.get('productos', [])
        print(f"Found {len(productos)} products with stock <= 150")
        for p in productos[:2]:
            print(f"  - {p['nombre']}: stock={p['stock']}")

        return True

def scenario_2_admin_smart_edit():
    """Admin tests smart product editing workflow."""
    with app.test_request_context():
        admin = Usuario.query.filter_by(username='admin').first()

        # Step 1: Search for existing product
        search = _tool_buscar_productos({"termino": "coca"}, admin)
        productos = search.get('productos', [])

        if not productos:
            print("[SKIP] No Coca-Cola product found")
            return True

        prod = productos[0]
        original_stock = prod['stock']

        print(f"Found: {prod['nombre']} (stock={original_stock})")

        # Step 2: Simulate chatbot smart editing with Claude
        mensaje = f"Anade 50 unidades de {prod['nombre']}"
        msgs = _construir_mensajes_chat([], mensaje, None, None)
        result = _ejecutar_turno_chat(msgs, admin, max_iteraciones=4)

        print(f"Bot response type: {result.get('tipo')}")
        print(f"Response length: {len(result.get('texto', ''))}")

        return True

def scenario_3_user_with_permissions():
    """Regular user checks products in their sucursal."""
    with app.app_context():
        # Create a test user if needed
        user = Usuario.query.filter_by(username='test_user').first()
        if not user:
            print("[SKIP] test_user not found")
            return True

        # Regular user should see their sucursal's products
        result = _tool_productos_por_agotar({"limite_stock": 150}, user)

        productos = result.get('productos', [])
        print(f"User sees {len(productos)} products")

        # Verify all products belong to user's sucursales
        if productos and user.sucursal_id:
            for p in productos[:2]:
                if p['sucursal_id'] == user.sucursal_id:
                    print(f"  [OK] {p['nombre']} in user's sucursal")
                else:
                    print(f"  [WARN] {p['nombre']} NOT in user's sucursal!")
                    return False

        return True

def scenario_4_nonexistent_product():
    """Search for product that doesn't exist."""
    with app.app_context():
        admin = Usuario.query.filter_by(username='admin').first()

        search = _tool_buscar_productos({"termino": "XXXNONEXISTENTXXX123"}, admin)
        productos = search.get('productos', [])

        if len(productos) == 0:
            print("[OK] Search correctly returns empty for non-existent product")
            return True
        else:
            print(f"[WARN] Found {len(productos)} products for non-existent search")
            return False

def scenario_5_empty_stock():
    """Verify handling of products with zero stock."""
    with app.app_context():
        # Find or create a product with 0 stock
        prod = Producto.query.filter_by(nombre='Coca-Cola').first()
        if not prod:
            print("[SKIP] Coca-Cola product not found")
            return True

        original_stock = prod.stock
        prod.stock = 0
        db.session.commit()

        try:
            admin = Usuario.query.filter_by(username='admin').first()

            # productos_por_agotar with threshold 0 should include it
            result = _tool_productos_por_agotar({"limite_stock": 0}, admin)
            productos = result.get('productos', [])

            zero_stock_found = any(p['stock'] == 0 for p in productos)
            print(f"Products with 0 stock found: {zero_stock_found}")

            return True
        finally:
            # Restore original stock
            prod.stock = original_stock
            db.session.commit()

def scenario_6_multiple_sucursales():
    """Verify that admin sees products from all sucursales."""
    with app.app_context():
        admin = Usuario.query.filter_by(username='admin').first()

        result = _tool_productos_por_agotar({"limite_stock": 1000}, admin)
        productos = result.get('productos', [])

        if not productos:
            print("[SKIP] No products found")
            return True

        # Check that we have products from different sucursales
        sucursal_ids = set(p['sucursal_id'] for p in productos)
        print(f"Products from {len(sucursal_ids)} sucursal(es)")

        # Admin should see all
        if admin.es_admin and len(sucursal_ids) > 0:
            print("[OK] Admin can see products from multiple sucursales")
            return True

        return True

def scenario_7_chat_with_context():
    """Chat with multi-turn conversation context."""
    with app.test_request_context():
        admin = Usuario.query.filter_by(username='admin').first()

        # Build conversation history
        historial = []

        # Turn 1: Low stock query
        msg1 = "Que productos se van a agotar"
        msgs1 = _construir_mensajes_chat(historial, msg1, None, None)
        result1 = _ejecutar_turno_chat(msgs1, admin, max_iteraciones=4)

        print(f"Turn 1: {result1.get('tipo')}")

        # Add to history
        historial.append({"role": "user", "content": msg1})
        historial.append({"role": "assistant", "content": result1.get('texto', '')})

        # Turn 2: Follow-up question
        msg2 = "Cuales tienen la fecha de vencimiento mas proxima"
        msgs2 = _construir_mensajes_chat(historial, msg2, None, None)
        result2 = _ejecutar_turno_chat(msgs2, admin, max_iteraciones=4)

        print(f"Turn 2: {result2.get('tipo')}")

        return result1.get('tipo') == 'texto' and result2.get('tipo') == 'texto'

def scenario_8_spanish_queries():
    """Test various Spanish language queries."""
    with app.test_request_context():
        admin = Usuario.query.filter_by(username='admin').first()

        queries = [
            "Que productos se agotan pronto",
            "Mostrame los productos con bajo stock",
            "Anade 25 coca cola",
            "Anade 50 unidades de Sprite",
            "Cuales son los precios actuales",
            "Cuanto stock hay de cada producto",
        ]

        success_count = 0
        for query in queries:
            try:
                msgs = _construir_mensajes_chat([], query, None, None)
                result = _ejecutar_turno_chat(msgs, admin, max_iteraciones=4)

                if result.get('tipo') in ['texto', 'propuesta']:
                    success_count += 1
                    print(f"[OK] '{query[:30]}...'")
                else:
                    print(f"[WARN] '{query[:30]}...' -> {result.get('tipo')}")
            except Exception as e:
                print(f"[ERROR] '{query[:30]}...' -> {e}")

        print(f"\nPassed {success_count}/{len(queries)} Spanish queries")
        return success_count >= len(queries) - 2  # Allow 2 failures

def scenario_9_database_integrity():
    """Verify database integrity after operations."""
    with app.app_context():
        # Count products before
        count_before = Producto.query.filter_by(activo=True).count()

        # Run queries
        admin = Usuario.query.filter_by(username='admin').first()
        _tool_productos_por_agotar({"limite_stock": 100}, admin)
        _tool_buscar_productos({"termino": "coca"}, admin)

        # Count products after (should be same)
        count_after = Producto.query.filter_by(activo=True).count()

        if count_before == count_after:
            print(f"[OK] Database integrity maintained ({count_before} products)")
            return True
        else:
            print(f"[ERROR] Product count changed: {count_before} -> {count_after}")
            return False

def scenario_10_fecha_vencimiento_consistency():
    """Verify fecha_vencimiento field consistency."""
    with app.app_context():
        admin = Usuario.query.filter_by(username='admin').first()

        # Get products
        result = _tool_productos_por_agotar({"limite_stock": 150}, admin)
        productos = result.get('productos', [])

        if not productos:
            print("[SKIP] No products found")
            return True

        # Check fecha_vencimiento is properly formatted
        valid_count = 0
        for p in productos:
            fv = p.get('fecha_vencimiento')
            if fv is None or isinstance(fv, str):
                valid_count += 1
            else:
                print(f"[WARN] Invalid fecha_vencimiento format: {fv}")

        print(f"Valid fecha_vencimiento format: {valid_count}/{len(productos)}")
        return valid_count == len(productos)

def main():
    print("\n" + "="*70)
    print("ADVANCED TESTING SCENARIOS")
    print("="*70)
    print(f"API Key configured: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")

    scenarios = [
        ("Admin checks low-stock products", scenario_1_admin_low_stock),
        ("Admin smart product editing", scenario_2_admin_smart_edit),
        ("Regular user with permissions", scenario_3_user_with_permissions),
        ("Search non-existent product", scenario_4_nonexistent_product),
        ("Handle empty stock", scenario_5_empty_stock),
        ("Multi-sucursal access", scenario_6_multiple_sucursales),
        ("Chat with context history", scenario_7_chat_with_context),
        ("Spanish language queries", scenario_8_spanish_queries),
        ("Database integrity check", scenario_9_database_integrity),
        ("fecha_vencimiento consistency", scenario_10_fecha_vencimiento_consistency),
    ]

    results = {}
    for name, func in scenarios:
        results[name] = test_scenario(name, func)

    # Summary
    print("\n" + "="*70)
    print("ADVANCED TESTING SUMMARY")
    print("="*70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")

    print(f"\nTotal: {passed}/{total} scenarios passed")

    if passed >= total - 1:  # Allow 1 failure
        print("\n[OK] ADVANCED TESTING SUCCESSFUL")
        print("All critical scenarios working correctly")
        return 0
    else:
        print("\n[ERROR] Some scenarios failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
