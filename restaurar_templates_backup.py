#!/usr/bin/env python3
"""
Restaurar templates desde backup del 24/08 preservando rutas actuales y BD
"""

import os
import shutil
from datetime import datetime

BACKUP_DIR = 'backup_pre_vouchers_20250824_131706/templates'
TARGET_DIR = 'templates'
RESPALDO_DIR = f'backups/templates_respaldo_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

REEMPLAZOS = {
    'user_dashboard': 'dashboard',
    'admin_dashboard': 'dashboard',
    'tareos_usuario': 'operaciones',
    'admin_sucursales': 'operaciones',
    'admin_usuarios': 'operaciones',
    'admin_medios': 'operaciones',
    'admin_tareos': 'operaciones',
    'registrar_operacion': 'operaciones'
}

EXCLUIR = set(['login.html'])


def aplicar_reemplazos(path):
    with open(path, 'r', encoding='utf-8') as f:
        contenido = f.read()
    for viejo, nuevo in REEMPLAZOS.items():
        contenido = contenido.replace(viejo, nuevo)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(contenido)


def main():
    os.makedirs('backups', exist_ok=True)
    os.makedirs(RESPALDO_DIR, exist_ok=True)

    if not os.path.isdir(BACKUP_DIR):
        print('❌ No se encontró el directorio de backup.\nAsegúrate de tener backup_pre_vouchers_20250824_131706/templates')
        return 1

    # Respaldar templates actuales
    if os.path.isdir(TARGET_DIR):
        shutil.copytree(TARGET_DIR, os.path.join(RESPALDO_DIR, 'templates'))
        print(f'✅ Respaldo creado en {RESPALDO_DIR}')

    # Restaurar desde backup, aplicando reemplazos
    for root, _, files in os.walk(BACKUP_DIR):
        for file in files:
            if not file.endswith('.html'):
                continue
            if file in EXCLUIR:
                continue
            src = os.path.join(root, file)
            rel = os.path.relpath(src, BACKUP_DIR)
            dst = os.path.join(TARGET_DIR, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            aplicar_reemplazos(dst)
            print(f'🔧 Restaurado {rel}')

    print('✅ Restauración de templates completada')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
