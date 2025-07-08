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
    
    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 900))  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))  # 30 jours
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # SMTP Configuration (legacy)
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 465))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    FROM_EMAIL = os.getenv('FROM_EMAIL')
    NO_REPLY_EMAIL = os.getenv('NO_REPLY_EMAIL')
    
    # CORS Origins
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:8080,http://localhost:5173,http://localhost:3000').split(',')
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', "memory://")
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if not all([self.MYSQL_USERNAME, self.MYSQL_PASSWORD, self.MYSQL_DATABASE]):
            return 'sqlite:///app.db'  # Fallback to SQLite
        return f"mysql+pymysql://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    def __init__(self):
        super().__init__()
        # Set SQLALCHEMY_DATABASE_URI as class attribute for Flask-SQLAlchemy
        if not all([self.MYSQL_USERNAME, self.MYSQL_PASSWORD, self.MYSQL_DATABASE]):
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Fallback to SQLite
        else:
            self.SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        if not all([self.MYSQL_USERNAME, self.MYSQL_PASSWORD, self.MYSQL_DATABASE]):
            raise ValueError("MySQL configuration required in production")
        return f"mysql+pymysql://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    def __init__(self):
        super().__init__()
        # Set SQLALCHEMY_DATABASE_URI as class attribute for Flask-SQLAlchemy
        if not all([self.MYSQL_USERNAME, self.MYSQL_PASSWORD, self.MYSQL_DATABASE]):
            raise ValueError("MySQL configuration required in production")
        self.SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
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
    config_class = config.get(env, config['default'])
    return config_class()  # Return instance instead of class