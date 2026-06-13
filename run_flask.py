#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run Flask app with correct database."""
import os
import sys

# Set Flask environment
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_APP'] = 'app_compatible_optimizado.py'

# Import and run the app
from app_compatible_optimizado import app

if __name__ == '__main__':
    print("[*] Starting Flask app on port 5000...")
    app.run(debug=True, port=5000, use_reloader=False)
