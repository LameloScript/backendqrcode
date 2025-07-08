#!/usr/bin/env python3
"""
Configuration pour l'environnement de production LWS
"""

import os
from dotenv import load_dotenv

load_dotenv()

class ProductionConfig:
    """Configuration de production pour LWS"""
    
    # Configuration Flask
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False
    TESTING = False
    
    # Configuration MySQL pour LWS
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    
    # Configuration JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 900))
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    # Configuration SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Configuration CORS pour production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
    
    # URL de base pour les liens courts (à adapter selon votre domaine)
    BASE_URL = os.getenv('BASE_URL', 'https://votre-domaine.com')
    
    # Rate Limiting avec Redis si disponible
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Configuration Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    def __init__(self):
        # Configuration de la base de données
        if all([self.MYSQL_USERNAME, self.MYSQL_PASSWORD, self.MYSQL_DATABASE]):
            # Utiliser MySQL si configuré
            self.SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        else:
            # Fallback vers SQLite pour Railway
            import os
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'qrcode_users.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        
        # Vérifier les variables critiques
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY manquante en production")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY manquante en production")

def get_config():
    """Récupérer la configuration de production"""
    return ProductionConfig()