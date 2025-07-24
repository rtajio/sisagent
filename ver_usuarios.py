from app import app, db, Operacion, Usuario

with app.app_context():
    print('Usuarios:')
    for u in Usuario.query.all():
        print(f'ID: {u.id}, Usuario: {u.username}, es_admin: {u.es_admin}')
    print('\nOperaciones:')
    for op in Operacion.query.order_by(Operacion.hora.desc()).all():
        usuario = Usuario.query.get(op.usuario_id)
        print(f'Operacion ID: {op.id}, usuario_id: {op.usuario_id}, usuario: {usuario.username if usuario else "N/A"}') 