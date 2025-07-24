from app import app, db, Operacion, Sucursal
from datetime import datetime
from sqlalchemy import extract

with app.app_context():
    hoy = datetime.now()
    mes_actual = hoy.month
    año_actual = hoy.year
    print("Operaciones del mes actual:")
    operaciones = db.session.query(Operacion).filter(
        extract('month', Operacion.hora) == mes_actual,
        extract('year', Operacion.hora) == año_actual
    ).all()
    for op in operaciones:
        sucursal = Sucursal.query.get(op.sucursal_id)
        print(f"ID: {op.id}, Fecha: {op.hora}, Comisión: {op.comision}, Sucursal: {sucursal.nombre if sucursal else 'N/A'}")
    if not operaciones:
        print("No hay operaciones este mes.") 