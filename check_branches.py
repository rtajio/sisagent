#!/usr/bin/env python3
"""Check all branches in the database."""

import sys
sys.path.insert(0, '/c/Users/LENOVO/sisagent')

from app_compatible_optimizado import app, db, Sucursal, Operacion, get_peru_time
from datetime import datetime

with app.app_context():
    hoy = get_peru_time().date()

    print("=" * 80)
    print("ALL BRANCHES IN DATABASE:")
    print("=" * 80)

    branches = db.session.query(Sucursal).order_by(Sucursal.nombre).all()

    for branch in branches:
        # Count operations for today
        ops_today = db.session.query(Operacion).filter(
            Operacion.sucursal_id == branch.id,
            db.func.date(Operacion.hora) == hoy
        ).all()

        comision_total = sum(float(o.comision) if o.comision else 0 for o in ops_today)

        status = "ACTIVA" if branch.activa else "INACTIVA"
        ops_count = len(ops_today)

        print(f"\nID: {branch.id:3d} | {branch.nombre:30} | {status:8} | Ops today: {ops_count:3d} | Comisión: S/ {comision_total:8.2f}")
        if branch.direccion:
            print(f"         Dirección: {branch.direccion}")

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print("-" * 80)

    # Get commission summary for all branches today
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
        db.func.sum(Operacion.comision).desc()
    )

    results = query.all()
    total_comision = 0

    for nombre, count, comision in results:
        comision_float = float(comision) if comision else 0.0
        total_comision += comision_float
        print(f"{nombre:30} | Operaciones: {count:3d} | Comisión: S/ {comision_float:8.2f}")

    print("-" * 80)
    print(f"{'TOTAL':30} | Comisión: S/ {total_comision:8.2f}")
    print("=" * 80)
