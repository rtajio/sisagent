#!/usr/bin/env python3
"""Backup de la base de datos PostgreSQL"""

import json
import os
from datetime import datetime

# Importar la app y BD
from app_compatible_optimizado import app, db

backup_dir = "backups"
os.makedirs(backup_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(backup_dir, f"sisagent_backup_{timestamp}.json")

print(f"[*] Creando backup de la BD PostgreSQL...")

with app.app_context():
    backup_data = {}
    total_rows = 0

    # Obtener todas las tablas
    from sqlalchemy import inspect
    inspector = inspect(db.engine)

    for table_name in sorted(inspector.get_table_names()):
        print(f"  - Exportando: {table_name}")

        # Query directo para obtener todos los datos
        result = db.session.execute(db.text(f"SELECT * FROM {table_name}"))
        columns = [col[0] for col in result.description] if result.description else []
        rows = result.fetchall()

        backup_data[table_name] = {
            "columns": columns,
            "row_count": len(rows),
            "rows": [dict(zip(columns, [str(v) if v is not None else None for v in row])) for row in rows]
        }
        total_rows += len(rows)

    # Guardar backup JSON
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2)

    size_mb = os.path.getsize(backup_file) / (1024*1024)

    print(f"\n{'='*60}")
    print(f"[✓] BACKUP CREADO EXITOSAMENTE")
    print(f"{'='*60}")
    print(f"Archivo: {backup_file}")
    print(f"Tamaño:  {size_mb:.2f} MB")
    print(f"Filas:   {total_rows}")
    print(f"Tablas:  {len(backup_data)}")
    print(f"\n[!] GUARDA ESTE ARCHIVO EN UN LUGAR SEGURO")
    print(f"{'='*60}")
