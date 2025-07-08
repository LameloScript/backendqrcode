#!/usr/bin/env python3
"""
WSGI Entry Point pour l'hébergement LWS
"""

import os
import sys

# Ajouter le répertoire de l'application au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_clean import create_app

# Créer l'application
application = create_app()

if __name__ == "__main__":
    application.run()