#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test editing an operation."""
import sys
sys.path.insert(0, r'C:\Users\LENOVO\sisagent')

from app_compatible_optimizado import app, db, Usuario, Operacion, _ejecutar_editar_operacion_validada

# Setup app context
with app.app_context():
    print("[1] Setting up test user...")
    test_user = Usuario.query.filter_by(username='test_user').first()
    if not test_user:
        print("    ERROR: No test_user found!")
        sys.exit(1)

    print("\n[2] Getting latest operation...")
    operacion = Operacion.query.order_by(Operacion.id.desc()).first()
    if not operacion:
        print("    ERROR: No operations found!")
        sys.exit(1)

    print(f"    Found: ID {operacion.id}, Monto: S/ {operacion.monto}, Medio: {operacion.medio}")

    print("\n[3] Testing _ejecutar_editar_operacion_validada...")

    try:
        resultado = _ejecutar_editar_operacion_validada({
            'id': str(operacion.id),
            'monto': '50',
            'comision': '0.5',
            'medio': operacion.medio,
        }, test_user)

        print(f"    Result: {resultado}")

        if isinstance(resultado, dict) and 'mensaje' in resultado:
            print(f"\n[OK] Function returned dict with 'mensaje'")
            print(f"    Message: {resultado['mensaje']}")
        else:
            print(f"\n[ERROR] Unexpected result")

    except Exception as e:
        print(f"\n[ERROR] Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("\nTest complete!")
