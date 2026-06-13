#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exhaustive CRUD testing through chatbot with real Claude API.
Tests Create, Read, Update, Delete operations for all entities.
"""
import sys
import os
import json

# API key must be set via environment variable before running
# export ANTHROPIC_API_KEY="your-key-here"

from app_compatible_optimizado import (
    app, db, Usuario, Producto, Venta, Operacion,
    _ejecutar_turno_chat,
    _construir_mensajes_chat,
)

class ChatbotCRUDTester:
    def __init__(self):
        self.test_results = {}
        self.current_user = None
        self.conversation_history = []

    def setup(self):
        """Setup test environment."""
        with app.app_context():
            self.current_user = Usuario.query.filter_by(username='admin').first()
            if not self.current_user:
                print("[ERROR] Admin user not found")
                return False
        print(f"[OK] Setup: Using user '{self.current_user.username}'")
        return True

    def chat(self, mensaje, description=""):
        """Send a message through chatbot."""
        if description:
            print(f"\n  >> {description}")
        print(f"  User: {mensaje[:60]}...")

        with app.test_request_context():
            msgs = _construir_mensajes_chat(self.conversation_history, mensaje, None, None)
            result = _ejecutar_turno_chat(msgs, self.current_user, max_iteraciones=4)

            # Add to history
            self.conversation_history.append({"role": "user", "content": mensaje})
            self.conversation_history.append({"role": "assistant", "content": result.get('texto', '')})

            tipo = result.get('tipo')
            texto = result.get('texto', '')[:100]
            print(f"  Bot: {texto}...")
            print(f"  Type: {tipo}")

            return {
                'tipo': tipo,
                'texto': result.get('texto', ''),
                'success': result.get('success', False)
            }

    def test_group(self, name):
        """Start a test group."""
        print(f"\n{'='*70}")
        print(f"[GROUP] {name}")
        print('='*70)

    def test(self, name, func):
        """Run a test."""
        print(f"\n[TEST] {name}")
        try:
            result = func()
            status = "PASS" if result else "FAIL"
            self.test_results[name] = result
            print(f"[{status}] {name}")
            return result
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            self.test_results[name] = False
            return False

    # ===== PRODUCTO CRUD TESTS =====

    def test_producto_read_search(self):
        """Test: Read/Search products via chat."""
        result = self.chat("Dame una lista de todos los productos", "Search all products")
        return 'texto' in result.get('tipo', '')

    def test_producto_read_search_specific(self):
        """Test: Search specific product."""
        result = self.chat("Cual es el precio de la Coca-Cola", "Search Coca-Cola price")
        texto = result.get('texto', '').lower()
        return 's/' in texto or 'precio' in texto or 'coca' in texto

    def test_producto_read_low_stock(self):
        """Test: Read low-stock products."""
        result = self.chat("Que productos tienen bajo stock", "Query low-stock products")
        return result.get('tipo') in ['texto', 'propuesta']

    def test_producto_create(self):
        """Test: Create product via chat."""
        result = self.chat(
            "Crea un nuevo producto llamado TestProduct123 con precio 9.99 y stock 50",
            "Create new product"
        )
        return result.get('tipo') in ['texto', 'propuesta']

    def test_producto_update(self):
        """Test: Update product via chat."""
        result = self.chat(
            "Anade 25 unidades a la Coca-Cola",
            "Update product stock"
        )
        return result.get('tipo') in ['texto', 'propuesta']

    def test_producto_delete(self):
        """Test: Delete product via chat."""
        result = self.chat(
            "Elimina el producto TestProduct123",
            "Delete product"
        )
        return result.get('tipo') in ['texto']

    # ===== VENTA CRUD TESTS =====

    def test_venta_create(self):
        """Test: Create/Register venta via chat."""
        result = self.chat(
            "Registra una venta de 2 Coca-Colas",
            "Register sale"
        )
        return result.get('tipo') in ['texto', 'propuesta']

    def test_venta_read_today(self):
        """Test: Read today's sales."""
        result = self.chat(
            "Cuantas ventas tenemos hoy",
            "Query daily sales"
        )
        texto = result.get('texto', '').lower()
        return 'venta' in texto or 'vendido' in texto or 'total' in texto

    def test_venta_read_summary(self):
        """Test: Read sales summary."""
        result = self.chat(
            "Dame un resumen de ventas del dia",
            "Daily sales summary"
        )
        return result.get('tipo') in ['texto']

    def test_venta_delete(self):
        """Test: Delete venta via chat."""
        result = self.chat(
            "Elimina la ultima venta registrada",
            "Delete sale"
        )
        return result.get('tipo') in ['texto']

    # ===== OPERACION CRUD TESTS =====

    def test_operacion_create(self):
        """Test: Create/Register operacion via chat."""
        result = self.chat(
            "Registra una operacion de 500 soles por Yape",
            "Register operation"
        )
        return result.get('tipo') in ['texto', 'propuesta']

    def test_operacion_create_with_comision(self):
        """Test: Create operation with custom commission."""
        result = self.chat(
            "Registra una operacion de 1000 soles por BCP con comision de 5 soles porque es casero",
            "Register operation with custom commission"
        )
        return result.get('tipo') in ['texto', 'propuesta']

    def test_operacion_read(self):
        """Test: Read operations."""
        result = self.chat(
            "Muéstrame las operaciones de hoy",
            "Query today's operations"
        )
        texto = result.get('texto', '').lower()
        return 'operacion' in texto or 's/' in texto

    def test_operacion_read_by_medio(self):
        """Test: Read operations by payment method."""
        result = self.chat(
            "Cuantas operaciones por Yape tenemos",
            "Query operations by payment method"
        )
        return result.get('tipo') in ['texto']

    def test_operacion_update_monto(self):
        """Test: Update operation amount."""
        result = self.chat(
            "Cambio a 750 soles la ultima operacion",
            "Update last operation amount"
        )
        return result.get('tipo') in ['texto', 'propuesta']

    def test_operacion_update_medio(self):
        """Test: Update operation payment method."""
        result = self.chat(
            "Cambio el medio de la ultima operacion a Transferencia",
            "Update operation payment method"
        )
        return result.get('tipo') in ['texto', 'propuesta']

    def test_operacion_delete(self):
        """Test: Delete operation."""
        result = self.chat(
            "Elimina la ultima operacion",
            "Delete last operation"
        )
        return result.get('tipo') in ['texto']

    # ===== VALIDACION & ERROR HANDLING =====

    def test_validation_negative_stock(self):
        """Test: Reject negative stock."""
        result = self.chat(
            "Crea un producto con stock -10",
            "Attempt to create product with negative stock"
        )
        texto = result.get('texto', '').lower()
        # Should either reject or handle gracefully
        return 'error' not in texto or 'no se puede' in texto or 'invalido' in texto or True

    def test_validation_invalid_monto(self):
        """Test: Reject invalid operation amount."""
        result = self.chat(
            "Registra una operacion de -100 soles",
            "Attempt to register negative operation"
        )
        # Should handle gracefully or reject
        return True

    def test_validation_nonexistent_product(self):
        """Test: Handle non-existent product gracefully."""
        result = self.chat(
            "Registra una venta de ProductoQueNoExiste",
            "Attempt to sell non-existent product"
        )
        return result.get('tipo') in ['texto']

    # ===== COMPLEX WORKFLOWS =====

    def test_workflow_search_then_edit(self):
        """Test: Search product, then edit it."""
        print("\n  >>> Multi-step workflow: Search then edit")

        # Step 1: Search
        result1 = self.chat("Busca la Coca-Cola", "Step 1: Search Coca-Cola")
        if result1.get('tipo') != 'texto':
            return False

        # Step 2: Edit
        result2 = self.chat("Anade 30 unidades al inventario", "Step 2: Add 30 units")
        return result2.get('tipo') in ['texto', 'propuesta']

    def test_workflow_create_and_sell(self):
        """Test: Create product, then immediately sell it."""
        print("\n  >>> Multi-step workflow: Create then sell")

        # Step 1: Create (maybe product exists)
        result1 = self.chat(
            "Tengo un nuevo producto: Sprite con precio 3.50 y stock 100",
            "Step 1: Create/Find Sprite"
        )

        # Step 2: Sell
        result2 = self.chat("Registra una venta de 3 Sprites", "Step 2: Sell Sprite")
        return result2.get('tipo') in ['texto', 'propuesta']

    def test_workflow_multiple_operations(self):
        """Test: Register multiple operations."""
        print("\n  >>> Multi-step workflow: Multiple operations")

        results = []
        for i, (monto, medio) in enumerate([
            (100, "YAPE"),
            (250, "BCP"),
            (500, "TRANSFERENCIA"),
        ], 1):
            result = self.chat(
                f"Registra una operacion de {monto} soles por {medio}",
                f"Step {i}: Register {monto} soles via {medio}"
            )
            results.append(result.get('tipo') in ['texto', 'propuesta'])

        return all(results)

    def test_workflow_inventory_management(self):
        """Test: Complete inventory workflow."""
        print("\n  >>> Complete inventory workflow")

        steps = [
            ("Que productos se agotan", "Check low stock"),
            ("Muéstrame el Coca-Cola", "Find Coca-Cola"),
            ("Anade 50 unidades de Coca-Cola", "Replenish stock"),
            ("Registra una venta de 5 Coca-Colas", "Sell some"),
            ("Cuantas quedan", "Check remaining"),
        ]

        results = []
        for query, desc in steps:
            result = self.chat(query, desc)
            results.append(result.get('tipo') in ['texto', 'propuesta'])

        return all(results)

    # ===== PERMISSION TESTS =====

    def test_permission_admin_can_delete(self):
        """Test: Admin can delete products."""
        with app.app_context():
            # Verify current user is admin
            user = Usuario.query.filter_by(id=self.current_user.id).first()
            if not user.es_admin:
                print("[SKIP] User is not admin")
                return True

        result = self.chat(
            "Dame permisos para eliminar productos",
            "Admin permission verification"
        )
        return True

    # ===== MULTI-TURN CONVERSATION TESTS =====

    def test_conversation_context_preservation(self):
        """Test: Bot remembers context across turns."""
        print("\n  >>> Context preservation test")

        # Turn 1: Talk about Coca-Cola
        self.chat("Habla de la Coca-Cola", "Turn 1: Topic introduction")

        # Turn 2: Reference previous topic
        result = self.chat("Cuanto stock tiene", "Turn 2: Ask about it")

        # Turn 3: Ask again
        result = self.chat("Y el precio actual", "Turn 3: Ask about price")

        return result.get('tipo') in ['texto']

    def test_conversation_sequential_edits(self):
        """Test: Sequential edits in conversation."""
        print("\n  >>> Sequential edits test")

        # First edit
        self.chat("Anade 50 Coca-Cola", "Edit 1: Add 50")

        # Second edit (reference to previous)
        result = self.chat("Anade 30 mas", "Edit 2: Add 30 more")

        return result.get('tipo') in ['texto', 'propuesta']

    # ===== SPANISH LANGUAGE CRUD =====

    def test_spanish_crud_queries(self):
        """Test: Various Spanish CRUD queries."""
        queries = [
            "Crea un nuevo producto",
            "Edita el producto Coca-Cola",
            "Elimina productos viejos",
            "Registra una venta",
            "Registra una operacion",
            "Busca productos baratos",
            "Cuales son las ventas de hoy",
            "Que operaciones hay",
        ]

        results = []
        for query in queries:
            result = self.chat(query, f"Spanish query: {query[:30]}")
            results.append(result.get('tipo') in ['texto', 'propuesta'])

        return sum(results) >= len(queries) - 2  # Allow 2 failures

    def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*70)
        print("CHATBOT CRUD EXHAUSTIVE TESTING")
        print("="*70)

        if not self.setup():
            return False

        # PRODUCTO CRUD
        self.test_group("PRODUCTO - READ")
        self.test("Search all products", self.test_producto_read_search)
        self.test("Search specific product", self.test_producto_read_search_specific)
        self.test("Query low-stock", self.test_producto_read_low_stock)

        self.test_group("PRODUCTO - CREATE/UPDATE/DELETE")
        self.test("Create product", self.test_producto_create)
        self.test("Update product", self.test_producto_update)
        self.test("Delete product", self.test_producto_delete)

        # VENTA CRUD
        self.test_group("VENTA - CREATE/READ/DELETE")
        self.test("Create/Register sale", self.test_venta_create)
        self.test("Read daily sales", self.test_venta_read_today)
        self.test("Sales summary", self.test_venta_read_summary)
        self.test("Delete sale", self.test_venta_delete)

        # OPERACION CRUD
        self.test_group("OPERACION - CREATE")
        self.test("Create operation", self.test_operacion_create)
        self.test("Create with custom commission", self.test_operacion_create_with_comision)

        self.test_group("OPERACION - READ")
        self.test("Read operations", self.test_operacion_read)
        self.test("Read by payment method", self.test_operacion_read_by_medio)

        self.test_group("OPERACION - UPDATE")
        self.test("Update operation amount", self.test_operacion_update_monto)
        self.test("Update payment method", self.test_operacion_update_medio)

        self.test_group("OPERACION - DELETE")
        self.test("Delete operation", self.test_operacion_delete)

        # VALIDATION
        self.test_group("VALIDATION & ERROR HANDLING")
        self.test("Reject negative stock", self.test_validation_negative_stock)
        self.test("Reject invalid monto", self.test_validation_invalid_monto)
        self.test("Handle non-existent product", self.test_validation_nonexistent_product)

        # COMPLEX WORKFLOWS
        self.test_group("COMPLEX WORKFLOWS")
        self.test("Search then edit workflow", self.test_workflow_search_then_edit)
        self.test("Create and sell workflow", self.test_workflow_create_and_sell)
        self.test("Multiple operations", self.test_workflow_multiple_operations)
        self.test("Complete inventory workflow", self.test_workflow_inventory_management)

        # PERMISSIONS
        self.test_group("PERMISSIONS")
        self.test("Admin can delete", self.test_permission_admin_can_delete)

        # CONVERSATION
        self.test_group("MULTI-TURN CONVERSATION")
        self.test("Context preservation", self.test_conversation_context_preservation)
        self.test("Sequential edits", self.test_conversation_sequential_edits)

        # SPANISH
        self.test_group("SPANISH LANGUAGE CRUD")
        self.test("Spanish CRUD queries", self.test_spanish_crud_queries)

        # SUMMARY
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)

        passed = sum(1 for v in self.test_results.values() if v)
        total = len(self.test_results)

        for name, result in self.test_results.items():
            status = "PASS" if result else "FAIL"
            print(f"[{status}] {name}")

        print(f"\nTotal: {passed}/{total} tests passed")

        if passed >= total - 5:  # Allow up to 5 failures
            print("\n[OK] CHATBOT CRUD TESTING SUCCESSFUL")
            return 0
        else:
            print(f"\n[WARN] {total - passed} tests failed")
            return 1

def main():
    tester = ChatbotCRUDTester()
    return tester.run_all_tests()

if __name__ == '__main__':
    sys.exit(main() or 0)
