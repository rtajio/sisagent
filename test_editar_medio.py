#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test changing medio in operation edit."""
import sys
sys.path.insert(0, r'C:\Users\LENOVO\sisagent')

from app_compatible_optimizado import app, db, Usuario, Operacion, _ejecutar_editar_operacion_validada

with app.app_context():
    print("[1] Getting test user...")
    test_user = Usuario.query.filter_by(username='test_user').first()
    if not test_user:
        print("    ERROR: No test_user!")
        sys.exit(1)

    print("\n[2] Getting latest operation...")
    operacion = Operacion.query.order_by(Operacion.id.desc()).first()
    print(f"    Found: ID {operacion.id}, Monto: S/ {operacion.monto}, Medio: {operacion.medio}")

    print("\n[3] Testing change medium ONLY...")
    try:
        resultado = _ejecutar_editar_operacion_validada({
            'id': str(operacion.id),
            'medio': 'BBVA',  # Change ONLY the medium
        }, test_user)

        print(f"    Result: {resultado}")
        if 'mensaje' in resultado:
            print(f"\n[OK] Message: {resultado['mensaje']}")
        else:
            print(f"\n[ERROR] No mensaje in result")

    except Exception as e:
        print(f"\n[ERROR] Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\nTest complete!")
