from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import re
import logging
from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configuration sécurisée CORS
CORS(app, origins=[
    "http://localhost:8080",  # Vite dev
    "http://localhost:5173",  # Vite dev alternative
    "https://pepiteafrica.com/",     # Production
    "https://www.pepiteafrica.com/"  # Production avec www
])

# Rate limiting (version corrigée)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Logging
logging.basicConfig(level=logging.INFO)

# Stockage temporaire en mémoire (à remplacer par une base de données)
qr_codes = {}
qr_stats = {}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrcode_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    # Ajoute d'autres champs si besoin

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    # Nettoie et limite la longueur
    if not text or len(text) > 1000:
        return None
    return text.strip()

# Routes pour les QR codes
@app.route('/qr-codes', methods=['POST'])
@limiter.limit("30 per minute")
def create_qr_code():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400

        qr_id = data.get('id', str(uuid.uuid4()))
        data['id'] = qr_id
        data['createdAt'] = datetime.utcnow().isoformat()
        data['scans'] = 0
        data['status'] = 'active'

        qr_codes[qr_id] = data
        qr_stats[qr_id] = []

        return jsonify(data), 201
    except Exception as e:
        logging.error(f"Erreur lors de la création du QR code: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/qr-codes', methods=['GET'])
@limiter.limit("60 per minute")
def get_all_qr_codes():
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'error': 'userId requis'}), 400

        user_qr_codes = [qr for qr in qr_codes.values() if qr.get('userId') == user_id]
        return jsonify(user_qr_codes)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des QR codes: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/qr-codes/<qr_id>', methods=['GET'])
@limiter.limit("60 per minute")
def get_qr_code(qr_id):
    try:
        qr_code = qr_codes.get(qr_id)
        if not qr_code:
            return jsonify({'error': 'QR code non trouvé'}), 404
        return jsonify(qr_code)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération du QR code: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/qr-codes/<qr_id>', methods=['PUT'])
@limiter.limit("30 per minute")
def update_qr_code(qr_id):
    try:
        if qr_id not in qr_codes:
            return jsonify({'error': 'QR code non trouvé'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Données manquantes'}), 400

        qr_codes[qr_id].update(data)
        return jsonify(qr_codes[qr_id])
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour du QR code: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/qr-codes/<qr_id>', methods=['DELETE'])
@limiter.limit("30 per minute")
def delete_qr_code(qr_id):
    try:
        if qr_id not in qr_codes:
            return jsonify({'error': 'QR code non trouvé'}), 404

        del qr_codes[qr_id]
        if qr_id in qr_stats:
            del qr_stats[qr_id]
        return '', 204
    except Exception as e:
        logging.error(f"Erreur lors de la suppression du QR code: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/qr-codes/<qr_id>/stats', methods=['GET'])
@limiter.limit("60 per minute")
def get_qr_stats(qr_id):
    try:
        if qr_id not in qr_codes:
            return jsonify({'error': 'QR code non trouvé'}), 404

        stats = {
            'totalScans': qr_codes[qr_id]['scans'],
            'scanHistory': qr_stats.get(qr_id, []),
            'status': qr_codes[qr_id]['status']
        }
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des statistiques: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/qr-codes/<qr_id>/scan', methods=['POST'])
@limiter.limit("60 per minute")
def record_scan(qr_id):
    try:
        if qr_id not in qr_codes:
            return jsonify({'error': 'QR code non trouvé'}), 404

        scan_time = datetime.utcnow().isoformat()
        qr_codes[qr_id]['scans'] += 1
        qr_stats[qr_id].append({
            'timestamp': scan_time,
            'userAgent': request.headers.get('User-Agent'),
            'ip': request.remote_addr
        })

        return jsonify({'success': True, 'scanTime': scan_time})
    except Exception as e:
        logging.error(f"Erreur lors de l'enregistrement du scan: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/send-email', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 emails par minute
def send_email():
    try:
        data = request.get_json()
        
        # Validation des données
        if not data:
            return jsonify({'error': 'Aucune donnée reçue'}), 400
        
        to_email = data.get('to')
        subject = sanitize_input(data.get('subject'))
        message = sanitize_input(data.get('message'))
        from_name = sanitize_input(data.get('from_name', 'LeClick'))
        sender_email = sanitize_input(data.get('sender_email', ''))  # Email de l'expéditeur réel
        
        if not all([to_email, subject, message]):
            return jsonify({'error': 'Champs requis manquants'}), 400
        
        if not validate_email(to_email):
            return jsonify({'error': 'Email invalide'}), 400
        
        # Configuration SMTP
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 465))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL')
        no_reply_email = os.getenv('NO_REPLY_EMAIL', f'noreply@{from_email.split("@")[1]}')
        
        if not all([smtp_server, smtp_username, smtp_password, from_email]):
            return jsonify({'error': 'Configuration serveur manquante'}), 500
        
        # Création du message avec no-reply
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{no_reply_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Reply-To'] = no_reply_email
        
        # Ajout des headers no-reply
        msg['X-Auto-Response-Suppress'] = 'All'
        msg['Auto-Submitted'] = 'auto-generated'
        
        # Corps du message avec mention no-reply
        text_body = f"""
{message}

---
ATTENTION: Ceci est un email automatique envoyé depuis notre système.
Ne répondez pas à cet email, il ne sera pas lu.
"""
        

        
        html_body = f"""
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <p>{message.replace(chr(10), '<br>')}</p>
                    
                    <hr style="border: 1px solid #eee; margin: 20px 0;">
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <p style="margin: 0; color: #6c757d; font-size: 14px;">
                            <strong>⚠️ ATTENTION:</strong> Ceci est un email automatique envoyé depuis notre système.<br>
                            <strong>Ne répondez pas à cet email</strong>, il ne sera pas lu.
                        </p>
                        {"<p style='margin: 10px 0 0 0; color: #6c757d; font-size: 14px;'>Pour toute question, contactez directement: <a href='mailto:" + sender_email + "'>" + sender_email + "</a></p>" if sender_email and validate_email(sender_email) else "<p style='margin: 10px 0 0 0; color: #6c757d; font-size: 14px;'>Pour toute question, contactez-nous sur: <a href='mailto:" + from_email + "'>" + from_email + "</a></p>"}
                    </div>
                    
                    <small style="color: #6c757d;">Envoyé depuis LeClick</small>
                </div>
            </body>
        </html>
        """
        
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Envoi sécurisé avec SSL (port 465)
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        logging.info(f"Email no-reply envoyé avec succès à {to_email}")
        return jsonify({'success': True, 'message': 'Email envoyé'})
        
    except smtplib.SMTPException as e:
        logging.error(f"Erreur SMTP: {e}")
        return jsonify({'error': 'Erreur d\'envoi email'}), 500
    except Exception as e:
        logging.error(f"Erreur générale: {e}")
        return jsonify({'error': 'Erreur serveur'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Utilisateur déjà existant'}), 400
    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Utilisateur créé'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({'message': 'Connexion réussie', 'user_id': user.id, 'email': user.email})
    return jsonify({'error': 'Identifiants invalides'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Déconnexion réussie'})

if __name__ == '__main__':
    # Initialize database tables
    with app.app_context():
        db.create_all()
    
    # Mode debug uniquement en développement
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='127.0.0.1', port=5000)