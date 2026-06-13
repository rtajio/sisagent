#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r'C:\Users\LENOVO\sisagent')
# API key must be set via environment variable before running
# export ANTHROPIC_API_KEY="your-key-here"

from app_compatible_optimizado import app, db, Usuario, _ejecutar_turno_chat

with app.app_context():
    test_user = Usuario.query.filter_by(username='test_user').first()
    
    print("[TEST] Full chat flow with medium change")
    print("[1] Register operation with CULQI (unavailable)")
    msgs = [{"role": "user", "parts": [{"text": "registra operacion de S/ 7 via CULQI"}]}]
    r1 = _ejecutar_turno_chat(msgs, test_user)
    print(f"    OK - Registered with CULQI")
    
    print("[2] Request to use KS instead (edit)")
    msgs.append({"role": "model", "parts": [{"text": r1.get('texto', '')}]})
    msgs.append({"role": "user", "parts": [{"text": "usa KS"}]})
    r2 = _ejecutar_turno_chat(msgs, test_user)
    resp2 = r2.get('texto', '')
    if 'error' in resp2.lower():
        print(f"    FAIL - Got error: {resp2[:60]}")
    else:
        print(f"    OK - Edit accepted")
    
    print("[3] Request to change to BCP")
    msgs.append({"role": "model", "parts": [{"text": resp2}]})
    msgs.append({"role": "user", "parts": [{"text": "cambiar a BCP"}]})
    r3 = _ejecutar_turno_chat(msgs, test_user)
    resp3 = r3.get('texto', '')
    if 'error' in resp3.lower():
        print(f"    FAIL - Got error: {resp3[:60]}")
    elif 'BCP' in resp3:
        print(f"    OK - Successfully changed to BCP!")
    else:
        print(f"    ? - Unclear response: {resp3[:60]}")
    
    print("\n[DONE]")
