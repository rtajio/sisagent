#!/usr/bin/env python3
"""
Punto de entrada para Gunicorn en Railway.
Importa la aplicación principal desde app_compatible_optimizado.py
"""

import os

from app_compatible_optimizado import app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
 