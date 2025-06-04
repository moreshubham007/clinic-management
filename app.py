from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
import click
from datetime import timedelta
from urllib.parse import urlencode
from flask_cors import CORS
from flask_caching import Cache
import logging
from logging.handlers import RotatingFileHandler
from docs.api_docs import swagger_ui_blueprint

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Basic configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(24).hex())
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///clinic.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google OAuth configuration
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Only for development

# Configure CSRF protection
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY', os.getenv('SECRET_KEY'))
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # Disable CSRF check for GET requests

# Configure email settings
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

# Add these settings to your app config
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Initialize mail
mail = Mail(app)

# Initialize CSRF protection
from flask_wtf.csrf import CSRFProtect, generate_csrf
csrf = CSRFProtect(app)

# Exempt API routes from CSRF protection if needed
csrf.exempt('admin.user_api')

# User roles
ROLE_ADMIN = 'admin'
ROLE_DOCTOR = 'doctor'
ROLE_RECEPTIONIST = 'receptionist'
ROLE_PATIENT = 'patient'

# Import models after db initialization
from models import User, Doctor

# If you're using Flask-Caching or similar, configure it to exclude admin routes
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add current_user and csrf_token to template context
@app.context_processor
def inject_template_globals():
    return {
        'current_user': current_user,
        'csrf_token': generate_csrf
    }

# Register blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.dashboard import dashboard_bp
from routes.patient import patient_bp
from routes.doctor import doctor_bp
from routes.appointments import appointments_bp
from routes.cases import cases_bp
from routes.receptionist import receptionist_bp
from routes.api.patient import patient_api_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(dashboard_bp)
app.register_blueprint(patient_bp, url_prefix='/patient')
app.register_blueprint(doctor_bp, url_prefix='/doctor')
app.register_blueprint(appointments_bp, url_prefix='/appointments')
app.register_blueprint(cases_bp)
app.register_blueprint(receptionist_bp, url_prefix='/receptionist')
app.register_blueprint(patient_api_bp, url_prefix='/api')
app.register_blueprint(swagger_ui_blueprint, url_prefix='/api/docs')

# Basic error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 error: {str(error)}")
    import traceback
    app.logger.error(traceback.format_exc())
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Root route
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == ROLE_ADMIN:
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == ROLE_DOCTOR:
            return redirect(url_for('dashboard.doctor_dashboard'))
        elif current_user.role == ROLE_RECEPTIONIST:
            return redirect(url_for('dashboard.receptionist_dashboard'))
        else:
            return redirect(url_for('dashboard.patient_dashboard'))
    return redirect(url_for('auth.login'))

@app.cli.command("create-admin")
@click.argument("email")
@click.argument("name")
@click.password_option()
def create_admin(email, name, password):
    """Create a new admin user."""
    from werkzeug.security import generate_password_hash
    
    try:
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            click.echo(f"Error: User with email {email} already exists.")
            return

        # Create new admin user
        admin = User(
            email=email,
            name=name,
            role=ROLE_ADMIN,
            password_hash=generate_password_hash(password),
            is_active=True
        )
        
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Admin user {email} created successfully!")
    
    except Exception as e:
        click.echo(f"Error creating admin user: {str(e)}")
        db.session.rollback()

def update_url_params(args, **new_params):
    """Update URL parameters while preserving existing ones."""
    params = args.copy()
    for key, value in new_params.items():
        params[key] = value
    return '?' + urlencode(params)

app.jinja_env.globals.update(
    update_url_params=update_url_params,
    min=min
)

@app.after_request
def add_cache_control_headers(response):
    """Add cache control headers to prevent browser caching"""
    if request.blueprint == 'admin' or request.blueprint == 'dashboard':
        # For admin and dashboard pages, strictly disable caching
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    else:
        # For other pages, we can use a more relaxed policy
        response.headers["Cache-Control"] = "private, no-cache, max-age=0"
        
    # Add Vary header to respect HTTP headers in cache
    response.headers["Vary"] = "Cookie, Authorization"
    
    return response

# Don't cache admin routes
@cache.cached(unless=lambda: request.blueprint == 'admin')
def my_cached_route():
    # ... function body here
    pass

@app.before_request
def before_request():
    print(f"Processing request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    print(f"Completed request: {request.method} {request.path} - Status: {response.status_code}")
    return response

# Configure logging
if not os.path.exists('logs'):
    os.mkdir('logs')
    
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

# Move this outside any function
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 

# Debug SQLAlchemy
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

@app.route('/test-db')
def test_db():
    try:
        user_count = User.query.count()
        return f"Database connection successful. User count: {user_count}"
    except Exception as e:
        return f"Database error: {str(e)}" 