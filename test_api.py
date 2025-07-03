#!/usr/bin/env python3
"""
Simple API test script for the QR Code Analytics Backend
"""

import requests
import json
import sys

# Configuration
BASE_URL = 'http://127.0.0.1:5000'

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            return True
        else:
            print(f"❌ Health check: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Health check: FAILED (Connection refused - is the server running?)")
        return False
    except Exception as e:
        print(f"❌ Health check: FAILED ({str(e)})")
        return False

def test_user_registration():
    """Test user registration"""
    try:
        test_user = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = requests.post(f'{BASE_URL}/register', json=test_user)
        
        if response.status_code == 201:
            print("✅ User registration: PASSED")
            return True
        elif response.status_code == 400 and 'déjà existant' in response.json().get('error', ''):
            print("✅ User registration: PASSED (User already exists)")
            return True
        else:
            print(f"❌ User registration: FAILED (Status: {response.status_code}, Response: {response.text})")
            return False
    except Exception as e:
        print(f"❌ User registration: FAILED ({str(e)})")
        return False

def test_user_login():
    """Test user login"""
    try:
        test_user = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = requests.post(f'{BASE_URL}/login', json=test_user)
        
        if response.status_code == 200:
            print("✅ User login: PASSED")
            return response.json().get('user_id')
        else:
            print(f"❌ User login: FAILED (Status: {response.status_code}, Response: {response.text})")
            return None
    except Exception as e:
        print(f"❌ User login: FAILED ({str(e)})")
        return None

def test_qr_code_creation(user_id):
    """Test QR code creation"""
    try:
        test_qr = {
            'id': 'test-qr-001',
            'userId': str(user_id),
            'title': 'Test QR Code',
            'url': 'https://example.com',
            'type': 'url'
        }
        
        response = requests.post(f'{BASE_URL}/qr-codes', json=test_qr)
        
        if response.status_code == 201:
            print("✅ QR code creation: PASSED")
            return test_qr['id']
        else:
            print(f"❌ QR code creation: FAILED (Status: {response.status_code}, Response: {response.text})")
            return None
    except Exception as e:
        print(f"❌ QR code creation: FAILED ({str(e)})")
        return None

def test_qr_code_retrieval(user_id):
    """Test QR code retrieval"""
    try:
        response = requests.get(f'{BASE_URL}/qr-codes', params={'userId': user_id})
        
        if response.status_code == 200:
            qr_codes = response.json()
            print(f"✅ QR code retrieval: PASSED (Found {len(qr_codes)} QR codes)")
            return True
        else:
            print(f"❌ QR code retrieval: FAILED (Status: {response.status_code}, Response: {response.text})")
            return False
    except Exception as e:
        print(f"❌ QR code retrieval: FAILED ({str(e)})")
        return False

def test_qr_code_scan(qr_id):
    """Test QR code scan recording"""
    try:
        response = requests.post(f'{BASE_URL}/qr-codes/{qr_id}/scan')
        
        if response.status_code == 200:
            print("✅ QR code scan: PASSED")
            return True
        else:
            print(f"❌ QR code scan: FAILED (Status: {response.status_code}, Response: {response.text})")
            return False
    except Exception as e:
        print(f"❌ QR code scan: FAILED ({str(e)})")
        return False

def test_qr_code_stats(qr_id):
    """Test QR code statistics"""
    try:
        response = requests.get(f'{BASE_URL}/qr-codes/{qr_id}/stats')
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ QR code stats: PASSED (Total scans: {stats.get('totalScans', 0)})")
            return True
        else:
            print(f"❌ QR code stats: FAILED (Status: {response.status_code}, Response: {response.text})")
            return False
    except Exception as e:
        print(f"❌ QR code stats: FAILED ({str(e)})")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting API Tests...")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Server is not running. Please start the Flask application first.")
        print("Run: python run.py")
        sys.exit(1)
    
    # Test user registration and login
    test_user_registration()
    user_id = test_user_login()
    
    if user_id:
        # Test QR code operations
        qr_id = test_qr_code_creation(user_id)
        test_qr_code_retrieval(user_id)
        
        if qr_id:
            test_qr_code_scan(qr_id)
            test_qr_code_stats(qr_id)
    
    print("\n" + "=" * 50)
    print("🏁 API Tests Completed!")
    print("\nNote: Email sending test is not included as it requires SMTP configuration.")

if __name__ == '__main__':
    main()