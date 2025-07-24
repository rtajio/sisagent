from app import app, db, MedioPago

with app.app_context():
    medios = MedioPago.query.order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    if not medios:
        print('No hay medios de pago en la base de datos.')
    else:
        print('Medios de pago en la base de datos:')
        for medio in medios:
            print(f"- {medio.nombre_abreviado} | {medio.nombre_completo} | Activo: {medio.activo}") 