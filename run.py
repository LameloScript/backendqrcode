#!/usr/bin/env python3
"""
Simple script to run the Flask application
"""

import os
from app import app, db

if __name__ == '__main__':
    # Initialize database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Get configuration from environment
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"Starting Flask application...")
    print(f"Debug mode: {debug_mode}")
    print(f"Server: http://{host}:{port}")
    print(f"Health check: http://{host}:{port}/health")
    
    app.run(debug=debug_mode, host=host, port=port)