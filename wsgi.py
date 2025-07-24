import os
from app import app, db

# Crear las tablas de la base de datos
with app.app_context():
    db.create_all()
    
    # Crear usuario admin por defecto si no existe
    from app import Usuario
    from werkzeug.security import generate_password_hash
    
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

if __name__ == "__main__":
    app.run() 