#!/usr/bin/env python3
"""
Test simple JWT pour identifier le problème
"""

import os
import sys
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajout du path pour pouvoir importer nos modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_clean import create_app

def test_jwt_simple():
    """Test simple de JWT"""
    
    print("=== TEST JWT SIMPLE ===\n")
    
    # Créer l'application
    app = create_app()
    
    with app.app_context():
        # Vérifier la configuration
        jwt_secret = app.config.get('JWT_SECRET_KEY')
        print(f"JWT Secret: {jwt_secret[:20]}...")
        
        # Tester création manuelle d'un token
        payload = {
            'sub': '7',  # User ID as string
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }
        
        # Créer le token manuellement
        manual_token = jwt.encode(payload, jwt_secret, algorithm='HS256')
        print(f"Token manuel créé: {manual_token[:50]}...")
        
        # Tester décodage
        try:
            decoded = jwt.decode(manual_token, jwt_secret, algorithms=['HS256'])
            print(f"Décodage réussi: {decoded}")
        except Exception as e:
            print(f"Erreur décodage: {e}")
        
        # Tester avec Flask-JWT-Extended
        print("\n--- Test avec Flask-JWT-Extended ---")
        from flask_jwt_extended import create_access_token, decode_token
        
        # Créer token avec Flask-JWT-Extended
        flask_token = create_access_token(identity='7')
        print(f"Token Flask-JWT: {flask_token[:50]}...")
        
        # Décoder avec JWT standard
        try:
            decoded_flask = jwt.decode(flask_token, jwt_secret, algorithms=['HS256'])
            print(f"Décodage token Flask-JWT avec jwt standard: {decoded_flask}")
        except Exception as e:
            print(f"Erreur décodage Flask-JWT avec jwt standard: {e}")
        
        # Décoder avec Flask-JWT-Extended
        try:
            decoded_flask_native = decode_token(flask_token)
            print(f"Décodage token Flask-JWT avec Flask-JWT-Extended: {decoded_flask_native}")
        except Exception as e:
            print(f"Erreur décodage Flask-JWT avec Flask-JWT-Extended: {e}")
        
        # Tester avec un vrai token reçu du serveur
        print("\n--- Test avec token serveur ---")
        real_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1MjA1MDg3OSwianRpIjoiOGM0NDIwOWItZjhjMC00YzFkLWE1ZmQtY2MzODE0MjA1Mzg0IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6NywibmJmIjoxNzUyMDUwODc5LCJjc3JmIjoiZTRiMWEyODAtOTMyNS00ZGY5LTk5NmYtM2YzYmM5ODRlOGE1IiwiZXhwIjoxNzUyMDUxNzc5fQ.bp54x8HBYPQhHKOpBajuYTvvLhKeM_DPd1fmWqh5vnI"
        
        # Décoder sans vérification
        try:
            payload_real = jwt.decode(real_token, options={"verify_signature": False})
            print(f"Payload token serveur: {payload_real}")
        except Exception as e:
            print(f"Erreur payload: {e}")
        
        # Décoder avec vérification
        try:
            decoded_real = jwt.decode(real_token, jwt_secret, algorithms=['HS256'])
            print(f"Décodage token serveur avec jwt standard: {decoded_real}")
        except Exception as e:
            print(f"Erreur décodage token serveur avec jwt standard: {e}")
        
        # Décoder avec Flask-JWT-Extended
        try:
            decoded_real_flask = decode_token(real_token)
            print(f"Décodage token serveur avec Flask-JWT-Extended: {decoded_real_flask}")
        except Exception as e:
            print(f"Erreur décodage token serveur avec Flask-JWT-Extended: {e}")

if __name__ == "__main__":
    test_jwt_simple()