#!/usr/bin/env python3
"""
QR Code Generator - Backend Flask unifié avec MySQL/SQLite
Version propre et organisée
"""

from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_mail import Mail, Message
from email_validator import validate_email, EmailNotValidError
import os
import logging
from datetime import datetime, timedelta
import uuid
import string
import random
import secrets
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Import des modèles et configuration
from config import get_config
from models import db, User, RefreshToken, QRCode, QRScanLog, ShortLink

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration selon l'environnement
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        from config_production import get_config
        config = get_config()
    else:
        from config import get_config
        config = get_config()
    
    app.config.from_object(config)
    
    # Initialisation des extensions
    db.init_app(app)
    jwt = JWTManager(app)
    mail = Mail(app)
    
    # Configuration CORS
    CORS(app, origins=config.CORS_ORIGINS, supports_credentials=True)
    
    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri=getattr(config, 'RATELIMIT_STORAGE_URL', 'memory://')
    )
    
    # Logging
    log_level = getattr(config, 'LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Configuration JWT
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=getattr(config, 'JWT_ACCESS_TOKEN_EXPIRES', 900))
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=getattr(config, 'JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    
    # JWT Error Handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token expiré', 'code': 'TOKEN_EXPIRED'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Token invalide', 'code': 'TOKEN_INVALID'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Token manquant', 'code': 'TOKEN_MISSING'}), 401
    
    # Utilitaires
    def validate_email_format(email: str) -> bool:
        """Valide le format de l'email"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Nettoie et valide les entrées"""
        if not text or len(text) > max_length:
            return None
        return text.strip()
    
    def generate_short_code(length: int = 6) -> str:
        """Génère un code court aléatoire"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def get_device_type(user_agent: str) -> str:
        """Détermine le type d'appareil"""
        user_agent = user_agent.lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            return 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'tablet'
        else:
            return 'desktop'
    
    # Routes d'authentification
    @app.route('/register', methods=['POST'])
    @limiter.limit("5 per minute")
    def register():
        """Inscription utilisateur"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Données manquantes'}), 400
            
            email = sanitize_input(data.get('email', ''), 120)
            password = data.get('password', '')
            
            # Validation
            if not email or not password:
                return jsonify({'error': 'Email et mot de passe requis'}), 400
            
            if not validate_email_format(email):
                return jsonify({'error': 'Format email invalide'}), 400
            
            if len(password) < 8:
                return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères'}), 400
            
            # Vérifier si l'utilisateur existe
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Un compte avec cet email existe déjà'}), 409
            
            # Créer l'utilisateur
            user = User(email=email)
            user.set_password(password)
            user.email_verified = True  # Auto-vérification pour simplifier
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'Compte créé avec succès',
                'user_id': user.id
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur inscription: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/login', methods=['POST'])
    @limiter.limit("10 per minute")
    def login():
        """Connexion utilisateur"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Données manquantes'}), 400
            
            email = sanitize_input(data.get('email', ''), 120)
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'error': 'Email et mot de passe requis'}), 400
            
            # Trouver l'utilisateur
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                return jsonify({'error': 'Identifiants invalides'}), 401
            
            # Vérifier si le compte est verrouillé
            if user.is_locked():
                return jsonify({'error': 'Compte temporairement verrouillé'}), 423
            
            # Connexion réussie
            user.clear_failed_login()
            user.update_last_login()
            
            # Créer les tokens JWT
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            # Stocker le refresh token
            refresh_token_obj = RefreshToken(
                user_id=user.id,
                token=refresh_token,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                device_info=get_device_type(request.headers.get('User-Agent', ''))
            )
            
            db.session.add(refresh_token_obj)
            db.session.commit()
            
            return jsonify({
                'message': 'Connexion réussie',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur connexion: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/refresh', methods=['POST'])
    @jwt_required(refresh=True)
    def refresh():
        """Rafraîchir le token d'accès"""
        try:
            current_user_id = get_jwt_identity()
            new_access_token = create_access_token(identity=current_user_id)
            
            return jsonify({'access_token': new_access_token}), 200
        except Exception as e:
            logger.error(f"Erreur refresh: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/logout', methods=['POST'])
    @jwt_required()
    def logout():
        """Déconnexion utilisateur"""
        try:
            current_user_id = get_jwt_identity()
            
            # Révoquer tous les refresh tokens
            RefreshToken.query.filter_by(user_id=current_user_id).update({'is_revoked': True})
            db.session.commit()
            
            return jsonify({'message': 'Déconnexion réussie'}), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur déconnexion: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/me', methods=['GET'])
    @jwt_required()
    def get_current_user():
        """Récupérer le profil utilisateur"""
        try:
            current_user_id = get_jwt_identity()
            user = db.session.get(User, current_user_id)
            
            if not user:
                return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
            return jsonify({'user': user.to_dict()}), 200
        except Exception as e:
            logger.error(f"Erreur récupération utilisateur: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/debug-auth', methods=['GET'])
    @jwt_required()
    def debug_auth():
        """Endpoint de debug pour l'authentification"""
        try:
            current_user_id = get_jwt_identity()
            user = db.session.get(User, current_user_id)
            
            return jsonify({
                'status': 'authenticated',
                'user_id': current_user_id,
                'user_exists': user is not None,
                'user_email': user.email if user else None,
                'timestamp': datetime.now().isoformat(),
                'jwt_config': {
                    'access_token_expires': app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds(),
                    'refresh_token_expires': app.config['JWT_REFRESH_TOKEN_EXPIRES'].total_seconds()
                }
            }), 200
        except Exception as e:
            logger.error(f"Erreur debug auth: {e}")
            return jsonify({'error': 'Erreur serveur', 'details': str(e)}), 500
    

    
    # Routes QR Codes
    @app.route('/qr-codes', methods=['POST'])
    @jwt_required()
    @limiter.limit("30 per minute")
    def create_qr_code():
        """Créer un QR code"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Données manquantes'}), 400
            
            # Générer un ID unique pour le QR code
            qr_id = data.get('id')
            if not qr_id:
                # Générer un ID unique avec timestamp et random
                timestamp = int(datetime.now().timestamp() * 1000)
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                qr_id = f"qr_{timestamp}_{random_suffix}"
            
            # Vérifier si l'ID existe déjà
            while QRCode.query.filter_by(id=qr_id).first():
                timestamp = int(datetime.now().timestamp() * 1000)
                random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                qr_id = f"qr_{timestamp}_{random_suffix}"
            
            # Vérifier si un QR code existe déjà avec le même contenu pour cet utilisateur
            existing_qr = QRCode.query.filter_by(
                user_id=current_user_id,
                data=data.get('data'),
                type=data.get('type')
            ).first()
            
            if existing_qr:
                return jsonify({
                    'exists': True,
                    'existing': existing_qr.to_dict(),
                    'message': 'Un QR code existe déjà avec ce contenu'
                }), 200
            
            # Gérer les QR codes dynamiques
            is_dynamic = data.get('isDynamic', False)
            original_url = None
            short_code = None
            short_url = None
            
            if is_dynamic and data.get('type') == 'url':
                # Générer un code court unique
                short_code = generate_short_code()
                while ShortLink.query.filter_by(short_code=short_code).first():
                    short_code = generate_short_code()
                
                original_url = data.get('data')
                base_url = app.config['BASE_URL'].rstrip('/')
                short_url = f"{base_url}/go/{short_code}"
                
                # Créer le lien court
                short_link = ShortLink(
                    short_code=short_code,
                    original_url=original_url,
                    qr_code_id=qr_id
                )
                db.session.add(short_link)
                
                # Modifier les données pour utiliser le lien court
                data['data'] = short_url
            
            # Créer le QR code
            qr_code = QRCode(
                id=qr_id,
                user_id=current_user_id,
                type=data.get('type'),
                data=data.get('data'),
                original_url=original_url,
                color=data.get('color', '#000000'),
                background_color=data.get('backgroundColor', '#ffffff'),
                size=data.get('size', 256),
                is_dynamic=is_dynamic,
                short_code=short_code,
                short_url=short_url,
                expires_at=datetime.fromisoformat(data.get('expiresAt').replace('Z', '+00:00')),
                validity_duration=data.get('validityDuration')
            )
            
            db.session.add(qr_code)
            db.session.commit()
            
            response_data = qr_code.to_dict()
            response_data['exists'] = False
            response_data['message'] = 'QR code créé avec succès'
            
            return jsonify(response_data), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur création QR: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/qr-codes', methods=['GET'])
    @jwt_required()
    @limiter.limit("60 per minute")
    def get_user_qr_codes():
        """Récupérer les QR codes de l'utilisateur"""
        try:
            current_user_id = get_jwt_identity()
            qr_codes = QRCode.query.filter_by(user_id=current_user_id).all()
            
            return jsonify([qr.to_dict() for qr in qr_codes]), 200
        except Exception as e:
            logger.error(f"Erreur récupération QR: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/qr-codes/<qr_id>/update-url', methods=['PUT'])
    @jwt_required()
    @limiter.limit("30 per minute")
    def update_dynamic_url(qr_id):
        """Mettre à jour l'URL d'un QR code dynamique"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or 'newUrl' not in data:
                return jsonify({'error': 'Nouvelle URL manquante'}), 400
            
            qr_code = QRCode.query.filter_by(id=qr_id, user_id=current_user_id).first()
            if not qr_code:
                return jsonify({'error': 'QR code non trouvé'}), 404
            
            if not qr_code.is_dynamic:
                return jsonify({'error': 'QR code non dynamique'}), 400
            
            new_url = sanitize_input(data['newUrl'], 2000)
            if not new_url:
                return jsonify({'error': 'URL invalide'}), 400
            
            # Mettre à jour le lien court
            short_link = ShortLink.query.filter_by(short_code=qr_code.short_code).first()
            if short_link:
                short_link.original_url = new_url
                qr_code.original_url = new_url
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'URL mise à jour avec succès',
                    'newUrl': new_url,
                    'shortUrl': qr_code.short_url
                }), 200
            else:
                return jsonify({'error': 'Lien court non trouvé'}), 404
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur mise à jour URL: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/qr-codes/<qr_id>', methods=['PUT'])
    @jwt_required()
    @limiter.limit("30 per minute")
    def update_qr_code(qr_id):
        """Mettre à jour un QR code (couleur, taille, etc.)"""
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Données manquantes'}), 400
            
            # Vérifier que le QR code appartient à l'utilisateur
            qr_code = QRCode.query.filter_by(id=qr_id, user_id=current_user_id).first()
            if not qr_code:
                return jsonify({'error': 'QR code non trouvé'}), 404
            
            # Mettre à jour les champs autorisés
            if 'color' in data:
                qr_code.color = sanitize_input(data['color'], 7)  # Format hex color
            if 'backgroundColor' in data:
                qr_code.background_color = sanitize_input(data['backgroundColor'], 7)
            if 'size' in data:
                size = data['size']
                if isinstance(size, int) and 100 <= size <= 1000:
                    qr_code.size = size
            if 'data' in data and not qr_code.is_dynamic:
                # Seuls les QR codes non-dynamiques peuvent avoir leur data modifiée
                qr_code.data = sanitize_input(data['data'], 2000)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'QR code mis à jour avec succès',
                'qr_code': qr_code.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur mise à jour QR code: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/qr-codes/<qr_id>', methods=['DELETE'])
    @jwt_required()
    @limiter.limit("30 per minute")
    def delete_qr_code(qr_id):
        """Supprimer un QR code"""
        try:
            current_user_id = get_jwt_identity()
            
            # Vérifier que le QR code appartient à l'utilisateur
            qr_code = QRCode.query.filter_by(id=qr_id, user_id=current_user_id).first()
            if not qr_code:
                return jsonify({'error': 'QR code non trouvé'}), 404
            
            # Supprimer le lien court associé si c'est un QR code dynamique
            if qr_code.is_dynamic and qr_code.short_code:
                short_link = ShortLink.query.filter_by(short_code=qr_code.short_code).first()
                if short_link:
                    db.session.delete(short_link)
            
            # Supprimer le QR code (les scan logs seront supprimés automatiquement grâce au cascade)
            db.session.delete(qr_code)
            db.session.commit()
            
            logger.info(f"QR code supprimé: {qr_id} par utilisateur: {current_user_id}")
            
            return jsonify({'message': 'QR code supprimé avec succès'}), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur suppression QR code: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/qr-codes/<qr_id>/scan-logs', methods=['GET'])
    @jwt_required()
    @limiter.limit("60 per minute")
    def get_qr_scan_logs(qr_id):
        """Récupérer les logs de scan pour un QR code spécifique"""
        try:
            current_user_id = get_jwt_identity()
            
            # Vérifier que le QR code appartient à l'utilisateur
            qr_code = QRCode.query.filter_by(id=qr_id, user_id=current_user_id).first()
            if not qr_code:
                return jsonify({'error': 'QR code non trouvé'}), 404
            
            # Récupérer les paramètres de pagination
            page = request.args.get('page', 1, type=int)
            per_page = min(request.args.get('per_page', 50, type=int), 100)  # Limiter à 100 par page
            
            # Récupérer les logs de scan avec pagination
            scan_logs_query = QRScanLog.query.filter_by(qr_code_id=qr_id).order_by(
                QRScanLog.scanned_at.desc()
            )
            
            scan_logs_paginated = scan_logs_query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Formatter les logs de scan
            scan_logs = [log.to_dict() for log in scan_logs_paginated.items]
            
            return jsonify({
                'qr_code_id': qr_id,
                'scan_logs': scan_logs,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': scan_logs_paginated.total,
                    'pages': scan_logs_paginated.pages,
                    'has_next': scan_logs_paginated.has_next,
                    'has_prev': scan_logs_paginated.has_prev
                },
                'summary': {
                    'total_scans': qr_code.scans,
                    'total_logs': scan_logs_paginated.total
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur récupération scan logs: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    # Route de redirection pour les liens courts
    @app.route('/go/<short_code>')
    @limiter.limit("100 per minute")
    def redirect_short_link(short_code):
        """Rediriger via un lien court"""
        try:
            short_link = ShortLink.query.filter_by(short_code=short_code, is_active=True).first()
            
            if not short_link:
                return jsonify({'error': 'Lien court non trouvé'}), 404
            
            # Incrémenter les compteurs
            short_link.increment_clicks()
            
            # Mettre à jour le QR code associé
            if short_link.qr_code_id:
                qr_code = db.session.get(QRCode, short_link.qr_code_id)
                if qr_code:
                    qr_code.increment_scan()
                    
                    # Logger le scan
                    scan_log = QRScanLog(
                        qr_code_id=qr_code.id,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent'),
                        device_type=get_device_type(request.headers.get('User-Agent', ''))
                    )
                    db.session.add(scan_log)
            
            db.session.commit()
            
            # Rediriger vers l'URL originale
            return redirect(short_link.original_url)
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erreur redirection: {e}")
            return jsonify({'error': 'Erreur serveur'}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Vérification de santé"""
        try:
            # Test de connexion à la base de données
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            return jsonify({
                'status': 'OK',
                'database': 'connected',
                'timestamp': datetime.now().isoformat()
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'ERROR',
                'database': 'disconnected',
                'error': str(e)
            }), 500
    
    # Créer les tables au démarrage
    with app.app_context():
        try:
            db.create_all()
            logger.info("Tables créées avec succès")
        except Exception as e:
            logger.error(f"Erreur création tables: {e}")
    
    return app

# Point d'entrée principal
if __name__ == '__main__':
    app = create_app()
    
    # Mode debug selon l'environnement
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    print("QR Code Generator Backend")
    print("=" * 30)
    print(f"URL: http://127.0.0.1:5000")
    print(f"Health: http://127.0.0.1:5000/health")
    print(f"Debug: {debug_mode}")
    print("\nCtrl+C pour arreter\n")
    
    # Configuration selon l'environnement
    if os.getenv('FLASK_ENV') == 'production':
        # En production, l'application sera gérée par le serveur web
        pass
    else:
        app.run(
            debug=debug_mode, 
            host='127.0.0.1', 
            port=5000
        )