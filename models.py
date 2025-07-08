from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets
import string
from typing import Optional

db = SQLAlchemy()

class User(db.Model):
    """Modèle utilisateur avancé avec sécurité renforcée"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Verification email
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    email_verification_token = db.Column(db.String(100), unique=True)
    email_verification_sent_at = db.Column(db.DateTime)
    
    # Reset password
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)
    
    # Security
    failed_login_attempts = db.Column(db.Integer, default=0)
    account_locked_until = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relations
    refresh_tokens = db.relationship('RefreshToken', backref='user', lazy=True, cascade='all, delete-orphan')
    qr_codes = db.relationship('QRCode', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password: str) -> None:
        """Hash et stocke le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def generate_email_verification_token(self) -> str:
        """Génère un token de vérification email"""
        token = secrets.token_urlsafe(32)
        self.email_verification_token = token
        self.email_verification_sent_at = datetime.utcnow()
        return token
    
    def generate_reset_token(self) -> str:
        """Génère un token de reset password"""
        token = secrets.token_urlsafe(32)
        self.reset_token = token
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        return token
    
    def verify_reset_token(self, token: str) -> bool:
        """Vérifie la validité du token de reset"""
        return (self.reset_token == token and 
                self.reset_token_expires and 
                self.reset_token_expires > datetime.utcnow())
    
    def clear_reset_token(self) -> None:
        """Supprime le token de reset"""
        self.reset_token = None
        self.reset_token_expires = None
    
    def increment_failed_login(self) -> None:
        """Incrémente les tentatives de connexion échouées"""
        self.failed_login_attempts += 1
        # Verrouiller le compte après 5 tentatives
        if self.failed_login_attempts >= 5:
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=15)
    
    def clear_failed_login(self) -> None:
        """Remet à zéro les tentatives échouées"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
    
    def is_locked(self) -> bool:
        """Vérifie si le compte est verrouillé"""
        return (self.account_locked_until and 
                self.account_locked_until > datetime.utcnow())
    
    def update_last_login(self) -> None:
        """Met à jour la dernière connexion"""
        self.last_login = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convertit l'utilisateur en dictionnaire"""
        return {
            'id': self.id,
            'email': self.email,
            'email_verified': self.email_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class RefreshToken(db.Model):
    """Modèle pour les refresh tokens JWT"""
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False, index=True)
    
    # Metadata
    device_info = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    last_used = db.Column(db.DateTime)
    is_revoked = db.Column(db.Boolean, default=False, nullable=False)
    
    def __init__(self, user_id: int, token: str, expires_in_days: int = 30, **kwargs):
        super().__init__()
        self.user_id = user_id
        self.token_hash = generate_password_hash(token)
        self.expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        self.device_info = kwargs.get('device_info')
        self.ip_address = kwargs.get('ip_address')
        self.user_agent = kwargs.get('user_agent')
    
    def verify_token(self, token: str) -> bool:
        """Vérifie la validité du token"""
        return (not self.is_revoked and 
                self.expires_at > datetime.utcnow() and
                check_password_hash(self.token_hash, token))
    
    def revoke(self) -> None:
        """Révoque le token"""
        self.is_revoked = True
    
    def is_expired(self) -> bool:
        """Vérifie si le token a expiré"""
        return self.expires_at <= datetime.utcnow()
    
    def update_last_used(self) -> None:
        """Met à jour la dernière utilisation"""
        self.last_used = datetime.utcnow()


class QRCode(db.Model):
    """Modèle QR Code étendu"""
    __tablename__ = 'qr_codes'
    
    id = db.Column(db.String(100), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Contenu du QR Code
    type = db.Column(db.String(20), nullable=False)  # url, text, email, etc.
    data = db.Column(db.Text, nullable=False)
    original_url = db.Column(db.Text)  # Pour les QR dynamiques
    
    # Apparence
    color = db.Column(db.String(7), default='#000000')
    background_color = db.Column(db.String(7), default='#ffffff')
    size = db.Column(db.Integer, default=256)
    
    # QR Code dynamique
    is_dynamic = db.Column(db.Boolean, default=False)
    short_code = db.Column(db.String(10), unique=True)
    short_url = db.Column(db.String(255))
    
    # Statut et validation
    status = db.Column(db.String(20), default='active')  # active, expired, disabled
    scans = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    validity_duration = db.Column(db.String(20))
    
    # Relations
    scan_logs = db.relationship('QRScanLog', backref='qr_code', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def increment_scan(self) -> None:
        """Incrémente le compteur de scans"""
        self.scans += 1
    
    def is_expired(self) -> bool:
        """Vérifie si le QR code a expiré"""
        return self.expires_at <= datetime.utcnow()
    
    def is_active(self) -> bool:
        """Vérifie si le QR code est actif"""
        return self.status == 'active' and not self.is_expired()
    
    def to_dict(self) -> dict:
        """Convertit le QR code en dictionnaire"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'data': self.data,
            'original_url': self.original_url,
            'color': self.color,
            'background_color': self.background_color,
            'size': self.size,
            'is_dynamic': self.is_dynamic,
            'short_code': self.short_code,
            'short_url': self.short_url,
            'status': self.status,
            'scans': self.scans,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'validity_duration': self.validity_duration
        }


class QRScanLog(db.Model):
    """Log des scans de QR codes"""
    __tablename__ = 'qr_scan_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    qr_code_id = db.Column(db.String(100), db.ForeignKey('qr_codes.id'), nullable=False)
    
    # Metadata du scan
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referer = db.Column(db.String(500))
    country = db.Column(db.String(2))
    device_type = db.Column(db.String(20))  # mobile, desktop, tablet
    
    # Timestamp
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self) -> dict:
        """Convertit le log de scan en dictionnaire"""
        return {
            'id': self.id,
            'qr_code_id': self.qr_code_id,
            'timestamp': self.scanned_at.isoformat() if self.scanned_at else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referer': self.referer,
            'country': self.country,
            'device_type': self.device_type,
            'device_info': {
                'type': self.device_type,
                'user_agent': self.user_agent
            },
            'location': {
                'country': self.country,
                'ip_address': self.ip_address
            }
        }


class ShortLink(db.Model):
    """Modèle pour les liens courts (QR dynamiques)"""
    __tablename__ = 'short_links'
    
    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    original_url = db.Column(db.Text, nullable=False)
    qr_code_id = db.Column(db.String(100), db.ForeignKey('qr_codes.id'))
    
    # Statistiques
    clicks = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, short_code: str, original_url: str, **kwargs):
        super().__init__()
        self.short_code = short_code
        self.original_url = original_url
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def increment_clicks(self) -> None:
        """Incrémente le compteur de clics"""
        self.clicks += 1
    
    def to_dict(self) -> dict:
        """Convertit le lien court en dictionnaire"""
        return {
            'id': self.id,
            'short_code': self.short_code,
            'original_url': self.original_url,
            'qr_code_id': self.qr_code_id,
            'clicks': self.clicks,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }