#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Direct database tests for inventory features."""
import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\sisagent')

from app_compatible_optimizado import app, db, Producto, Sucursal
from datetime import datetime, date

def test_fecha_vencimiento_field():
    """Test that fecha_vencimiento field exists and works."""
    print("\n[TEST 1] Fecha vencimiento field in Producto model")
    print("-" * 50)

    with app.app_context():
        try:
            # Get first sucursal
            suc = Sucursal.query.first()
            if not suc:
                print("[ERROR] No sucursal found in database")
                return False

            # Create a test product with fecha_vencimiento
            hoy = date.today()
            vencimiento = date(hoy.year, hoy.month + 1 if hoy.month < 12 else 12, 15)

            prod = Producto(
                nombre=f"Test Product {datetime.now().timestamp()}",
                descripcion="Test product",
                precio=10.0,
                stock=5,
                sucursal_id=suc.id,
                activo=True,
                fecha_vencimiento=vencimiento
            )

            db.session.add(prod)
            db.session.commit()
            prod_id = prod.id

            # Retrieve and verify
            retrieved = Producto.query.get(prod_id)
            if not retrieved:
                print("[ERROR] Could not retrieve product")
                return False

            if retrieved.fecha_vencimiento != vencimiento:
                print(f"[ERROR] Fecha vencimiento mismatch: {retrieved.fecha_vencimiento} != {vencimiento}")
                return False

            print(f"[OK] Created product with fecha_vencimiento: {retrieved.fecha_vencimiento}")

            # Clean up
            db.session.delete(retrieved)
            db.session.commit()

            return True

        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_productos_por_agotar_function():
    """Test the _tool_productos_por_agotar function."""
    print("\n[TEST 2] productos_por_agotar function")
    print("-" * 50)

    with app.app_context():
        try:
            from app_compatible_optimizado import _tool_productos_por_agotar, Usuario

            # Get a test user
            user = Usuario.query.filter_by(username='test_user').first()
            if not user:
                print("[ERROR] test_user not found")
                return False

            # Call the function
            result = _tool_productos_por_agotar({"limite_stock": 10}, user)

            if not isinstance(result, dict):
                print(f"[ERROR] Function did not return dict: {type(result)}")
                return False

            if "productos" not in result:
                print(f"[ERROR] Result missing 'productos' key: {result.keys()}")
                return False

            productos = result.get("productos", [])
            print(f"[OK] Found {len(productos)} products with stock <= 10")

            if productos:
                prod = productos[0]
                print(f"    Sample: {prod.get('nombre')} (stock: {prod.get('stock')})")
                # Check if fecha_vencimiento is included
                if "fecha_vencimiento" in prod:
                    print(f"    Has fecha_vencimiento: {prod.get('fecha_vencimiento')}")

            return True

        except Exception as e:
            print(f"[ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_chatbot_tools_registration():
    """Test that productos_por_agotar is in CHATBOT_TOOLS."""
    print("\n[TEST 3] productos_por_agotar registered in CHATBOT_TOOLS")
    print("-" * 50)

    try:
        from app_compatible_optimizado import CHATBOT_TOOLS, _HERRAMIENTAS_DECLARACIONES

        # Check if registered in CHATBOT_TOOLS
        if "productos_por_agotar" not in CHATBOT_TOOLS:
            print("[ERROR] productos_por_agotar not in CHATBOT_TOOLS")
            return False

        tool_config = CHATBOT_TOOLS["productos_por_agotar"]
        print(f"[OK] Found in CHATBOT_TOOLS: {tool_config.keys()}")

        # Check if in declarations
        decl = next((d for d in _HERRAMIENTAS_DECLARACIONES if d.get("name") == "productos_por_agotar"), None)
        if not decl:
            print("[ERROR] Declaration not found in _HERRAMIENTAS_DECLARACIONES")
            return False

        print(f"[OK] Found declaration: {decl.get('description')[:50]}...")
        return True

    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Direct Database Tests for Inventory Features")
    print("=" * 50)

    tests = [
        ("fecha_vencimiento_field", test_fecha_vencimiento_field),
        ("productos_por_agotar_function", test_productos_por_agotar_function),
        ("chatbot_tools_registration", test_chatbot_tools_registration),
    ]

    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"[ERROR] Test {name} raised exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for name, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        print(f"{status} {name}")

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n[OK] All database tests passed!")
        return 0
    else:
        print("\n[ERROR] Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
