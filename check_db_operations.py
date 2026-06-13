#!/usr/bin/env python3
"""Check database operations to verify data consistency."""

import sys
sys.path.insert(0, '/c/Users/LENOVO/sisagent')

from app_compatible_optimizado import app, db, Operacion, Sucursal, get_peru_time
from datetime import datetime, timedelta

with app.app_context():
    # Get today's date in Peru timezone
    hoy = get_peru_time().date()
    print(f"Today's date (Perú): {hoy}")
    print("=" * 60)

    # Query operations grouped by sucursal
    query = db.session.query(
        Sucursal.nombre,
        db.func.count(Operacion.id).label('count'),
        db.func.sum(Operacion.comision).label('total_comision')
    ).join(
        Operacion, Sucursal.id == Operacion.sucursal_id
    ).filter(
        db.func.date(Operacion.hora) == hoy
    ).group_by(
        Sucursal.id, Sucursal.nombre
    ).order_by(
        Sucursal.nombre
    )

    operations_by_branch = query.all()

    print("\nOPERATIONS BY BRANCH (today):")
    print("-" * 60)
    if not operations_by_branch:
        print("No operations found for today")
    else:
        for sucursal_nombre, count, total_comision in operations_by_branch:
            total_comision = float(total_comision) if total_comision else 0.0
            print(f"{sucursal_nombre:20} | Count: {count:3d} | Total Comisión: S/ {total_comision:8.2f}")

    print("\n" + "=" * 60)
    print("\nDETAILED OPERATIONS:")
    print("-" * 60)

    # Get all operations for today with details
    operations = db.session.query(Operacion).filter(
        db.func.date(Operacion.hora) == hoy
    ).order_by(Operacion.hora.desc()).limit(50).all()

    if not operations:
        print("No operations found")
    else:
        for op in operations:
            sucursal_name = op.sucursal.nombre if op.sucursal else "N/A"
            print(f"ID: {op.id:4d} | {sucursal_name:20} | Monto: S/ {op.monto:8.2f} | Comisión: S/ {op.comision:6.2f} | Medio: {op.medio:12} | Hora: {op.hora}")

    print("\n" + "=" * 60)
    print("\nCHECKING SPECIFIC BRANCHES:")
    print("-" * 60)

    # Check specific branches mentioned by user
    for branch_name in ["Santa Rosa", "La Unión"]:
        branch = db.session.query(Sucursal).filter_by(nombre=branch_name).first()
        if branch:
            ops = db.session.query(Operacion).filter(
                Operacion.sucursal_id == branch.id,
                db.func.date(Operacion.hora) == hoy
            ).all()
            total_comision = sum(float(o.comision) if o.comision else 0 for o in ops)
            print(f"\n{branch_name}:")
            print(f"  - Operations count: {len(ops)}")
            print(f"  - Total commission: S/ {total_comision:.2f}")
            if ops:
                for op in ops[:3]:  # Show first 3
                    print(f"    * Monto: S/ {op.monto}, Comisión: S/ {op.comision}, Medio: {op.medio}, Hora: {op.hora}")
        else:
            print(f"\n{branch_name}: Branch not found in database")
