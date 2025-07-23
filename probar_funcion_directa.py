#!/usr/bin/env python3
"""
Script para probar la función operaciones directamente
"""

from app import app, db, Sucursal, Usuario, Operacion
from flask_login import login_user
from datetime import datetime
import pytz
from flask import request
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

def probar_funcion_directa():
    """Probar la función operaciones directamente"""
    
    peru_tz = pytz.timezone('America/Lima')
    hoy = datetime.now(peru_tz).date()
    
    print("🧪 PROBANDO FUNCIÓN OPERACIONES DIRECTAMENTE")
    print("=" * 50)
    print(f"Fecha actual: {hoy}")
    
    with app.app_context():
        # 1. Verificar usuario normal
        usuario = Usuario.query.filter_by(username='40619883').first()
        if not usuario:
            print("❌ Usuario no encontrado")
            return False
        
        print(f"1. Usuario encontrado: {usuario.username}")
        print(f"   - Es admin: {usuario.es_admin}")
        print(f"   - Sucursal ID: {usuario.sucursal_id}")
        
        # 2. Simular request con fecha anterior
        print(f"\n2. Simulando request con fecha anterior...")
        
        # Crear un request simulado
        builder = EnvironBuilder(
            path='/operaciones',
            query_string='fecha=2024-01-01'
        )
        env = builder.get_environ()
        req = Request(env)
        
        # Simular la lógica de la función operaciones
        fecha = req.args.get('fecha')
        medio = req.args.get('medio')
        hora_inicio = req.args.get('hora_inicio')
        hora_fin = req.args.get('hora_fin')
        
        print(f"   - Fecha parámetro: {fecha}")
        print(f"   - Medio parámetro: {medio}")
        
        # Query base - admin puede ver todas las sucursales, usuarios solo su sucursal
        if usuario.es_admin:
            query = Operacion.query
            if req.args.get('sucursal_id'):
                query = query.filter_by(sucursal_id=req.args.get('sucursal_id'))
        else:
            query = Operacion.query.filter_by(sucursal_id=usuario.sucursal_id)
        
        # Obtener fecha actual para comparación
        hoy = datetime.now(peru_tz).date()
        
        # Aplicar filtros
        if fecha:
            # Convertir fecha string a objeto date para comparación
            fecha_objeto = datetime.strptime(fecha, '%Y-%m-%d').date()
            
            print(f"   - Fecha objeto: {fecha_objeto}")
            print(f"   - Fecha actual: {hoy}")
            print(f"   - Son iguales: {fecha_objeto == hoy}")
            
            # Solo admin puede buscar fechas diferentes al día actual
            if not usuario.es_admin and fecha_objeto != hoy:
                print("   ✅ DEBERÍA MOSTRAR ADVERTENCIA AQUÍ")
                print("   - Usuario NO es admin")
                print("   - Fecha es diferente a hoy")
                # flash('Solo los administradores pueden consultar operaciones de otros días', 'warning')
                fecha = None
            else:
                print("   ❌ NO DEBERÍA MOSTRAR ADVERTENCIA")
                if usuario.es_admin:
                    print("   - Usuario ES admin")
                if fecha_objeto == hoy:
                    print("   - Fecha es igual a hoy")
            
            if fecha:
                query = query.filter(db.func.date(Operacion.hora) == fecha)
                print(f"   - Aplicado filtro de fecha: {fecha}")
        
        # Si no hay fecha específica o no es admin, mostrar solo el día actual
        if not fecha or not usuario.es_admin:
            query = query.filter(db.func.date(Operacion.hora) == hoy)
            print(f"   - Aplicado filtro de fecha actual: {hoy}")
        
        if medio:
            query = query.filter(Operacion.medio == medio)
            print(f"   - Aplicado filtro de medio: {medio}")
        
        if hora_inicio:
            query = query.filter(Operacion.hora >= hora_inicio)
            print(f"   - Aplicado filtro de hora inicio: {hora_inicio}")
        
        if hora_fin:
            query = query.filter(Operacion.hora <= hora_fin)
            print(f"   - Aplicado filtro de hora fin: {hora_fin}")
        
        operaciones = query.order_by(Operacion.hora.desc()).all()
        print(f"   - Operaciones encontradas: {len(operaciones)}")
        
        # Detectar si hay filtros aplicados
        filtros_aplicados = bool(fecha or medio or hora_inicio or hora_fin or (usuario.es_admin and req.args.get('sucursal_id')))
        print(f"   - Filtros aplicados: {filtros_aplicados}")
        
        return True

if __name__ == "__main__":
    probar_funcion_directa() 