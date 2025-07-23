#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
"""

from app import app, db, Usuario

def verificar_usuarios():
    """Verificar usuarios en la base de datos"""
    
    print("👥 VERIFICANDO USUARIOS EN LA BASE DE DATOS")
    print("=" * 40)
    
    with app.app_context():
        usuarios = Usuario.query.all()
        
        if usuarios:
            print(f"Total usuarios encontrados: {len(usuarios)}")
            print()
            
            for i, usuario in enumerate(usuarios, 1):
                print(f"{i}. Usuario: {usuario.username}")
                print(f"   - Email: {usuario.email}")
                print(f"   - Nombre: {usuario.nombre_completo}")
                print(f"   - Es admin: {usuario.es_admin}")
                print(f"   - Sucursal ID: {usuario.sucursal_id}")
                print(f"   - Activo: {usuario.activo}")
                print()
        else:
            print("❌ No se encontraron usuarios en la base de datos")
            return False
        
        return True

if __name__ == "__main__":
    verificar_usuarios() 