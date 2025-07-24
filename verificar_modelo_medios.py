from app import app, db, MedioPago

with app.app_context():
    print("=== VERIFICANDO MODELO MEDIOPAGO ===")
    
    try:
        # Verificar si el modelo existe
        print("1. Verificando si MedioPago está disponible...")
        print(f"MedioPago: {MedioPago}")
        
        # Verificar si la tabla existe
        print("2. Verificando si la tabla existe...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tablas disponibles: {tables}")
        
        if 'medio_pago' in tables:
            print("✅ Tabla medio_pago existe")
        else:
            print("❌ Tabla medio_pago NO existe")
        
        # Intentar hacer una consulta
        print("3. Intentando consulta...")
        medios = MedioPago.query.all()
        print(f"Medios en la base de datos: {len(medios)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=== FIN VERIFICACIÓN ===") 