from app import app, db, MedioPago, Sucursal

with app.app_context():
    print("=== PRUEBA DE FUNCIÓN REPORTES() ===")
    
    # Simular la función reportes()
    try:
        medios_pago = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
        sucursales = Sucursal.query.all()
        
        print(f"✅ Medios obtenidos: {len(medios_pago)}")
        print(f"✅ Sucursales obtenidas: {len(sucursales)}")
        
        if medios_pago:
            print("\nMedios de pago:")
            for medio in medios_pago:
                print(f"  - {medio.nombre_abreviado} (orden: {medio.orden})")
        else:
            print("❌ No se obtuvieron medios de pago")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== FIN DE PRUEBA ===") 