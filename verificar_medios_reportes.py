from app import app, db, MedioPago

with app.app_context():
    print("=== VERIFICACIÓN DE MEDIOS DE PAGO ===")
    
    # Verificar todos los medios
    todos_medios = MedioPago.query.all()
    print(f"Total de medios en la base de datos: {len(todos_medios)}")
    
    for medio in todos_medios:
        print(f"- ID: {medio.id} | Nombre: {medio.nombre_abreviado} | Completo: {medio.nombre_completo} | Activo: {medio.activo} | Orden: {medio.orden}")
    
    # Verificar medios activos (los que deberían aparecer en reportes)
    medios_activos = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    print(f"\nMedios activos (para reportes): {len(medios_activos)}")
    
    for medio in medios_activos:
        print(f"- {medio.nombre_abreviado} (orden: {medio.orden})")
    
    # Verificar si hay medios con orden 0 o nulo
    medios_sin_orden = MedioPago.query.filter((MedioPago.orden == 0) | (MedioPago.orden.is_(None))).all()
    if medios_sin_orden:
        print(f"\nMedios sin orden definido: {len(medios_sin_orden)}")
        for medio in medios_sin_orden:
            print(f"- {medio.nombre_abreviado}")
    
    print("\n=== FIN DE VERIFICACIÓN ===") 