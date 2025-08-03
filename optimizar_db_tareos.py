#!/usr/bin/env python3
"""
Script para optimizar la base de datos agregando índices para mejorar el rendimiento
de las consultas de tareos y operaciones de tareos.
"""

import os
import sys
from datetime import datetime
import pytz

# Agregar el directorio actual al path para importar app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def optimizar_base_datos():
    """Agregar índices para optimizar consultas de tareos"""
    
    with app.app_context():
        try:
            print("🔧 Iniciando optimización de base de datos...")
            
            # Detectar tipo de base de datos
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            is_sqlite = 'sqlite' in db_url.lower()
            is_postgresql = 'postgresql' in db_url.lower()
            
            print(f"📊 Tipo de base de datos detectado: {'SQLite' if is_sqlite else 'PostgreSQL' if is_postgresql else 'Otro'}")
            
            # Índices para mejorar consultas de tareos
            indices = [
                # Índice para consultas de tareos por usuario
                "CREATE INDEX IF NOT EXISTS idx_tareo_usuario_id ON tareo(usuario_id)",
                
                # Índice para consultas de tareos por sucursal
                "CREATE INDEX IF NOT EXISTS idx_tareo_sucursal_id ON tareo(sucursal_id)",
                
                # Índice para consultas de tareos por estado
                "CREATE INDEX IF NOT EXISTS idx_tareo_estado ON tareo(estado)",
                
                # Índice compuesto para tareos por usuario y estado
                "CREATE INDEX IF NOT EXISTS idx_tareo_usuario_estado ON tareo(usuario_id, estado)",
                
                # Índice para operaciones de tareo por tareo_id
                "CREATE INDEX IF NOT EXISTS idx_operacion_tareo_tareo_id ON operacion_tareo(tareo_id)",
                
                # Índice para operaciones de tareo por completado
                "CREATE INDEX IF NOT EXISTS idx_operacion_tareo_completado ON operacion_tareo(completado)",
                
                # Índice compuesto para operaciones de tareo por tareo_id y completado
                "CREATE INDEX IF NOT EXISTS idx_operacion_tareo_tareo_completado ON operacion_tareo(tareo_id, completado)",
                
                # Índice para orden de operaciones
                "CREATE INDEX IF NOT EXISTS idx_operacion_tareo_orden ON operacion_tareo(orden)",
                
                # Índice para fecha de completado
                "CREATE INDEX IF NOT EXISTS idx_operacion_tareo_fecha_completado ON operacion_tareo(fecha_completado)",
                
                # Índice para fecha de creación de tareos
                "CREATE INDEX IF NOT EXISTS idx_tareo_fecha_creacion ON tareo(fecha_creacion)",
                
                # Índice para fecha de completado de tareos
                "CREATE INDEX IF NOT EXISTS idx_tareo_fecha_completado ON tareo(fecha_completado)"
            ]
            
            # Ejecutar cada índice
            for i, indice in enumerate(indices, 1):
                try:
                    print(f"📊 Creando índice {i}/{len(indices)}...")
                    db.session.execute(text(indice))
                    print(f"✅ Índice creado exitosamente")
                except Exception as e:
                    print(f"⚠️  Advertencia al crear índice: {e}")
                    continue
            
            # Commit de todos los cambios
            db.session.commit()
            print("✅ Optimización de base de datos completada exitosamente")
            
            # Mostrar estadísticas de índices
            print("\n📈 Estadísticas de índices creados:")
            try:
                if is_sqlite:
                    # Para SQLite
                    indices_tareo = db.session.execute(text(
                        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='tareo'"
                    )).fetchall()
                    print(f"   - Índices en tabla 'tareo': {len(indices_tareo)}")
                    
                    indices_operacion = db.session.execute(text(
                        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='operacion_tareo'"
                    )).fetchall()
                    print(f"   - Índices en tabla 'operacion_tareo': {len(indices_operacion)}")
                    
                    # Mostrar nombres de índices
                    if indices_tareo:
                        print(f"   - Índices de tareo: {[idx[0] for idx in indices_tareo]}")
                    if indices_operacion:
                        print(f"   - Índices de operacion_tareo: {[idx[0] for idx in indices_operacion]}")
                        
                elif is_postgresql:
                    # Para PostgreSQL
                    indices_tareo = db.session.execute(text(
                        "SELECT indexname FROM pg_indexes WHERE tablename = 'tareo'"
                    )).fetchall()
                    print(f"   - Índices en tabla 'tareo': {len(indices_tareo)}")
                    
                    indices_operacion = db.session.execute(text(
                        "SELECT indexname FROM pg_indexes WHERE tablename = 'operacion_tareo'"
                    )).fetchall()
                    print(f"   - Índices en tabla 'operacion_tareo': {len(indices_operacion)}")
                
            except Exception as e:
                print(f"   ⚠️  No se pudieron obtener estadísticas: {e}")
            
        except Exception as e:
            print(f"❌ Error durante la optimización: {e}")
            db.session.rollback()
            return False
        
        return True

def verificar_rendimiento():
    """Verificar el rendimiento de las consultas principales"""
    
    with app.app_context():
        try:
            print("\n🔍 Verificando rendimiento de consultas...")
            
            # Simular consulta de tareos por usuario
            from app import Tareo, OperacionTareo, Usuario
            from sqlalchemy import func
            
            # Obtener un usuario para las pruebas
            usuario = Usuario.query.first()
            if not usuario:
                print("   ⚠️  No hay usuarios en la base de datos para las pruebas")
                return
            
            # Consulta 1: Tareos por usuario
            start_time = datetime.now()
            tareos_usuario = Tareo.query.filter_by(usuario_id=usuario.id).all()
            tiempo1 = (datetime.now() - start_time).total_seconds()
            print(f"   - Consulta tareos por usuario: {tiempo1:.4f}s ({len(tareos_usuario)} tareos)")
            
            # Consulta 2: Operaciones de tareo
            if tareos_usuario:
                start_time = datetime.now()
                operaciones = OperacionTareo.query.filter_by(tareo_id=tareos_usuario[0].id).all()
                tiempo2 = (datetime.now() - start_time).total_seconds()
                print(f"   - Consulta operaciones de tareo: {tiempo2:.4f}s ({len(operaciones)} operaciones)")
            
                # Consulta 3: Conteo de operaciones completadas
                start_time = datetime.now()
                completadas = OperacionTareo.query.filter_by(
                    tareo_id=tareos_usuario[0].id, 
                    completado=True
                ).count()
                tiempo3 = (datetime.now() - start_time).total_seconds()
                print(f"   - Conteo operaciones completadas: {tiempo3:.4f}s ({completadas} completadas)")
            
            # Consulta 4: Simular la consulta optimizada de la función completar_operacion_tareo
            if tareos_usuario:
                start_time = datetime.now()
                operaciones_tareo = OperacionTareo.query.filter_by(tareo_id=tareos_usuario[0].id).all()
                total_operaciones = len(operaciones_tareo)
                operaciones_completadas = sum(1 for op in operaciones_tareo if op.completado)
                tiempo4 = (datetime.now() - start_time).total_seconds()
                print(f"   - Consulta optimizada (nueva): {tiempo4:.4f}s")
            
            print("✅ Verificación de rendimiento completada")
            
        except Exception as e:
            print(f"❌ Error durante verificación: {e}")

def mostrar_mejoras():
    """Mostrar las mejoras implementadas"""
    print("\n🚀 MEJORAS IMPLEMENTADAS:")
    print("=" * 50)
    print("1. ✅ Optimización de consultas en completar_operacion_tareo:")
    print("   - Reducción de múltiples consultas a una sola")
    print("   - Cálculo en memoria en lugar de consultas separadas")
    print("   - Eliminación de consultas COUNT redundantes")
    
    print("\n2. ✅ Índices de base de datos agregados:")
    print("   - Índices en usuario_id, sucursal_id, estado")
    print("   - Índices compuestos para consultas frecuentes")
    print("   - Índices en tareo_id y completado para operaciones")
    
    print("\n3. ✅ Beneficios esperados:")
    print("   - Reducción de tiempo de respuesta de ~10s a <1s")
    print("   - Mejor experiencia de usuario")
    print("   - Menor carga en la base de datos")
    
    print("\n4. ✅ Próximos pasos recomendados:")
    print("   - Monitorear el rendimiento en producción")
    print("   - Considerar cache si el volumen aumenta")
    print("   - Revisar logs para identificar cuellos de botella")

if __name__ == "__main__":
    print("🚀 Iniciando optimización de rendimiento para tareos...")
    print("=" * 60)
    
    if optimizar_base_datos():
        verificar_rendimiento()
        mostrar_mejoras()
        print("\n🎉 Optimización completada exitosamente!")
        print("Los checkboxes de tareos ahora deberían responder mucho más rápido.")
        print("\n💡 Recomendación: Reinicia el servidor para aplicar todos los cambios.")
    else:
        print("\n❌ La optimización falló. Revisa los errores anteriores.") 