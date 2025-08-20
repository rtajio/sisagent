#!/usr/bin/env python3
"""
Script para diagnosticar el problema de las horas de operaciones
"""

from app import app, db, Operacion, Usuario
from datetime import datetime, timedelta
import pytz

def diagnosticar_horas():
    """Diagnosticar el problema de las horas de operaciones"""
    
    peru_tz = pytz.timezone('America/Lima')
    hora_actual = datetime.now(peru_tz)
    
    print("🔍 DIAGNÓSTICO DE HORAS DE OPERACIONES")
    print("=" * 50)
    print(f"Hora actual en Perú: {hora_actual}")
    print(f"Hora actual UTC: {datetime.utcnow()}")
    print(f"Diferencia: {hora_actual.hour - datetime.utcnow().hour} horas")
    
    with app.app_context():
        # 1. Verificar usuario específico
        usuario = Usuario.query.filter_by(username='62031506').first()
        if not usuario:
            print("❌ Usuario 62031506 no encontrado")
            return
        
        print(f"\n1. Usuario: {usuario.username}")
        print(f"   - Es admin: {usuario.es_admin}")
        print(f"   - Sucursal ID: {usuario.sucursal_id}")
        
        # 2. Verificar operaciones del usuario
        operaciones = Operacion.query.filter_by(usuario_id=usuario.id).order_by(Operacion.hora.desc()).limit(10).all()
        
        print(f"\n2. Últimas 10 operaciones del usuario:")
        for i, op in enumerate(operaciones, 1):
            print(f"   {i}. Hora: {op.hora} | TZ: {op.hora.tzinfo} | Monto: {op.monto} | Medio: {op.medio}")
        
        # 3. Verificar operaciones de hoy
        hoy = hora_actual.date()
        operaciones_hoy = Operacion.query.filter(
            Operacion.usuario_id == usuario.id,
            db.func.date(Operacion.hora) == hoy
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"\n3. Operaciones de hoy ({hoy}):")
        for i, op in enumerate(operaciones_hoy, 1):
            print(f"   {i}. Hora: {op.hora} | TZ: {op.hora.tzinfo} | Monto: {op.monto}")
        
        # 4. Verificar operaciones de ayer
        ayer = hoy - timedelta(days=1)
        operaciones_ayer = Operacion.query.filter(
            Operacion.usuario_id == usuario.id,
            db.func.date(Operacion.hora) == ayer
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"\n4. Operaciones de ayer ({ayer}):")
        for i, op in enumerate(operaciones_ayer, 1):
            print(f"   {i}. Hora: {op.hora} | TZ: {op.hora.tzinfo} | Monto: {op.monto}")
        
        # 5. Verificar operaciones después de las 19:00 de ayer
        ayer_19h = datetime.combine(ayer, datetime.min.time().replace(hour=19, minute=0, second=0)).replace(tzinfo=peru_tz)
        operaciones_despues_19h = Operacion.query.filter(
            Operacion.usuario_id == usuario.id,
            Operacion.hora >= ayer_19h
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"\n5. Operaciones después de las 19:00 de ayer ({ayer_19h}):")
        for i, op in enumerate(operaciones_despues_19h, 1):
            print(f"   {i}. Hora: {op.hora} | TZ: {op.hora.tzinfo} | Monto: {op.monto}")
        
        # 6. Verificar operaciones de las últimas 24 horas
        hace_24h = hora_actual - timedelta(hours=24)
        operaciones_24h = Operacion.query.filter(
            Operacion.usuario_id == usuario.id,
            Operacion.hora >= hace_24h
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"\n6. Operaciones de las últimas 24 horas (desde {hace_24h}):")
        for i, op in enumerate(operaciones_24h, 1):
            print(f"   {i}. Hora: {op.hora} | TZ: {op.hora.tzinfo} | Monto: {op.monto}")

if __name__ == "__main__":
    diagnosticar_horas() 