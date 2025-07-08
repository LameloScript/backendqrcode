#!/usr/bin/env python3
"""
Configuration simple et fonctionnelle
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de base"""
    
    # Configuration Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Configuration MySQL
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    
    # Configuration JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 900))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    # Configuration SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8080,http://localhost:5173,http://localhost:3000,https://qrcode.taohome.ci').split(',')
    
    # Configuration URL de base pour les liens courts
    BASE_URL = os.getenv('BASE_URL', 'https://qrcode.taohome.ci')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    def __init__(self):
        # Configuration automatique de la base de données avec test de connexion
        if all([self.MYSQL_USERNAME, self.MYSQL_PASSWORD, self.MYSQL_DATABASE]):
            # Tenter MySQL d'abord
            mysql_uri = f"mysql+pymysql://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            
            # Test de connexion MySQL
            if self._test_mysql_connection(mysql_uri):
                self.SQLALCHEMY_DATABASE_URI = mysql_uri
                print(f"Configuration MySQL: {self.MYSQL_DATABASE}")
            else:
                # Fallback SQLite si MySQL échoue
                db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'qrcode_users.db')
                self.SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
                print("Configuration SQLite (MySQL inaccessible)")
        else:
            # Fallback SQLite si credentials manquants
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'qrcode_users.db')
            self.SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
            print("Configuration SQLite (MySQL indisponible)")
    
    def _test_mysql_connection(self, uri):
        """Test la connexion MySQL"""
        try:
            import pymysql
            # Extraire les paramètres de connexion
            connection = pymysql.connect(
                host=self.MYSQL_HOST,
                port=self.MYSQL_PORT,
                user=self.MYSQL_USERNAME,
                password=self.MYSQL_PASSWORD,
                database=self.MYSQL_DATABASE,
                connect_timeout=5
            )
            connection.close()
            return True
        except Exception as e:
            print(f"Test connexion MySQL échoué: {e}")
            return False

def get_config():
    """Récupérer la configuration"""
    return Config()