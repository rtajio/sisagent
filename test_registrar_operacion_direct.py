#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test _tool_registrar_operacion function directly."""
import sys
sys.path.insert(0, 'C:\\Users\\LENOVO\\sisagent')

from app_compatible_optimizado import app, db, Usuario, Operacion, MedioPago, MedioSucursal, Sucursal
from werkzeug.security import generate_password_hash

# Setup app context
with app.app_context():
    # 1. Create test user if needed
    print("[1] Setting up test user...")
    test_user = Usuario.query.filter_by(username='test_user').first()
    if not test_user:
        test_user = Usuario(
            username='test_user',
            password_hash=generate_password_hash('test123'),
            email='test@test.com',
            es_admin=False,
            es_admin_sucursal=False,
            nombre_completo='Test User'
        )
        db.session.add(test_user)
        db.session.commit()
        print("    Created test_user")
    else:
        print("    test_user already exists")

    # 2. Get sucursal
    print("\n[2] Setting up sucursal...")
    sucursal = Sucursal.query.first()
    if not sucursal:
        print("    ERROR: No sucursal found!")
        sys.exit(1)
    print(f"    Using sucursal: {sucursal.nombre}")

    # 3. Count operations before
    print("\n[3] Counting operations before...")
    ops_before = Operacion.query.count()
    print(f"    Operations before: {ops_before}")

    # 4. Import and test the function
    print("\n[4] Testing _tool_registrar_operacion...")
    from app_compatible_optimizado import _tool_registrar_operacion

    try:
        resultado = _tool_registrar_operacion({
            'monto': '100',
            'comision': '',
            'medio': 'BCP',
            'sucursal_id': str(sucursal.id),
            'comision_manual': 'false',
            'motivo_descuento': ''
        }, test_user)

        print(f"    Result type: {type(resultado)}")
        print(f"    Result: {resultado}")

        if isinstance(resultado, dict):
            if 'mensaje' in resultado:
                print(f"\n[OK] Function returned dict with 'mensaje'")
                print(f"    Message: {resultado['mensaje']}")
            else:
                print(f"\n[ERROR] Function returned dict but missing 'mensaje' key")
                print(f"    Keys: {resultado.keys()}")
        else:
            print(f"\n[ERROR] Function did not return dict")

    except Exception as e:
        print(f"\n[ERROR] Exception raised: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    # 5. Count operations after
    print("\n[5] Counting operations after...")
    ops_after = Operacion.query.count()
    print(f"    Operations after: {ops_after}")

    if ops_after > ops_before:
        print(f"    [OK] +{ops_after - ops_before} operation(s) registered!")
        latest = Operacion.query.order_by(Operacion.id.desc()).first()
        print(f"    Latest: ID {latest.id}, Monto: S/ {latest.monto}, Medio: {latest.medio}")
    else:
        print(f"    [ERROR] No operations were registered")

print("\nTest complete!")
