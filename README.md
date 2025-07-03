# QR Code Analytics Backend

A Flask-based backend API for QR code generation, management, and analytics tracking.

## Features

- QR code CRUD operations
- Scan tracking and analytics
- User authentication and registration
- Email sending functionality
- Rate limiting for API protection
- CORS support for frontend integration

## Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd backendqrcode
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create environment file:
   ```bash
   cp .env.example .env
   ```

6. Configure your `.env` file with your SMTP settings and other configurations.

### Running the Application

1. Make sure your virtual environment is activated

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. The API will be available at `http://127.0.0.1:5000`

## API Endpoints

### QR Code Management

- `POST /qr-codes` - Create a new QR code
- `GET /qr-codes?userId=<user_id>` - Get all QR codes for a user
- `GET /qr-codes/<qr_id>` - Get a specific QR code
- `PUT /qr-codes/<qr_id>` - Update a QR code
- `DELETE /qr-codes/<qr_id>` - Delete a QR code

### Analytics

- `GET /qr-codes/<qr_id>/stats` - Get QR code statistics
- `POST /qr-codes/<qr_id>/scan` - Record a QR code scan

### User Authentication

- `POST /register` - Register a new user
- `POST /login` - User login
- `POST /logout` - User logout

### Utility

- `POST /send-email` - Send email notifications
- `GET /health` - Health check endpoint

## Rate Limiting

The API includes rate limiting to prevent abuse:
- Default: 200 requests per day, 50 per hour
- Email sending: 5 per minute
- QR code creation/updates: 30 per minute
- Data retrieval: 60 per minute

## Database

The application uses SQLite by default with Flask-SQLAlchemy. The database file will be created automatically in the `instance` directory.

## Security Features

- Input sanitization
- Email validation
- Password hashing
- CORS configuration
- Rate limiting
- Secure session management

## Development

For development, set `FLASK_ENV=development` in your `.env` file to enable debug mode.

## Production Deployment

For production deployment:
1. Set `FLASK_ENV=production` in your environment
2. Use a production WSGI server like Gunicorn
3. Configure a proper database (PostgreSQL, MySQL)
4. Set up proper logging and monitoring
5. Use environment variables for sensitive configuration