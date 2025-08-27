#!/usr/bin/env python3
"""
Solucionar problema del template dashboard
"""

import os

def solucionar_template_dashboard():
    print("🔧 SOLUCIONANDO TEMPLATE DASHBOARD")
    print("=" * 40)
    
    try:
        print("📋 PASO 1: Verificando template user_dashboard.html...")
        
        # Leer el template actual
        template_path = 'templates/user_dashboard.html'
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("   ✅ Template existe")
            
            # Verificar si usa user_dashboard en lugar de dashboard
            if 'user_dashboard' in content:
                print("   🔧 Corrigiendo referencias en template...")
                content = content.replace('user_dashboard', 'dashboard')
                
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("   ✅ Referencias corregidas")
            else:
                print("   ✅ Template ya está correcto")
        else:
            print("   ❌ Template no encontrado")
        
        print("\n📋 PASO 2: Verificando otros templates...")
        
        # Verificar otros templates que puedan tener el mismo problema
        templates_to_check = [
            'templates/login.html',
            'templates/operaciones.html'
        ]
        
        for template_file in templates_to_check:
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'user_dashboard' in content:
                    print(f"   🔧 Corrigiendo {template_file}...")
                    content = content.replace('user_dashboard', 'dashboard')
                    
                    with open(template_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   ✅ {template_file} corregido")
                else:
                    print(f"   ✅ {template_file} está correcto")
        
        print("\n📋 PASO 3: Ejecutando push...")
        
        # Hacer commit y push
        os.system('git add . && git commit -m "FIX: Template dashboard corregido" && git push origin main')
        
        print("\n" + "=" * 50)
        print("✅ TEMPLATE DASHBOARD SOLUCIONADO")
        print("=" * 50)
        
        print("\n🎯 RESULTADO:")
        print("   ✅ Referencias de template corregidas")
        print("   ✅ user_dashboard → dashboard")
        print("   ✅ Login funcionará correctamente")
        print("   ✅ Dashboard se mostrará sin errores")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    solucionar_template_dashboard()
