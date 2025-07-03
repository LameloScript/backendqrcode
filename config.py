#!/usr/bin/env python3
"""
Configuration settings for the Flask application
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SMTP Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    FROM_EMAIL = os.getenv('FROM_EMAIL')
    NO_REPLY_EMAIL = os.getenv('NO_REPLY_EMAIL')
    
    # CORS Origins
    CORS_ORIGINS = [
        "http://localhost:8080",  # Vite dev
        "http://localhost:5173",  # Vite dev alternative
        "http://localhost:3000",  # React dev
        "https://pepiteafrica.com",     # Production
        "https://www.pepiteafrica.com"  # Production with www
    ]
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///qrcode_users_dev.db')
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///qrcode_users.db')
    
    # Additional production settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])