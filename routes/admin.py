import os
import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from models import User, Doctor
from werkzeug.security import generate_password_hash
from functools import wraps
from app import ROLE_ADMIN, ROLE_DOCTOR
import re

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != ROLE_ADMIN:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_users = User.query.count()
    total_doctors = Doctor.query.count()
    active_doctors = Doctor.query.join(User).filter(User.is_active == True).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_doctors=total_doctors,
                         active_doctors=active_doctors)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    # Get filter parameters from request
    role = request.args.get('role')
    status = request.args.get('status')
    search = request.args.get('search', '').strip()
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Start with base query
    query = User.query
    
    # Apply filters
    if role:
        query = query.filter(User.role == role)
    
    if status:
        is_active = status == 'active'
        query = query.filter(User.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
    
    # Execute query with pagination
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, 
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'admin/users.html',
        users=users,
        per_page=per_page
    )

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form_data = {}
    
    if request.method == 'POST':
        print("Processing POST request to create user")
        print(f"Form data received: {request.form}")
        
        try:
            # Get form data
            form_data = {
                'name': request.form.get('name'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'role': request.form.get('role'),
                'is_active': bool(request.form.get('is_active', True)),
            }
            
            print(f"Processed form data: {form_data}")
            
            # Basic validation
            if not all([form_data['name'], form_data['email'], form_data['password'], form_data['role']]):
                print("Validation failed: missing required fields")
                flash('All basic fields are required', 'danger')
                return render_template('admin/create_user.html', form_data=form_data)
            
            # Check if email exists
            existing_user = User.query.filter_by(email=form_data['email']).first()
            if existing_user:
                print(f"Email already exists: {form_data['email']}")
                flash('Email already exists', 'danger')
                return render_template('admin/create_user.html', form_data=form_data)
            
            # Create user object
            print("Creating new user object")
            user = User(
                name=form_data['name'],
                email=form_data['email'],
                role=form_data['role'],
                is_active=form_data['is_active']
            )
            user.set_password(form_data['password'])
            print(f"User object created: {user.name}, {user.email}, {user.role}")
            
            # Add role-specific information
            if form_data['role'] == 'doctor':
                print("Processing doctor-specific data")
                # Collect doctor data
                form_data['specialization'] = request.form.get('specialization', '')
                form_data['availability'] = request.form.get('availability', '{}')
                
                # Process availability data
                try:
                    availability_data = json.loads(form_data['availability'])
                    print(f"Parsed availability data: {availability_data}")
                except json.JSONDecodeError:
                    availability_data = {}
                    print("Error parsing availability data, using empty dict")
                
                # Save the user first to get an ID
                print("Adding user to session")
                db.session.add(user)
                db.session.flush()  # Get ID without committing
                print(f"User flushed to DB with ID: {user.id}")
                
                # Create doctor record
                print("Creating doctor record")
                doctor = Doctor(
                    user_id=user.id,
                    specialization=form_data['specialization'],
                    availability=availability_data
                )
                print(f"Doctor object created with user_id: {doctor.user_id}")
                db.session.add(doctor)
                print("Doctor added to session")
                
            elif form_data['role'] == 'patient':
                print("Processing patient-specific data")
                # Validate required patient fields
                form_data.update({
                    'address': request.form.get('address', ''),
                    'state': request.form.get('state', ''),
                    'city': request.form.get('city', ''),
                    'pin_code': request.form.get('pin_code', ''),
                    'mobile_number': request.form.get('mobile_number', ''),
                    'date_of_birth': request.form.get('date_of_birth', ''),
                    'aadhar_number': request.form.get('aadhar_number', ''),
                    'patient_number': request.form.get('patient_number', ''),
                    'gender': request.form.get('gender', '')
                })
                
                required_fields = ['address', 'state', 'city', 'pin_code', 'mobile_number', 
                                'date_of_birth', 'aadhar_number', 'patient_number']
                if not all(form_data.get(field) for field in required_fields):
                    flash('All patient fields are required', 'danger')
                    return render_template('admin/create_user.html', form_data=form_data)

                # Set patient fields
                user.address = form_data['address']
                user.state = form_data['state']
                user.city = form_data['city']
                user.pin_code = form_data['pin_code']
                user.mobile_number = form_data['mobile_number']
                user.date_of_birth = datetime.strptime(form_data['date_of_birth'], '%Y-%m-%d').date()
                user.aadhar_number = form_data['aadhar_number']
                user.patient_number = form_data['patient_number']
                user.gender = form_data['gender']
                
                # Add user to the session
                db.session.add(user)
            
            else:  # Admin or other roles
                print(f"Adding user with role {user.role} to session")
                db.session.add(user)
            
            # Commit the transaction
            print("Committing the transaction")
            db.session.commit()
            print(f"User created successfully: {user.id}, {user.email}, {user.role}")
            flash(f'Successfully created {form_data["role"]}', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            print(f"ERROR creating user: {str(e)}")
            import traceback
            print(traceback.format_exc())
            flash(f'Error creating user: {str(e)}', 'danger')
            return render_template('admin/create_user.html', form_data=form_data)

    print("GET request for create_user form")
    return render_template('admin/create_user.html', form_data=form_data)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    doctor = None
    if user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.id).first()
    
    if request.method == 'POST':
        try:
            # Update basic user information
            user.name = request.form.get('name')
            user.email = request.form.get('email')
            new_role = request.form.get('role')
            user.is_active = bool(request.form.get('is_active'))
            
            # Handle password change if provided
            password = request.form.get('password')
            if password:
                user.set_password(password)
            
            # Handle patient-specific fields
            if new_role == 'patient':
                user.patient_number = request.form.get('patient_number')
                user.mobile_number = request.form.get('mobile_number')
                user.aadhar_number = request.form.get('aadhar_number')
                user.address = request.form.get('address')
                user.state = request.form.get('state')
                user.city = request.form.get('city')
                user.pin_code = request.form.get('pin_code')
                
                # Handle date of birth
                date_of_birth = request.form.get('date_of_birth')
                if date_of_birth:
                    user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            
            # Handle doctor-specific fields
            if new_role == 'doctor':
                if not doctor:
                    doctor = Doctor(user_id=user.id)
                    db.session.add(doctor)
                
                doctor.specialization = request.form.get('specialization', '')
                
                # Handle availability data
                availability_json = request.form.get('availability', '{}')
                print(f"Received availability data: {availability_json}")
                
                try:
                    availability = json.loads(availability_json)
                    doctor.availability = availability
                except json.JSONDecodeError:
                    doctor.availability = {}
                    print("Error decoding availability JSON")
            
            # Update role
            user.role = new_role
            
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
            print(f"Error in edit_user: {str(e)}")
    
    # For GET requests, prepare form data
    form_data = {
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'is_active': user.is_active,
        'patient_number': user.patient_number if hasattr(user, 'patient_number') else None,
        'mobile_number': user.mobile_number if hasattr(user, 'mobile_number') else None,
        'aadhar_number': user.aadhar_number if hasattr(user, 'aadhar_number') else None,
        'address': user.address if hasattr(user, 'address') else None,
        'state': user.state if hasattr(user, 'state') else None,
        'city': user.city if hasattr(user, 'city') else None,
        'pin_code': user.pin_code if hasattr(user, 'pin_code') else None,
        'date_of_birth': user.date_of_birth.strftime('%Y-%m-%d') if hasattr(user, 'date_of_birth') and user.date_of_birth else None,
        'specialization': doctor.specialization if doctor else None,
        'availability': doctor.availability if doctor else None
    }
    
    return render_template('admin/edit_user.html', 
        user=user, 
        form_data=form_data
    )

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.role == ROLE_ADMIN:
        flash('Cannot delete admin user.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    if user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if doctor:
            db.session.delete(doctor)
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == ROLE_ADMIN:
        flash('Cannot modify admin user status.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {status} successfully', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/api/next-patient-number')
@login_required
@admin_required
def next_patient_number():
    try:
        # Get the last patient number
        last_patient = User.query.filter(
            User.role == 'patient',
            User.patient_number.isnot(None)
        ).order_by(User.patient_number.desc()).first()
        
        if last_patient and last_patient.patient_number:
            try:
                # Extract the number part and increment
                last_num = int(last_patient.patient_number.split('-')[1])
                next_num = last_num + 1
            except (IndexError, ValueError):
                # If there's any error parsing the number, start from 1
                next_num = 1
        else:
            # Start with 1 if no existing patients
            next_num = 1
        
        # Format the new patient number
        patient_number = f'INRI-{next_num:05d}'
        
        return jsonify({
            'status': 'success',
            'patient_number': patient_number
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 