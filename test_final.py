#!/usr/bin/env python3
"""Test final du backend nettoye"""
import requests
import time

def test_backend():
    print("Test du backend nettoye...")
    
    try:
        # Test health
        response = requests.get("http://127.0.0.1:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Health OK - Database: {data.get('database')}")
            
            # Test inscription rapide
            test_email = f"test_{int(time.time())}@example.com"
            reg_response = requests.post("http://127.0.0.1:5000/register", json={
                "email": test_email,
                "password": "test123456"
            })
            
            if reg_response.status_code == 201:
                print("Inscription OK")
                
                # Test connexion
                login_response = requests.post("http://127.0.0.1:5000/login", json={
                    "email": test_email,
                    "password": "test123456"
                })
                
                if login_response.status_code == 200:
                    print("Connexion OK")
                    print("BACKEND FONCTIONNEL!")
                    return True
        
        print("Tests echoues")
        return False
        
    except Exception as e:
        print(f"Serveur non demarre ou erreur: {e}")
        print("Demarrez avec: python app_clean.py")
        return False

if __name__ == "__main__":
    test_backend()