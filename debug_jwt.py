#!/usr/bin/env python3
"""
Script de debug pour analyser le problème JWT
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Ajout du path pour pouvoir importer nos modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app_clean import create_app
from flask_jwt_extended import create_access_token, decode_token
import jwt
import json

def analyze_jwt_issue():
    """Analyser le problème JWT"""
    
    print("=== ANALYSE DU PROBLÈME JWT ===\n")
    
    # 1. Créer l'application
    app = create_app()
    
    with app.app_context():
        print("1. Configuration JWT:")
        print(f"   JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')[:20]}...")
        print(f"   SECRET_KEY: {app.config.get('SECRET_KEY')[:20]}...")
        print(f"   JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")
        print(f"   JWT_ALGORITHM: {app.config.get('JWT_ALGORITHM', 'HS256')}")
        
        # 2. Créer un token de test
        print("\n2. Création d'un token de test:")
        try:
            test_token = create_access_token(identity=1)
            print(f"   Token créé: {test_token[:50]}...")
            
            # 3. Décoder le token sans vérification
            print("\n3. Décodage du token (sans vérification):")
            payload = jwt.decode(test_token, options={"verify_signature": False})
            print(f"   Payload: {json.dumps(payload, indent=4)}")
            
            # 4. Vérifier manuellement avec la clé secrète
            print("\n4. Vérification manuelle avec la clé secrète:")
            try:
                jwt_secret = app.config.get('JWT_SECRET_KEY')
                decoded = jwt.decode(test_token, jwt_secret, algorithms=['HS256'])
                print(f"   Décodage réussi: {decoded}")
            except jwt.ExpiredSignatureError as e:
                print(f"   Erreur d'expiration: {e}")
            except jwt.InvalidTokenError as e:
                print(f"   Erreur de token invalide: {e}")
            except Exception as e:
                print(f"   Erreur inattendue: {e}")
            
            # 5. Utiliser Flask-JWT-Extended pour vérifier
            print("\n5. Vérification avec Flask-JWT-Extended:")
            try:
                from flask_jwt_extended import decode_token
                decoded_flask = decode_token(test_token)
                print(f"   Décodage Flask-JWT réussi: {decoded_flask}")
            except Exception as e:
                print(f"   Erreur Flask-JWT: {e}")
                
        except Exception as e:
            print(f"   Erreur lors de la création du token: {e}")
            
        # 6. Vérifier la configuration Flask-JWT-Extended
        print("\n6. Configuration Flask-JWT-Extended:")
        from flask_jwt_extended import get_jwt_manager
        jwt_manager = get_jwt_manager()
        print(f"   JWT Manager: {jwt_manager}")
        
        # 7. Test avec un token réel de login
        print("\n7. Test avec un token réel de login:")
        from models import User
        
        # Chercher un utilisateur test
        user = User.query.filter_by(email='test@test.com').first()
        if user:
            print(f"   Utilisateur trouvé: {user.email}")
            real_token = create_access_token(identity=user.id)
            print(f"   Token réel: {real_token[:50]}...")
            
            # Test de décodage
            try:
                decoded_real = jwt.decode(real_token, app.config.get('JWT_SECRET_KEY'), algorithms=['HS256'])
                print(f"   Décodage réussi: {decoded_real}")
            except Exception as e:
                print(f"   Erreur décodage token réel: {e}")
        else:
            print("   Utilisateur test non trouvé")

if __name__ == "__main__":
    analyze_jwt_issue()