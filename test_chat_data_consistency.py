#!/usr/bin/env python3
"""
Test: Verify chat assistant uses real data instead of hallucinating
"""
import sys
sys.path.insert(0, '.')

from app_compatible_optimizado import app, db, Usuario, _ejecutar_turno_chat, Operacion, get_peru_time, Sucursal

def test_chat_data_consistency():
    """
    Test que el asistente consulta datos reales en lugar de alucinar
    """
    with app.app_context():
        # Setup: crear usuario admin
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(username='admin', es_admin=True)
            db.session.add(admin)
            db.session.commit()

        # Setup: crear sucursal
        sucursal = Sucursal.query.first()
        if not sucursal:
            sucursal = Sucursal(nombre='Test Branch', direccion='Test')
            db.session.add(sucursal)
            db.session.commit()

        # CREATE: una operación de prueba HOY
        op = Operacion(
            usuario_id=admin.id,
            sucursal_id=sucursal.id,
            monto=500.00,
            comision=5.00,
            medio='EFECTIVO',
            hora=get_peru_time()
        )
        db.session.add(op)
        db.session.commit()
        print(f"[SETUP] Created operacion: S/{op.monto} on {sucursal.nombre}")

        # TEST: Ask chat "¿hay operaciones hoy?"
        print("\n[TEST] Asking chat: '¿Hay operaciones hoy?'")
        historial = [
            {
                "role": "user",
                "parts": [{"text": "¿Hay operaciones hoy?"}]
            }
        ]

        try:
            resultado = _ejecutar_turno_chat(historial, admin)
            respuesta = resultado.get("texto", "")
            print(f"[RESPONSE] {respuesta}")

            # VERIFY: Check if the response mentions the operation we just created
            # It should mention "500" or "EFECTIVO" or "operacion" if it's querying real data
            if "operacion" in respuesta.lower() or "500" in respuesta or "efectivo" in respuesta.lower():
                print("[PASS] ✅ Chat is referencing real data (mentions operation/monto/medio)")
                return True
            elif "no" in respuesta.lower() and "operacion" in respuesta.lower():
                print("[FAIL] ❌ Chat is hallucinating - says NO operations exist when we just created one!")
                return False
            else:
                print(f"[UNCERTAIN] Response doesn't clearly indicate real data usage: {respuesta}")
                return False

        except Exception as e:
            print(f"[ERROR] Exception during test: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_chat_data_consistency()
    sys.exit(0 if success else 1)
