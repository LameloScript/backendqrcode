#!/usr/bin/env python3
"""
Script de test pour vérifier la configuration Railway
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_local_server():
    """Tester le serveur local"""
    print("🧪 Test du serveur local...")
    
    try:
        # Tester le health check
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check OK: {data['status']}")
            print(f"📊 Database: {data['database']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur connexion: {e}")
        return False

def test_production_server():
    """Tester le serveur de production Railway"""
    print("🚀 Test du serveur Railway...")
    
    base_url = os.getenv('BASE_URL', 'https://backendqrcode-production.up.railway.app')
    
    try:
        # Tester le health check
        response = requests.get(f'{base_url}/health', timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Railway health check OK: {data['status']}")
            print(f"📊 Database: {data['database']}")
            return True
        else:
            print(f"❌ Railway health check failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur connexion Railway: {e}")
        return False

def check_environment():
    """Vérifier les variables d'environnement"""
    print("🔧 Vérification des variables d'environnement...")
    
    required_vars = ['SECRET_KEY', 'JWT_SECRET_KEY']
    optional_vars = ['FLASK_ENV', 'BASE_URL', 'CORS_ORIGINS']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10)}")
        else:
            print(f"❌ {var}: MANQUANT")
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"ℹ️  {var}: {value}")
        else:
            print(f"⚠️  {var}: Non défini")

def main():
    """Fonction principale"""
    print("🔍 Test de configuration Railway")
    print("=" * 40)
    
    # Vérifier l'environnement
    check_environment()
    print()
    
    # Tester le serveur de production
    if test_production_server():
        print("\n🎉 Le serveur Railway fonctionne correctement !")
    else:
        print("\n💥 Problème avec le serveur Railway")
        
        # Suggestions de dépannage
        print("\n🛠️  Suggestions de dépannage:")
        print("1. Vérifiez que le déploiement Railway est terminé")
        print("2. Consultez les logs Railway pour plus de détails")
        print("3. Vérifiez que toutes les variables d'environnement sont définies")
        print("4. Assurez-vous que le port est correctement configuré")

if __name__ == '__main__':
    main()