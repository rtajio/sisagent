#!/usr/bin/env python3
"""
Script para diagnosticar operaciones recientes
"""

import os
import sys
from datetime import datetime, timedelta
import pytz

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, Operacion, Usuario

def diagnosticar_operacion_reciente():
    """Diagnosticar operaciones recientes"""
    with app.app_context():
        try:
            print("🔍 DIAGNÓSTICO DE OPERACIONES RECIENTES")
            print("=" * 60)
            
            # Buscar el usuario 73800418
            usuario = Usuario.query.filter_by(username='73800418').first()
            if not usuario:
                print("❌ Usuario 73800418 no encontrado")
                return
            
            print(f"✅ Usuario 73800418: ID={usuario.id}, Nombre={usuario.nombre_completo}")
            
            # Operaciones de las últimas 2 horas
            peru_tz = pytz.timezone('America/Lima')
            hace_2_horas = datetime.now(peru_tz) - timedelta(hours=2)
            
            operaciones_recientes = Operacion.query.filter(
                Operacion.hora >= hace_2_horas
            ).order_by(Operacion.hora.desc()).all()
            
            print(f"\n🕐 Operaciones de las últimas 2 horas ({len(operaciones_recientes)}):")
            for op in operaciones_recientes:
                usuario_op = Usuario.query.get(op.usuario_id)
                print(f"  - ID: {op.id}, Monto: {op.monto}, Usuario: {usuario_op.username if usuario_op else 'N/A'}, Hora: {op.hora}")
            
            # Operaciones específicas del usuario 73800418
            operaciones_usuario = Operacion.query.filter_by(
                usuario_id=usuario.id
            ).order_by(Operacion.hora.desc()).limit(10).all()
            
            print(f"\n👤 Últimas 10 operaciones del usuario 73800418 ({len(operaciones_usuario)}):")
            for op in operaciones_usuario:
                print(f"  - ID: {op.id}, Monto: {op.monto}, Comisión: {op.comision}, Hora: {op.hora}")
            
            # Verificar si hay operaciones con usuario_id incorrecto
            print(f"\n🔍 VERIFICANDO OPERACIONES CON USUARIO_ID INCORRECTO:")
            todas_operaciones = Operacion.query.order_by(Operacion.hora.desc()).limit(20).all()
            
            for op in todas_operaciones:
                usuario_op = Usuario.query.get(op.usuario_id)
                if usuario_op and usuario_op.username == '73800418':
                    print(f"  ✅ Operación {op.id} pertenece al usuario 73800418")
                elif usuario_op:
                    print(f"  ❌ Operación {op.id} pertenece al usuario {usuario_op.username}")
                else:
                    print(f"  ⚠️  Operación {op.id} tiene usuario_id inválido: {op.usuario_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == "__main__":
    diagnosticar_operacion_reciente() 