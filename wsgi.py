#!/usr/bin/env python3
"""
WSGI Entry Point pour Railway et autres hébergeurs
"""

import os
import sys

# Ajouter le répertoire de l'application au chemin Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_clean import create_app
from models import db
import logging

# Créer l'application
application = create_app()
app = application  # Alias pour compatibilité

# Forcer la création des tables au démarrage
with application.app_context():
    try:
        db.create_all()
        logging.info("Tables créées avec succès dans wsgi.py")
    except Exception as e:
        logging.error(f"Erreur création tables dans wsgi.py: {e}")

if __name__ == "__main__":
    # Port pour Railway (utilise la variable d'environnement PORT)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 Démarrage du serveur sur {host}:{port}")
    application.run(host=host, port=port, debug=False)