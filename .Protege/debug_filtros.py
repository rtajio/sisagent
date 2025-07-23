#!/usr/bin/env python3
"""
Script para debuggear los filtros de operaciones
"""

from app import app, db, Sucursal, Usuario, Operacion
from flask_login import login_user
from datetime import datetime
import pytz

def debug_filtros():
    """Debuggear los filtros de operaciones"""
    
    peru_tz = pytz.timezone('America/Lima')
    hoy = datetime.now(peru_tz).date()
    
    print("🔍 DEBUGGEANDO FILTROS DE OPERACIONES")
    print("=" * 40)
    print(f"Fecha actual: {hoy}")
    
    with app.app_context():
        # 1. Verificar usuario normal
        usuario = Usuario.query.filter_by(username='40619883').first()
        if usuario:
            print(f"1. Usuario encontrado: {usuario.username}")
            print(f"   - Es admin: {usuario.es_admin}")
            print(f"   - Sucursal ID: {usuario.sucursal_id}")
        else:
            print("❌ Usuario no encontrado")
            return False
        
        # 2. Simular la lógica de filtros
        print(f"\n2. Simulando lógica de filtros...")
        
        # Parámetros de prueba
        fecha_param = "2024-01-01"  # Fecha anterior
        print(f"   - Fecha parámetro: {fecha_param}")
        
        # Convertir fecha string a objeto date
        fecha_objeto = datetime.strptime(fecha_param, '%Y-%m-%d').date()
        print(f"   - Fecha objeto: {fecha_objeto}")
        print(f"   - Fecha actual: {hoy}")
        print(f"   - Son iguales: {fecha_objeto == hoy}")
        
        # Verificar condición
        if not usuario.es_admin and fecha_objeto != hoy:
            print("   ✅ CONDICIÓN VERDADERA: Debería mostrar advertencia")
            print("   - Usuario NO es admin")
            print("   - Fecha es diferente a hoy")
        else:
            print("   ❌ CONDICIÓN FALSA: No debería mostrar advertencia")
            if usuario.es_admin:
                print("   - Usuario ES admin")
            if fecha_objeto == hoy:
                print("   - Fecha es igual a hoy")
        
        # 3. Verificar operaciones existentes
        print(f"\n3. Verificando operaciones existentes...")
        operaciones = Operacion.query.all()
        print(f"   - Total operaciones: {len(operaciones)}")
        
        if operaciones:
            for op in operaciones[:3]:  # Mostrar solo las primeras 3
                print(f"   - Operación {op.id}: {op.hora.date()} - {op.medio}")
        
        # 4. Simular query completa
        print(f"\n4. Simulando query completa...")
        
        # Query base
        query = Operacion.query.filter_by(sucursal_id=usuario.sucursal_id)
        print(f"   - Query base: sucursal_id = {usuario.sucursal_id}")
        
        # Aplicar filtro de fecha
        if fecha_param:
            fecha_objeto = datetime.strptime(fecha_param, '%Y-%m-%d').date()
            
            if not usuario.es_admin and fecha_objeto != hoy:
                print("   ✅ Debería mostrar advertencia aquí")
                # flash('Solo los administradores pueden consultar operaciones de otros días', 'warning')
                fecha_param = None
            
            if fecha_param:
                query = query.filter(db.func.date(Operacion.hora) == fecha_param)
                print(f"   - Aplicado filtro de fecha: {fecha_param}")
        
        # Si no hay fecha específica o no es admin, mostrar solo el día actual
        if not fecha_param or not usuario.es_admin:
            query = query.filter(db.func.date(Operacion.hora) == hoy)
            print(f"   - Aplicado filtro de fecha actual: {hoy}")
        
        # Ejecutar query
        operaciones_filtradas = query.all()
        print(f"   - Operaciones filtradas: {len(operaciones_filtradas)}")
        
        return True

if __name__ == "__main__":
    debug_filtros() 