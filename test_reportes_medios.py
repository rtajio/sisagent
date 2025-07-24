from app import app, db, MedioPago, Sucursal

with app.app_context():
    print("=== SIMULANDO FUNCIÓN REPORTES() ===")
    
    # Simular exactamente la consulta de la función reportes()
    medios_pago = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
    
    print(f"Medios obtenidos: {len(medios_pago)}")
    
    if medios_pago:
        print("Lista de medios:")
        for medio in medios_pago:
            print(f"- {medio.nombre_abreviado} (ID: {medio.id}, Orden: {medio.orden}, Activo: {medio.activo})")
    else:
        print("❌ No se obtuvieron medios")
    
    # Verificar también las sucursales
    sucursales = Sucursal.query.all()
    print(f"\nSucursales obtenidas: {len(sucursales)}")
    
    print("\n=== FIN DE SIMULACIÓN ===") 