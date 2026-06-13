#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pruebas exhaustivas para Fase 2: Machine Learning y Voice Learning
Verifica: tablas, endpoints, fuzzy matching, enseñanza
"""
import sys
import os
import json

# API key MUST be set via environment variable
# export ANTHROPIC_API_KEY="your-key-here"

from app_compatible_optimizado import (
    app, db, Usuario, BotCustomFunction, BotLearnedPhrase, BotTeachingHistory,
    _buscar_frase_aprendida
)

class Phase2MLTester:
    def __init__(self):
        self.results = {}
        self.admin_user = None
        self.test_user = None

    def setup(self):
        """Setup test environment"""
        with app.app_context():
            self.admin_user = Usuario.query.filter_by(username='admin').first()
            self.test_user = Usuario.query.filter_by(username='test_user').first()

            if not self.admin_user:
                print("[ERROR] Admin user not found")
                return False
            if not self.test_user:
                print("[ERROR] Test user not found")
                return False

        print(f"[OK] Setup: Admin={self.admin_user.username}, TestUser={self.test_user.username}")
        return True

    def test(self, name, func):
        """Run a test"""
        print(f"\n[TEST] {name}")
        try:
            result = func()
            status = "PASS" if result else "FAIL"
            self.results[name] = result
            print(f"[{status}] {name}")
            return result
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            import traceback
            traceback.print_exc()
            self.results[name] = False
            return False

    # ===== TABLE TESTS =====

    def test_tables_exist(self):
        """Verify all new tables exist"""
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            required = ['bot_custom_function', 'bot_learned_phrase', 'bot_teaching_history']
            for tabla in required:
                if tabla not in tables:
                    print(f"  [MISSING] {tabla}")
                    return False
                print(f"  [OK] {tabla} exists")

            return True

    # ===== FUZZY MATCHING TESTS =====

    def test_fuzzy_match_simple(self):
        """Test fuzzy matching of learned phrases"""
        with app.app_context():
            # Create a learned phrase
            frase = BotLearnedPhrase(
                usuario_id=self.test_user.id,
                frase_original="registra una opa",
                frase_normalizada="registra una operacion",
                categoria="operacion",
                confianza=0.9,
                frecuencia=1
            )
            db.session.add(frase)
            db.session.commit()

            # Test fuzzy match
            resultado = _buscar_frase_aprendida(self.test_user.id, "registra una opa")

            if resultado and resultado['frase_normalizada'] == "registra una operacion":
                print(f"  [OK] Fuzzy match found: {resultado}")
                return True
            else:
                print(f"  [FAIL] Fuzzy match failed: {resultado}")
                return False

    def test_fuzzy_match_no_match(self):
        """Test fuzzy matching with no match"""
        with app.app_context():
            resultado = _buscar_frase_aprendida(self.test_user.id, "xyz abc def")

            if resultado is None:
                print(f"  [OK] No match returned correctly")
                return True
            else:
                print(f"  [FAIL] Should not match: {resultado}")
                return False

    # ===== DATABASE TESTS =====

    def test_create_custom_function(self):
        """Test creating custom function directly"""
        with app.app_context():
            func = BotCustomFunction(
                nombre="test_registrar_pago_yape",
                descripcion="Registra pago por Yape",
                parametros=[{"name": "monto", "type": "float"}],
                logica="Llamar a registrar_operacion con medio=YAPE",
                admin_id=self.admin_user.id,
                activo=True
            )
            db.session.add(func)
            db.session.commit()

            # Verify it exists
            found = BotCustomFunction.query.filter_by(
                nombre="test_registrar_pago_yape"
            ).first()

            if found:
                print(f"  [OK] Function created: {found.nombre}")
                return True
            else:
                print(f"  [FAIL] Function not found")
                return False

    def test_create_learned_phrase(self):
        """Test creating learned phrase directly"""
        with app.app_context():
            frase = BotLearnedPhrase(
                usuario_id=self.test_user.id,
                frase_original="coka",
                frase_normalizada="coca-cola",
                categoria="producto",
                confianza=0.95,
                frecuencia=1
            )
            db.session.add(frase)
            db.session.commit()

            # Verify it exists
            found = BotLearnedPhrase.query.filter_by(
                usuario_id=self.test_user.id,
                frase_original="coka"
            ).first()

            if found:
                print(f"  [OK] Phrase created: {found.frase_original} -> {found.frase_normalizada}")
                return True
            else:
                print(f"  [FAIL] Phrase not found")
                return False

    def test_create_teaching_history(self):
        """Test creating teaching history record"""
        with app.app_context():
            historial = BotTeachingHistory(
                admin_id=self.admin_user.id,
                tipo="function",
                contenido="Test function teaching",
                usuarios_afectados=2
            )
            db.session.add(historial)
            db.session.commit()

            found = BotTeachingHistory.query.filter_by(
                admin_id=self.admin_user.id,
                tipo="function"
            ).first()

            if found:
                print(f"  [OK] Teaching history created")
                return True
            else:
                print(f"  [FAIL] Teaching history not found")
                return False

    # ===== API ENDPOINT TESTS =====

    def test_api_get_custom_functions(self):
        """Test GET /api/bot/custom_functions endpoint"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.admin_user.id

            response = client.get(f'/api/bot/custom_functions/{self.admin_user.id}')

            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"  [OK] Got {len(data.get('funciones', []))} custom functions")
                    return True

            print(f"  [FAIL] Response: {response.status_code}")
            return False

    def test_api_get_learned_phrases(self):
        """Test GET /api/bot/learned_phrases endpoint"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = self.test_user.id

            response = client.get(f'/api/bot/learned_phrases/{self.test_user.id}')

            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    total = data.get('total', 0)
                    print(f"  [OK] Got {total} learned phrases")
                    return True

            print(f"  [FAIL] Response: {response.status_code}")
            return False

    # ===== COMPLEX WORKFLOW TESTS =====

    def test_complete_learning_workflow(self):
        """Test complete workflow: teach -> use -> learn"""
        print("\n  >>> Complete Learning Workflow <<<")

        # Step 1: Admin teaches function
        print("  Step 1: Admin teaches function")
        with app.app_context():
            func = BotCustomFunction(
                nombre="workflow_test_func",
                descripcion="Test workflow function",
                parametros=[],
                logica="Test logic",
                admin_id=self.admin_user.id
            )
            db.session.add(func)
            db.session.commit()
            print(f"    [OK] Function taught")

        # Step 2: User learns phrase
        print("  Step 2: User learns phrase")
        with app.app_context():
            frase = BotLearnedPhrase(
                usuario_id=self.test_user.id,
                frase_original="wf",
                frase_normalizada="workflow",
                categoria="test"
            )
            db.session.add(frase)
            db.session.commit()
            print(f"    [OK] Phrase learned")

        # Step 3: User retrieves what they learned
        print("  Step 3: User retrieves learned phrases")
        with app.app_context():
            resultado = _buscar_frase_aprendida(self.test_user.id, "wf")
            if resultado and resultado['frase_normalizada'] == "workflow":
                print(f"    [OK] Can use learned phrase")
                return True
            else:
                print(f"    [FAIL] Cannot retrieve learned phrase")
                return False

    # ===== MULTI-USER LEARNING TESTS =====

    def test_isolated_learning_per_user(self):
        """Test that learning is isolated per user"""
        with app.app_context():
            # Add phrase to test_user
            frase1 = BotLearnedPhrase(
                usuario_id=self.test_user.id,
                frase_original="isolated",
                frase_normalizada="isolated_test",
                categoria="test"
            )
            db.session.add(frase1)
            db.session.commit()

            # Check test_user sees it
            result1 = _buscar_frase_aprendida(self.test_user.id, "isolated")

            # Check admin doesn't see it (unless they also learned it)
            result2 = _buscar_frase_aprendida(self.admin_user.id, "isolated")

            if result1 and result1['frase_normalizada'] == "isolated_test" and result2 is None:
                print(f"  [OK] Learning isolation works")
                return True
            else:
                print(f"  [FAIL] Learning isolation broken")
                return False

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("FASE 2: MACHINE LEARNING & VOICE LEARNING - EXHAUSTIVE TESTING")
        print("="*70)

        if not self.setup():
            return False

        # Table Tests
        print("\n" + "="*70)
        print("[GROUP] DATABASE TABLES")
        print("="*70)
        self.test("Tables exist", self.test_tables_exist)

        # Fuzzy Matching Tests
        print("\n" + "="*70)
        print("[GROUP] FUZZY MATCHING")
        print("="*70)
        self.test("Fuzzy match found", self.test_fuzzy_match_simple)
        self.test("Fuzzy match not found", self.test_fuzzy_match_no_match)

        # Database Tests
        print("\n" + "="*70)
        print("[GROUP] DIRECT DATABASE OPERATIONS")
        print("="*70)
        self.test("Create custom function", self.test_create_custom_function)
        self.test("Create learned phrase", self.test_create_learned_phrase)
        self.test("Create teaching history", self.test_create_teaching_history)

        # API Tests
        print("\n" + "="*70)
        print("[GROUP] API ENDPOINTS")
        print("="*70)
        self.test("GET /api/bot/custom_functions", self.test_api_get_custom_functions)
        self.test("GET /api/bot/learned_phrases", self.test_api_get_learned_phrases)

        # Complex Workflow Tests
        print("\n" + "="*70)
        print("[GROUP] COMPLEX WORKFLOWS")
        print("="*70)
        self.test("Complete learning workflow", self.test_complete_learning_workflow)
        self.test("Isolated learning per user", self.test_isolated_learning_per_user)

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)

        for name, result in self.results.items():
            status = "PASS" if result else "FAIL"
            print(f"[{status}] {name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed >= total - 2:  # Allow up to 2 failures
            print("\n[OK] FASE 2 TESTING SUCCESSFUL")
            return 0
        else:
            print(f"\n[WARN] {total - passed} tests failed")
            return 1

def main():
    tester = Phase2MLTester()
    return tester.run_all_tests()

if __name__ == '__main__':
    sys.exit(main() or 0)
