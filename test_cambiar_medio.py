#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test changing medio in operation edit."""
import sys
sys.path.insert(0, r'C:\Users\LENOVO\sisagent')

from app_compatible_optimizado import app, db, Usuario, Operacion, _ejecutar_editar_operacion_validada

with app.app_context():
    print("[1] Creating a test operation with BCP...")
    test_user = Usuario.query.filter_by(username='test_user').first()
    
    # Find or create an operation with BCP
    operacion = Operacion.query.filter_by(medio='BCP').order_by(Operacion.id.desc()).first()
    if operacion:
        print(f"    Found: ID {operacion.id}, Medio: {operacion.medio}")
    else:
        print("    No BCP operation found")
        sys.exit(1)

    print(f"\n[2] Changing medium from {operacion.medio} to BBVA...")
    try:
        resultado = _ejecutar_editar_operacion_validada({
            'id': str(operacion.id),
            'medio': 'BBVA',
        }, test_user)

        msg = resultado.get('mensaje', '')
        medio_nuevo = resultado.get('medio')
        medio_anterior = resultado.get('medio_anterior')
        
        print(f"    Message: {msg}")
        print(f"    Medio: {medio_anterior} -> {medio_nuevo}")
        
        if medio_anterior == 'BCP' and medio_nuevo == 'BBVA':
            print("\n[OK] Medium changed successfully!")
        else:
            print(f"\n[ERROR] Unexpected medium values")

    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()

print("\nTest complete!")
