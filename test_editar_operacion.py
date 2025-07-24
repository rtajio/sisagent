from app import app, db, MedioPago, Operacion

with app.app_context():
    print("=== PRUEBA FUNCIÓN EDITAR_OPERACION ===")
    
    try:
        # Simular la función editar_operacion
        medios_pago = MedioPago.query.filter_by(activo=True).order_by(MedioPago.orden, MedioPago.nombre_abreviado).all()
        
        print(f"✅ Medios obtenidos: {len(medios_pago)}")
        
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