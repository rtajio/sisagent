from app import app, db, MedioPago

with app.app_context():
    print("=== MEDIOS DE PAGO EN LA BASE DE DATOS ===")
    
    try:
        medios = MedioPago.query.all()
        print(f"Total de medios: {len(medios)}")
        
        for medio in medios:
            print(f"ID: {medio.id} | Nombre: {medio.nombre_abreviado} | Completo: {medio.nombre_completo} | Activo: {medio.activo} | Orden: {medio.orden}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== FIN ===") 