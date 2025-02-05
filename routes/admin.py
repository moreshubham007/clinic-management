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
        try:
            # Get all form data
            form_data = {
                'email': request.form.get('email'),
                'name': request.form.get('name'),
                'role': request.form.get('role'),
                'password': request.form.get('password'),
                'specialization': request.form.get('specialization'),
                'availability': request.form.get('availability'),
                'address': request.form.get('address'),
                'state': request.form.get('state'),
                'city': request.form.get('city'),
                'pin_code': request.form.get('pin_code'),
                'mobile_number': request.form.get('mobile_number'),
                'date_of_birth': request.form.get('date_of_birth'),
                'aadhar_number': request.form.get('aadhar_number'),
                'patient_number': request.form.get('patient_number')
            }

            # Validate required fields
            if not all([form_data['email'], form_data['name'], form_data['role'], form_data['password']]):
                flash('Email, name, role, and password are required', 'danger')
                return render_template('admin/create_user.html', form_data=form_data)

            # Check if user already exists
            if User.query.filter_by(email=form_data['email']).first():
                flash('Email already registered', 'danger')
                return render_template('admin/create_user.html', form_data=form_data)

            # Create new user
            user = User(
                email=form_data['email'],
                name=form_data['name'],
                role=form_data['role']
            )
            user.set_password(form_data['password'])

            # Handle role-specific fields
            if form_data['role'] == 'doctor':
                if not form_data['specialization']:
                    flash('Specialization is required for doctors', 'danger')
                    return render_template('admin/create_user.html', form_data=form_data)
                
                # Create doctor profile
                doctor = Doctor(
                    user=user,
                    specialization=form_data['specialization']
                )
                
                # Handle availability
                try:
                    # Get the availability data and checked days
                    availability_data = form_data.get('availability', '{}')
                    checked_days = request.form.getlist('day_enabled[]')  # Get list of checked days
                    
                    # Parse the availability data
                    availability = json.loads(availability_data) if availability_data else {}
                    
                    # Initialize all days
                    all_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    final_availability = {}
                    
                    # Process each day
                    for day in all_days:
                        if day in checked_days:
                            # If day is checked, use its slots or empty list if no slots defined
                            final_availability[day] = availability.get(day, [])
                        else:
                            # If day is unchecked, use empty list
                            final_availability[day] = []
                    
                    doctor.availability = final_availability
                    current_app.logger.info(f"Setting availability: {final_availability}")
                    
                except (json.JSONDecodeError, TypeError) as e:
                    current_app.logger.error(f"Error processing availability: {str(e)}")
                    doctor.availability = {day: [] for day in all_days}
                
                db.session.add(doctor)

            elif form_data['role'] == 'patient':
                # Validate required patient fields
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

            db.session.add(user)
            db.session.commit()
            flash(f'Successfully created {form_data["role"]}', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')
            return render_template('admin/create_user.html', form_data=form_data)

    return render_template('admin/create_user.html', form_data=form_data)

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
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
                if not request.form.get('specialization'):
                    flash('Specialization is required for doctors', 'danger')
                    return redirect(url_for('admin.edit_user', user_id=user_id))

                if not doctor:
                    doctor = Doctor(user_id=user.id)
                    db.session.add(doctor)
                
                doctor.specialization = request.form.get('specialization')
                
                # Handle availability schedule
                try:
                    availability_data = request.form.get('availability', '{}')
                    checked_days = request.form.getlist('day_enabled[]')
                    
                    availability = json.loads(availability_data) if availability_data else {}
                    
                    all_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    final_availability = {day: [] for day in all_days}
                    
                    for day in all_days:
                        if day in checked_days:
                            if day in availability and isinstance(availability[day], list):
                                final_availability[day] = availability[day]
                    
                    doctor.availability = final_availability
                    
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"JSON Decode Error: {str(e)}")
                    flash('Error processing availability schedule: Invalid format', 'danger')
                    return redirect(url_for('admin.edit_user', user_id=user_id))
                except Exception as e:
                    current_app.logger.error(f"Error updating availability: {str(e)}")
                    flash(f'Error updating availability schedule: {str(e)}', 'danger')
                    return redirect(url_for('admin.edit_user', user_id=user_id))
            
            # Update role
            user.role = new_role
            
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user: {str(e)}")
            flash(f'Error updating user: {str(e)}', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
    
    # For GET request, prepare form data
    form_data = {
        'id': user.id,
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
    
    return render_template('admin/edit_user.html', user=user, form_data=form_data)

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