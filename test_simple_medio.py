#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'C:\Users\LENOVO\sisagent')

from app_compatible_optimizado import app, db, Usuario, Operacion, _ejecutar_editar_operacion_validada

with app.app_context():
    test_user = Usuario.query.filter_by(username='test_user').first()
    
    # Find BCP operation
    operacion = Operacion.query.filter_by(medio='BCP').order_by(Operacion.id.desc()).first()
    if not operacion:
        print("ERROR: No BCP operation")
        sys.exit(1)

    op_id = operacion.id
    print(f"[1] Found operation ID {op_id}, Medio: {operacion.medio}")

    # Change to BBVA
    print(f"[2] Changing to BBVA...")
    try:
        resultado = _ejecutar_editar_operacion_validada({
            'id': str(op_id),
            'medio': 'BBVA',
        }, test_user)

        medio_nuevo = resultado.get('medio')
        medio_anterior = resultado.get('medio_anterior')
        op_id_result = resultado.get('operacion_id')
        
        print(f"[3] Result: Op {op_id_result}, Medio anterior={medio_anterior}, Nuevo={medio_nuevo}")
        
        if op_id_result == op_id and medio_anterior == 'BCP' and medio_nuevo == 'BBVA':
            print("[OK] SUCCESS - Medium changed!")
        else:
            print(f"[ERROR] Unexpected result")

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
