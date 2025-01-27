from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import User, Appointment, Case, Feedback
from functools import wraps
from datetime import datetime
from werkzeug.security import generate_password_hash
import re

receptionist_bp = Blueprint('receptionist', __name__)

def receptionist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'receptionist':
            flash('You need to be a receptionist to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@receptionist_bp.route('/patients')
@login_required
@receptionist_required
def patients_list():
    # Get search parameters
    search = request.args.get('search', '')
    
    # Base query for patients
    query = User.query.filter_by(role='patient')
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.name.like(search_term)) |
            (User.email.like(search_term)) |
            (User.patient_number.like(search_term))
        )
    
    # Get all patients ordered by name
    patients = query.order_by(User.name).all()
    
    return render_template('receptionist/patients_list.html', patients=patients, search=search)

@receptionist_bp.route('/patients/create', methods=['GET', 'POST'])
@login_required
@receptionist_required
def create_patient():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            mobile_number = request.form.get('mobile_number')
            patient_number = request.form.get('patient_number')
            gender = request.form.get('gender')
            city = request.form.get('city')
            address = request.form.get('address')
            
            # Handle date of birth
            dob_str = request.form.get('date_of_birth')
            date_of_birth = None
            if dob_str:
                try:
                    date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date format for date of birth', 'danger')
                    return redirect(url_for('receptionist.create_patient'))

            # Validate required fields
            if not all([name, email, password]):
                flash('Please fill in all required fields', 'danger')
                return redirect(url_for('receptionist.create_patient'))

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Please enter a valid email address', 'danger')
                return redirect(url_for('receptionist.create_patient'))

            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email address already exists', 'danger')
                return redirect(url_for('receptionist.create_patient'))

            # Generate patient number if not provided
            if not patient_number:
                # Get the last patient number
                last_patient = User.query.filter(
                    User.patient_number.isnot(None)
                ).order_by(User.patient_number.desc()).first()
                
                if last_patient and last_patient.patient_number:
                    # Extract the numeric part and increment
                    try:
                        last_num = int(last_patient.patient_number[1:])  # Remove P and convert to int
                        patient_number = f"P{str(last_num + 1).zfill(5)}"  # Format: P00001
                    except ValueError:
                        patient_number = "P00001"
                else:
                    patient_number = "P00001"
            
            # Check if patient number already exists
            if User.query.filter_by(patient_number=patient_number).first():
                flash('Patient number already exists', 'danger')
                return redirect(url_for('receptionist.create_patient'))

            # Create new patient user
            new_patient = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                role='patient',
                mobile_number=mobile_number,
                patient_number=patient_number,
                gender=gender,
                date_of_birth=date_of_birth,
                city=city,
                address=address,
                is_active=True
            )

            db.session.add(new_patient)
            db.session.commit()

            flash('Patient account created successfully', 'success')
            return redirect(url_for('receptionist.patients_list'))

        except Exception as e:
            db.session.rollback()
            print(f"Error creating patient: {str(e)}")  # For debugging
            flash('Error creating patient account. Please check all fields and try again.', 'danger')
            return redirect(url_for('receptionist.create_patient'))

    return render_template('receptionist/create_patient.html')

@receptionist_bp.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
@receptionist_required
def edit_patient(patient_id):
    patient = User.query.filter_by(id=patient_id, role='patient').first_or_404()
    
    if request.method == 'POST':
        try:
            # Update basic information
            patient.name = request.form.get('name')
            patient.email = request.form.get('email')
            patient.mobile_number = request.form.get('mobile_number')
            patient.city = request.form.get('city')
            patient.address = request.form.get('address')
            patient.gender = request.form.get('gender')
            
            # Handle date of birth
            dob_str = request.form.get('date_of_birth')
            if dob_str:
                try:
                    patient.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid date format for date of birth', 'danger')
                    return redirect(url_for('receptionist.edit_patient', patient_id=patient_id))
            
            # Update patient number if provided and not already set
            new_patient_number = request.form.get('patient_number')
            if new_patient_number and new_patient_number != patient.patient_number:
                # Check if patient number is unique
                existing_patient = User.query.filter_by(patient_number=new_patient_number).first()
                if existing_patient and existing_patient.id != patient.id:
                    flash('Patient number already exists', 'danger')
                    return redirect(url_for('receptionist.edit_patient', patient_id=patient_id))
                patient.patient_number = new_patient_number
            
            db.session.commit()
            flash('Patient details updated successfully', 'success')
            return redirect(url_for('receptionist.patients_list'))
            
        except Exception as e:
            db.session.rollback()
            flash('Error updating patient details', 'danger')
            return redirect(url_for('receptionist.edit_patient', patient_id=patient_id))
    
    return render_template('receptionist/edit_patient.html', patient=patient)

@receptionist_bp.route('/patient/<int:patient_id>/history')
@login_required
@receptionist_required
def patient_history(patient_id):
    """View patient history including appointments, cases, and feedback."""
    patient = User.query.get_or_404(patient_id)
    
    # Get patient's appointments with doctor details
    appointments = (Appointment.query
                   .join(User, Appointment.doctor_id == User.id)
                   .add_columns(User.name.label('doctor_name'))
                   .filter(Appointment.patient_id == patient_id)
                   .order_by(Appointment.datetime.desc())
                   .all())
    
    # Get patient's cases with doctor details
    cases = (Case.query
             .join(User, Case.doctor_id == User.id)
             .add_columns(User.name.label('doctor_name'))
             .filter(Case.patient_id == patient_id)
             .order_by(Case.created_at.desc())
             .all())
    
    # Get patient's feedback
    feedback = (Feedback.query
                .filter_by(patient_id=patient_id)
                .order_by(Feedback.created_at.desc())
                .all())
    
    return render_template('receptionist/patient_history.html',
                         patient=patient,
                         appointments=appointments,
                         cases=cases,
                         feedback=feedback) 