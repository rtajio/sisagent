import secrets
import string

def generar_secret_key():
    # Generar una clave secreta de 32 caracteres
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
    secret_key = ''.join(secrets.choice(caracteres) for _ in range(32))
    
    print("🔐 CLAVE SECRETA GENERADA")
    print("=" * 40)
    print(f"SECRET_KEY = {secret_key}")
    print("\n📋 INSTRUCCIONES:")
    print("1. Copia esta clave")
    print("2. Ve a Railway → Variables")
    print("3. Agrega: SECRET_KEY = [pega la clave aquí]")
    print("4. Guarda los cambios")
    
    return secret_key

if __name__ == "__main__":
    generar_secret_key() 