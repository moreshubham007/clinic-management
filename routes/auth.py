import os
import json
import requests as http_requests
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from oauthlib.oauth2 import WebApplicationClient
from app import db
from models import User, Doctor
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email

auth_bp = Blueprint('auth', __name__)

# Initialize OAuth 2 client
oauth_client = None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need to be an admin to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember.data
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

def get_google_provider_cfg():
    try:
        discovery_url = current_app.config['GOOGLE_DISCOVERY_URL']
        response = http_requests.get(discovery_url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()
    except Exception as e:
        current_app.logger.error(f"Error fetching Google provider config: {str(e)}")
        return None

@auth_bp.route('/google/login')
def google_login():
    try:
        global oauth_client
        if not oauth_client:
            client_id = current_app.config.get('GOOGLE_CLIENT_ID')
            if not client_id:
                flash("Google OAuth not configured properly", "danger")
                return redirect(url_for('auth.login'))
            oauth_client = WebApplicationClient(client_id)
        
        # Get Google's provider configuration
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash("Failed to get Google provider configuration", "danger")
            return redirect(url_for('auth.login'))
            
        authorization_endpoint = google_provider_cfg["authorization_endpoint"]
        
        # Construct the request for Google login
        redirect_uri = url_for('auth.google_callback', _external=True)
        request_uri = oauth_client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
        )
        
        return redirect(request_uri)
    except Exception as e:
        current_app.logger.error(f"Error in Google login: {str(e)}")
        flash("An error occurred during Google login", "danger")
        return redirect(url_for('auth.login'))

@auth_bp.route('/google/callback')
def google_callback():
    try:
        global oauth_client
        if not oauth_client:
            oauth_client = WebApplicationClient(current_app.config['GOOGLE_CLIENT_ID'])
            
        # Get authorization code Google sent back
        code = request.args.get("code")
        if not code:
            flash("Authentication failed: No authorization code received", "danger")
            return redirect(url_for('auth.login'))

        # Find out what URL to hit to get tokens
        google_provider_cfg = get_google_provider_cfg()
        if not google_provider_cfg:
            flash("Failed to get Google provider configuration", "danger")
            return redirect(url_for('auth.login'))
            
        token_endpoint = google_provider_cfg["token_endpoint"]

        # Prepare and send request to get tokens
        token_url, headers, body = oauth_client.prepare_token_request(
            token_endpoint,
            authorization_response=request.url,
            redirect_url=url_for('auth.google_callback', _external=True),
            code=code,
        )
        
        token_response = http_requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(current_app.config['GOOGLE_CLIENT_ID'], current_app.config['GOOGLE_CLIENT_SECRET']),
        )

        # Parse the tokens
        oauth_client.parse_request_body_response(json.dumps(token_response.json()))

        # Get user info from Google
        userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
        uri, headers, body = oauth_client.add_token(userinfo_endpoint)
        userinfo_response = http_requests.get(uri, headers=headers)

        if userinfo_response.json().get("email_verified"):
            google_id = userinfo_response.json()["sub"]
            email = userinfo_response.json()["email"]
            name = userinfo_response.json().get("name", email.split('@')[0])
            
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            if not user:
                # Create new user
                user = User(
                    email=email,
                    name=name,
                    google_id=google_id,
                    role='patient'  # Default role for Google sign-ups
                )
                db.session.add(user)
                db.session.commit()
                
            # Log in the user
            login_user(user)
            return redirect(url_for('dashboard.index'))
        else:
            flash("Google authentication failed: Email not verified", "danger")
            return redirect(url_for('auth.login'))
    except Exception as e:
        current_app.logger.error(f"Error in Google callback: {str(e)}")
        flash("An error occurred during Google authentication", "danger")
        return redirect(url_for('auth.login'))

@auth_bp.route('/create-user', methods=['GET', 'POST'])
@admin_required
def create_user():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.create_user'))
        
        user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        
        if role == 'doctor':
            specialization = request.form.get('specialization')
            availability = request.form.get('availability')
            doctor = Doctor(
                user_id=user.id,
                specialization=specialization,
                availability=json.loads(availability)
            )
            db.session.add(doctor)
        
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('auth/create_user.html') 