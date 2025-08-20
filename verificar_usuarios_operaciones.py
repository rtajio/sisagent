#!/usr/bin/env python3
"""
Script para verificar usuarios y operaciones existentes
"""

from app import app, db, Operacion, Usuario
from datetime import datetime, timedelta
import pytz

def verificar_usuarios_operaciones():
    """Verificar usuarios y operaciones existentes"""
    
    peru_tz = pytz.timezone('America/Lima')
    hora_actual = datetime.now(peru_tz)
    
    print("🔍 VERIFICACIÓN DE USUARIOS Y OPERACIONES")
    print("=" * 50)
    print(f"Hora actual en Perú: {hora_actual}")
    
    with app.app_context():
        # 1. Verificar todos los usuarios
        usuarios = Usuario.query.all()
        print(f"\n1. Usuarios existentes ({len(usuarios)}):")
        for i, user in enumerate(usuarios, 1):
            print(f"   {i}. Username: {user.username} | Nombre: {user.nombre_completo} | Admin: {user.es_admin}")
        
        # 2. Verificar operaciones recientes
        operaciones_recientes = Operacion.query.order_by(Operacion.hora.desc()).limit(20).all()
        print(f"\n2. Últimas 20 operaciones:")
        for i, op in enumerate(operaciones_recientes, 1):
            usuario = Usuario.query.get(op.usuario_id)
            username = usuario.username if usuario else "N/A"
            print(f"   {i}. Hora: {op.hora} | Usuario: {username} | Monto: {op.monto} | Medio: {op.medio}")
        
        # 3. Verificar operaciones de hoy
        hoy = hora_actual.date()
        operaciones_hoy = Operacion.query.filter(
            db.func.date(Operacion.hora) == hoy
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"\n3. Operaciones de hoy ({hoy}) - {len(operaciones_hoy)} operaciones:")
        for i, op in enumerate(operaciones_hoy, 1):
            usuario = Usuario.query.get(op.usuario_id)
            username = usuario.username if usuario else "N/A"
            print(f"   {i}. Hora: {op.hora} | Usuario: {username} | Monto: {op.monto}")
        
        # 4. Verificar operaciones de ayer
        ayer = hoy - timedelta(days=1)
        operaciones_ayer = Operacion.query.filter(
            db.func.date(Operacion.hora) == ayer
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"\n4. Operaciones de ayer ({ayer}) - {len(operaciones_ayer)} operaciones:")
        for i, op in enumerate(operaciones_ayer, 1):
            usuario = Usuario.query.get(op.usuario_id)
            username = usuario.username if usuario else "N/A"
            print(f"   {i}. Hora: {op.hora} | Usuario: {username} | Monto: {op.monto}")
        
        # 5. Verificar operaciones después de las 19:00 de ayer
        ayer_19h = datetime.combine(ayer, datetime.min.time().replace(hour=19, minute=0, second=0)).replace(tzinfo=peru_tz)
        operaciones_despues_19h = Operacion.query.filter(
            Operacion.hora >= ayer_19h
        ).order_by(Operacion.hora.desc()).all()
        
        print(f"\n5. Operaciones después de las 19:00 de ayer ({ayer_19h}) - {len(operaciones_despues_19h)} operaciones:")
        for i, op in enumerate(operaciones_despues_19h, 1):
            usuario = Usuario.query.get(op.usuario_id)
            username = usuario.username if usuario else "N/A"
            print(f"   {i}. Hora: {op.hora} | Usuario: {username} | Monto: {op.monto}")

if __name__ == "__main__":
    verificar_usuarios_operaciones() 