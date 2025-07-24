from app import app, db, MedioPago

with app.app_context():
    print("=== ARREGLANDO ORDEN DE MEDIOS DE PAGO ===")
    
    # Obtener todos los medios activos
    medios = MedioPago.query.filter_by(activo=True).all()
    
    # Asignar orden secuencial
    for i, medio in enumerate(medios, 1):
        medio.orden = i
        print(f"Asignando orden {i} a {medio.nombre_abreviado}")
    
    # Guardar cambios
    db.session.commit()
    
    print(f"\nSe actualizaron {len(medios)} medios de pago")
    
    # Verificar resultado
    medios_ordenados = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden).all()
    print("\nMedios ordenados:")
    for medio in medios_ordenados:
        print(f"- {medio.nombre_abreviado} (orden: {medio.orden})")
    
    print("\n=== FIN ===") 