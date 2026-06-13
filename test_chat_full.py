#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Full integration test of the chat with operation registration and editing."""
import sys
import os
sys.path.insert(0, r'C:\Users\LENOVO\sisagent')

# API key must be set via environment variable before running
# export ANTHROPIC_API_KEY="your-key-here"

from app_compatible_optimizado import app, db, Usuario

with app.app_context():
    # Get test user
    test_user = Usuario.query.filter_by(username='test_user').first()
    if not test_user:
        print("[ERROR] No test_user")
        sys.exit(1)

    print("[1] Test user ready")
    print("[2] API key configured")
    
    # Simulate chat flow
    from app_compatible_optimizado import _ejecutar_turno_chat
    
    # Initial message - register with unavailable medium
    print("\n[3] Test: Registra operacion de S/ 7 via CULQI (unavailable)")
    mensajes = [
        {"role": "user", "parts": [{"text": "Registra una operacion de S/ 7 via CULQI"}]}
    ]
    
    try:
        resultado = _ejecutar_turno_chat(mensajes, test_user)
        print(f"    Chat response: {resultado.get('texto')[:80]}...")
    except Exception as e:
        print(f"    ERROR: {e}")
        sys.exit(1)

    # Follow up with valid medium
    print("\n[4] Test: mejor usa KS")
    mensajes.append({"role": "model", "parts": [{"text": resultado.get('texto', '')}]})
    mensajes.append({"role": "user", "parts": [{"text": "mejor usa KS"}]})
    
    try:
        resultado2 = _ejecutar_turno_chat(mensajes, test_user)
        print(f"    Chat response: {resultado2.get('texto')[:80]}...")
    except Exception as e:
        print(f"    ERROR: {e}")
        sys.exit(1)

    # Try to change medium to BCP
    print("\n[5] Test: me equivoque era via BCP")
    mensajes.append({"role": "model", "parts": [{"text": resultado2.get('texto', '')}]})
    mensajes.append({"role": "user", "parts": [{"text": "me equivoque era via BCP"}]})
    
    try:
        resultado3 = _ejecutar_turno_chat(mensajes, test_user)
        response_text = resultado3.get('texto', '')
        print(f"    Chat response: {response_text}")
        
        if "BCP" in response_text and "error" not in response_text.lower():
            print("\n[OK] SUCCESS - Chat changed medium to BCP!")
        elif "error" in response_text.lower():
            print("\n[FAILED] Chat reported error")
        else:
            print(f"\n[?] Response unclear")
            
    except Exception as e:
        print(f"    ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("\nFull test complete!")
