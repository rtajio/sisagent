#!/usr/bin/env python3
"""
Script de normalización de la BD PostgreSQL
PASO 1: Agregar FK medio_pago_id
PASO 2: Migrar datos
PASO 3: Normalizar nombres
PASO 4: Asignar medios globales a todas las sucursales
PASO 5: Eliminar columna medio original (opcional, después de verificar)
"""

import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:UaWirTbMaAasgXpeWkuHJzXmcBmJlVkV@sisagent-db.railway.internal:5432/railway'

from sqlalchemy import create_engine, text
import sys

db_url = os.environ['DATABASE_URL']
engine = create_engine(db_url)

def execute_step(step_num, description, sql_queries):
    """Ejecutar un paso de migración"""
    print(f"\n{'='*70}")
    print(f"PASO {step_num}: {description}")
    print(f"{'='*70}")
    
    try:
        with engine.connect() as conn:
            for query_name, query in sql_queries:
                print(f"\n  → {query_name}")
                result = conn.execute(text(query))
                conn.commit()
                
                # Mostrar resultado si es un SELECT
                if query.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    for row in rows:
                        print(f"    {dict(zip(result.keys(), row))}")
                else:
                    print(f"    ✓ Ejecutado")
        
        return True
    except Exception as e:
        print(f"  [!] ERROR: {e}")
        return False

# PASO 1: Agregar columna FK
step1_queries = [
    ("Verificar si columna ya existe", 
     "SELECT column_name FROM information_schema.columns WHERE table_name='operacion' AND column_name='medio_pago_id'"),
    
    ("Agregar columna medio_pago_id",
     """
     ALTER TABLE operacion 
     ADD COLUMN IF NOT EXISTS medio_pago_id INTEGER REFERENCES medio_pago(id)
     """),
    
    ("Contar operaciones totales",
     "SELECT COUNT(*) as operaciones FROM operacion"),
]

if not execute_step(1, "Agregar columna FK medio_pago_id", step1_queries):
    sys.exit(1)

# PASO 2: Migrar datos - mapear strings a IDs
step2_queries = [
    ("Ver medios únicos en operaciones",
     "SELECT DISTINCT medio FROM operacion ORDER BY medio"),
    
    ("Verificar correspondencias en medio_pago",
     """
     SELECT DISTINCT o.medio, m.id, m.nombre_abreviado, m.nombre_completo
     FROM operacion o
     LEFT JOIN medio_pago m ON 
       (UPPER(TRIM(o.medio)) = UPPER(TRIM(m.nombre_abreviado)) OR
        UPPER(TRIM(o.medio)) = UPPER(TRIM(m.nombre_completo)))
     ORDER BY o.medio
     """),
    
    ("Migrar datos: mapear medios a IDs",
     """
     UPDATE operacion o
     SET medio_pago_id = m.id
     FROM medio_pago m
     WHERE (UPPER(TRIM(o.medio)) = UPPER(TRIM(m.nombre_abreviado)) OR
            UPPER(TRIM(o.medio)) = UPPER(TRIM(m.nombre_completo)))
       AND o.medio_pago_id IS NULL
     """),
    
    ("Verificar operaciones migradas",
     "SELECT COUNT(*) as con_fk FROM operacion WHERE medio_pago_id IS NOT NULL"),
    
    ("Verificar operaciones SIN migrar",
     "SELECT COUNT(*) as sin_fk FROM operacion WHERE medio_pago_id IS NULL"),
]

if not execute_step(2, "Migrar datos (mapear strings a IDs)", step2_queries):
    print("  [!] Revisa los datos SIN MIGRAR arriba")
    sys.exit(1)

# PASO 3: Normalizar nombres en medio_pago
step3_queries = [
    ("Ver nombres actuales de medios",
     "SELECT id, nombre_abreviado, nombre_completo FROM medio_pago ORDER BY nombre_abreviado"),
    
    ("Normalizar: remover espacios extras y tabs",
     """
     UPDATE medio_pago 
     SET nombre_completo = TRIM(nombre_completo),
         nombre_abreviado = TRIM(UPPER(nombre_abreviado))
     """),
    
    ("Verificar después de normalizar",
     "SELECT id, nombre_abreviado, nombre_completo FROM medio_pago ORDER BY nombre_abreviado"),
]

if not execute_step(3, "Normalizar nombres en medio_pago", step3_queries):
    sys.exit(1)

# PASO 4: Asignar medios globales a todas las sucursales
step4_queries = [
    ("Listar medios SIN sucursal asignada",
     """
     SELECT m.id, m.nombre_abreviado, m.nombre_completo
     FROM medio_pago m
     WHERE m.id NOT IN (SELECT DISTINCT medio_pago_id FROM medio_sucursal)
     ORDER BY m.nombre_abreviado
     """),
    
    ("Asignar medios globales a TODAS las sucursales",
     """
     INSERT INTO medio_sucursal (sucursal_id, medio_pago_id, activo)
     SELECT s.id, m.id, true
     FROM sucursal s
     CROSS JOIN (
       SELECT id FROM medio_pago 
       WHERE id NOT IN (SELECT DISTINCT medio_pago_id FROM medio_sucursal)
     ) m
     WHERE NOT EXISTS (
       SELECT 1 FROM medio_sucursal 
       WHERE sucursal_id = s.id AND medio_pago_id = m.id
     )
     """),
    
    ("Verificar: contar asignaciones por medio",
     """
     SELECT m.nombre_abreviado, COUNT(ms.sucursal_id) as sucursales
     FROM medio_pago m
     LEFT JOIN medio_sucursal ms ON m.id = ms.medio_pago_id
     GROUP BY m.id, m.nombre_abreviado
     ORDER BY m.nombre_abreviado
     """),
]

if not execute_step(4, "Asignar medios globales a todas las sucursales", step4_queries):
    sys.exit(1)

# PASO 5: Resumen final (NO eliminamos la columna medio aún)
step5_queries = [
    ("Total operaciones con medio_pago_id asignado",
     "SELECT COUNT(*) as con_fk FROM operacion WHERE medio_pago_id IS NOT NULL"),
    
    ("Total operaciones sin FK",
     "SELECT COUNT(*) as sin_fk FROM operacion WHERE medio_pago_id IS NULL"),
    
    ("Medios de pago por sucursal (muestra)",
     """
     SELECT s.nombre, COUNT(ms.id) as medios_activos
     FROM sucursal s
     LEFT JOIN medio_sucursal ms ON s.id = ms.sucursal_id AND ms.activo = true
     GROUP BY s.id, s.nombre
     ORDER BY s.nombre
     """),
]

if not execute_step(5, "Resumen final", step5_queries):
    sys.exit(1)

print(f"\n{'='*70}")
print("[✓] NORMALIZACIÓN COMPLETADA EXITOSAMENTE")
print(f"{'='*70}")
print("\n[!] PRÓXIMOS PASOS:")
print("  1. Actualizar modelo Operacion en Python para usar FK")
print("  2. Limpiar caché de sesión")
print("  3. Probar la app")
print("  4. Si todo funciona, ELIMINAR columna 'medio' (opcional)")
print(f"{'='*70}")

