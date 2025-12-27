#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar cambios y hacer deploy a Railway
"""
import subprocess
import sys
import os

def ejecutar_comando(comando, descripcion):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n{'='*70}")
    print(f"🔧 {descripcion}")
    print(f"{'='*70}")
    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        if resultado.stdout:
            print(resultado.stdout)
        if resultado.stderr:
            print("STDERR:", resultado.stderr)
        return resultado.returncode == 0
    except Exception as e:
        print(f"❌ Error ejecutando comando: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🚀 VERIFICACIÓN Y DEPLOY A RAILWAY")
    print("="*70)
    
    # Cambiar al directorio del proyecto
    os.chdir(r'C:\Users\LENOVO\sisagent')
    print(f"\n📁 Directorio de trabajo: {os.getcwd()}")
    
    # Verificar que la función API esté en el código
    print("\n🔍 Verificando que la función API esté en el código...")
    try:
        with open('app_compatible_optimizado.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            if "def api_actualizar_operacion" in contenido:
                print("✅ La función API está en el código")
            else:
                print("❌ ERROR: La función API NO está en el código")
                return False
    except Exception as e:
        print(f"❌ Error leyendo archivo: {e}")
        return False
    
    # Verificar estado de git
    print("\n📋 Verificando estado de git...")
    ejecutar_comando("git status", "Estado de git")
    
    # Verificar cambios sin commitear
    print("\n📦 Verificando cambios sin commitear...")
    ejecutar_comando("git diff --name-only", "Archivos modificados")
    
    # Verificar commits locales vs remotos
    print("\n🔍 Verificando commits locales vs remotos...")
    ejecutar_comando("git log --oneline -5", "Últimos 5 commits locales")
    ejecutar_comando("git log origin/main..HEAD --oneline", "Commits locales no pusheados")
    
    # Agregar cambios
    print("\n📦 Agregando cambios al staging...")
    if not ejecutar_comando("git add app_compatible_optimizado.py templates/operaciones.html", "Agregando archivos"):
        print("⚠️  Advertencia al agregar archivos")
    
    # Verificar qué se agregó
    ejecutar_comando("git status --short", "Estado después de agregar")
    
    # Hacer commit
    print("\n💾 Haciendo commit...")
    resultado_commit = ejecutar_comando(
        'git commit -m "FIX: agregar ruta API /api/operaciones/<id> PUT para edición de operaciones"',
        "Commit de cambios"
    )
    
    if not resultado_commit:
        print("⚠️  No se pudo hacer commit (puede que no haya cambios o ya estén commiteados)")
    
    # Verificar commits después del commit
    ejecutar_comando("git log --oneline -3", "Últimos commits después del commit")
    
    # Hacer push
    print("\n🚀 Haciendo push a GitHub (esto debería activar el deploy en Railway)...")
    resultado_push = ejecutar_comando("git push origin main", "Push a GitHub")
    
    if resultado_push:
        print("\n✅ PUSH EXITOSO")
        print("="*70)
        print("📦 Los cambios se han enviado a GitHub")
        print("🔄 Railway debería detectar los cambios y iniciar el deploy automáticamente")
        print("⏳ Por favor espera 2-5 minutos y verifica el dashboard de Railway")
        print("="*70)
    else:
        print("\n❌ ERROR EN EL PUSH")
        print("="*70)
        print("⚠️  No se pudo hacer push. Verifica:")
        print("   1. Que tengas conexión a internet")
        print("   2. Que tengas permisos para hacer push al repositorio")
        print("   3. Que el repositorio remoto esté configurado correctamente")
        print("="*70)
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        input("\nPresiona Enter para salir...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)

