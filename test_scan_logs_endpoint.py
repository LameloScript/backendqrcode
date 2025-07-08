#!/usr/bin/env python3
"""
Test script pour l'endpoint de récupération des logs de scan
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:5000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

def register_and_login():
    """Créer un compte de test et se connecter"""
    print("=== Inscription et connexion ===")
    
    # Inscription
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    print(f"Inscription: {response.status_code}")
    
    # Connexion
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"Connexion réussie, token obtenu")
        return token
    else:
        print(f"Erreur connexion: {response.status_code} - {response.text}")
        return None

def create_test_qr_code(token):
    """Créer un QR code de test"""
    print("\n=== Création QR code de test ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    qr_data = {
        "type": "url",
        "data": "https://example.com",
        "color": "#000000",
        "backgroundColor": "#ffffff",
        "size": 256,
        "expiresAt": "2024-12-31T23:59:59Z",
        "validityDuration": "1 year"
    }
    
    response = requests.post(f"{BASE_URL}/qr-codes", json=qr_data, headers=headers)
    if response.status_code == 201:
        data = response.json()
        qr_id = data.get('id')
        print(f"QR code créé: {qr_id}")
        return qr_id
    else:
        print(f"Erreur création QR: {response.status_code} - {response.text}")
        return None

def test_scan_logs_endpoint(token, qr_id):
    """Tester l'endpoint des logs de scan"""
    print(f"\n=== Test endpoint scan logs pour QR: {qr_id} ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Récupérer les logs sans pagination
    print("\n1. Test récupération logs de base:")
    response = requests.get(f"{BASE_URL}/qr-codes/{qr_id}/scan-logs", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"QR Code ID: {data.get('qr_code_id')}")
        print(f"Nombre de logs: {len(data.get('scan_logs', []))}")
        print(f"Total scans: {data.get('summary', {}).get('total_scans', 0)}")
        print(f"Total logs: {data.get('summary', {}).get('total_logs', 0)}")
        
        # Afficher les détails de pagination
        pagination = data.get('pagination', {})
        print(f"Pagination - Page: {pagination.get('page')}, Par page: {pagination.get('per_page')}")
        print(f"Total pages: {pagination.get('pages')}, Total items: {pagination.get('total')}")
    else:
        print(f"Erreur: {response.text}")
    
    # Test 2: Test avec pagination
    print("\n2. Test avec pagination:")
    response = requests.get(f"{BASE_URL}/qr-codes/{qr_id}/scan-logs?page=1&per_page=10", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Logs récupérés: {len(data.get('scan_logs', []))}")
        
        # Afficher un exemple de log si disponible
        logs = data.get('scan_logs', [])
        if logs:
            print(f"Exemple de log:")
            example_log = logs[0]
            print(f"  - ID: {example_log.get('id')}")
            print(f"  - Timestamp: {example_log.get('timestamp')}")
            print(f"  - Device type: {example_log.get('device_type')}")
            print(f"  - IP: {example_log.get('ip_address')}")
        else:
            print("Aucun log disponible (normal pour un nouveau QR code)")
    else:
        print(f"Erreur: {response.text}")
    
    # Test 3: Test avec QR code inexistant
    print("\n3. Test avec QR code inexistant:")
    fake_qr_id = "fake-qr-id-123"
    response = requests.get(f"{BASE_URL}/qr-codes/{fake_qr_id}/scan-logs", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print("✓ Erreur 404 correctement retournée pour QR inexistant")
    else:
        print(f"Erreur inattendue: {response.text}")

def test_without_auth(qr_id):
    """Tester l'endpoint sans authentification"""
    print(f"\n=== Test sans authentification ===")
    
    response = requests.get(f"{BASE_URL}/qr-codes/{qr_id}/scan-logs")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✓ Erreur 401 correctement retournée sans token")
    else:
        print(f"Erreur inattendue: {response.text}")

def main():
    """Fonction principale de test"""
    print("Test de l'endpoint GET /qr-codes/{qr_id}/scan-logs")
    print("=" * 50)
    
    # Vérifier que le serveur est en marche
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Serveur non accessible - assurez-vous qu'il est démarré")
            return
        print("✓ Serveur accessible")
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("Assurez-vous que le serveur Flask est démarré sur http://127.0.0.1:5000")
        return
    
    # Tests avec authentification
    token = register_and_login()
    if not token:
        print("❌ Impossible de se connecter")
        return
    
    qr_id = create_test_qr_code(token)
    if not qr_id:
        print("❌ Impossible de créer un QR code")
        return
    
    test_scan_logs_endpoint(token, qr_id)
    test_without_auth(qr_id)
    
    print("\n" + "=" * 50)
    print("Tests terminés!")

if __name__ == "__main__":
    main()