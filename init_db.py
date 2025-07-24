from app import app, db, Usuario
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()
    # Crear usuario admin si no existe
    admin = Usuario.query.filter_by(username='admin').first()
    if not admin:
        admin = Usuario(
            username='admin',
            email='admin@sisagent.com',
            password_hash=generate_password_hash('61442159'),
            nombre_completo='Administrador SISAGENT',
            es_admin=True,
            sucursal_id=None
        )
        db.session.add(admin)
        db.session.commit()
        print("¡Usuario admin creado!")
    else:
        print("El usuario admin ya existe.")
