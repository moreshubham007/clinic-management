from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, Doctor, Appointment, Case, CaseHistory, WaitingArea
from datetime import datetime, timedelta
from functools import wraps

appointments_bp = Blueprint('appointments', __name__)

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            flash('You need to be a doctor to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def receptionist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'receptionist':
            flash('You need to be a receptionist to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@appointments_bp.route('/')
@login_required
def list_appointments():
    # Base query
    query = Appointment.query

    # Apply role-based filters
    if current_user.role == 'doctor':
        query = query.filter_by(doctor_id=current_user.doctor.id)
    elif current_user.role == 'patient':
        query = query.filter_by(patient_id=current_user.id)
    elif current_user.role not in ['admin', 'receptionist']:
        flash('You do not have permission to view appointments', 'danger')
        return redirect(url_for('index'))
    
    # Apply status filter
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    # Apply date filter
    date = request.args.get('date')
    if date:
        try:
            filter_date = datetime.strptime(date, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Appointment.datetime) == filter_date)
        except ValueError:
            flash('Invalid date format', 'warning')
    
    # Apply doctor filter (for admin/receptionist)
    doctor_id = request.args.get('doctor')
    if doctor_id and current_user.role in ['admin', 'receptionist']:
        try:
            query = query.filter_by(doctor_id=int(doctor_id))
        except ValueError:
            flash('Invalid doctor selection', 'warning')
    
    # Add patient_type filter
    if request.args.get('patient_type'):
        query = query.filter(Appointment.patient_type == request.args.get('patient_type'))
    
    # Add priority filter
    if request.args.get('priority'):
        query = query.filter(Appointment.priority == request.args.get('priority'))
    
    # Get all active doctors for the filter dropdown
    doctors = Doctor.query.join(User).filter(User.is_active == True).all()
    
    # Order by datetime in descending order (newest first)
    appointments = query.order_by(Appointment.datetime.desc()).all()
    
    return render_template('appointments/list.html', 
                         appointments=appointments,
                         doctors=doctors)

@appointments_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_appointment():
    if current_user.role not in ['admin', 'receptionist', 'patient', 'doctor']:
        flash('You do not have permission to create appointments', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    
    if request.method == 'POST':
        # For doctors, automatically set themselves as the doctor
        if current_user.role == 'doctor':
            doctor_id = current_user.doctor.id
        else:
            doctor_id = request.form.get('doctor_id')
            
        patient_id = request.form.get('patient_id') if current_user.role in ['admin', 'receptionist', 'doctor'] else current_user.id
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        
        if not all([doctor_id, patient_id, date_str, time_str]):
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('appointments.create_appointment'))
        
        try:
            appointment_datetime = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            
            # Check if the appointment time is in the future
            if appointment_datetime < datetime.now():
                flash('Appointment time must be in the future', 'danger')
                return redirect(url_for('appointments.create_appointment'))
            
            # Check if the doctor is available at this time
            existing_appointment = Appointment.query.filter_by(
                doctor_id=doctor_id,
                datetime=appointment_datetime
            ).first()
            
            if existing_appointment:
                flash('This time slot is already booked', 'danger')
                return redirect(url_for('appointments.create_appointment'))
            
            appointment = Appointment(
                doctor_id=doctor_id,
                patient_id=patient_id,
                datetime=appointment_datetime,
                patient_type=request.form.get('patient_type', 'existing'),
                priority=request.form.get('priority', 'medium'),
                notes=request.form.get('notes'),
                remarks=request.form.get('remarks') if current_user.role == 'doctor' else None
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            flash('Appointment created successfully', 'success')
            return redirect(url_for('appointments.list_appointments'))
            
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return redirect(url_for('appointments.create_appointment'))
    
    # For GET request - prepare data for the form
    if current_user.role == 'doctor':
        # Doctors can only create appointments for themselves
        doctors = [current_user.doctor]  # Only show themselves as an option
    else:
        doctors = Doctor.query.join(User).filter(User.is_active == True).all()
    
    patients = User.query.filter_by(role='patient').all() if current_user.role in ['admin', 'receptionist', 'doctor'] else None
    
    return render_template('appointments/create.html', doctors=doctors, patients=patients)

@appointments_bp.route('/<int:appointment_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check permissions
    if current_user.role not in ['admin', 'receptionist', 'doctor'] and current_user.id != appointment.patient_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    appointment.status = 'cancelled'
    db.session.commit()
    
    return jsonify({'success': True})

@appointments_bp.route('/<int:appointment_id>/complete', methods=['POST'])
@login_required
def complete_appointment(appointment_id):
    if current_user.role not in ['admin', 'receptionist', 'doctor']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'completed'
    
    # Update any waiting area entry for this appointment
    waiting_entry = WaitingArea.query.filter_by(appointment_id=appointment_id).first()
    if waiting_entry and waiting_entry.status in ['waiting', 'in_progress']:
        waiting_entry.status = 'completed'
        waiting_entry.completion_time = datetime.now()
        waiting_entry.updated_at = datetime.now()
    
    db.session.commit()
    
    return jsonify({'success': True})

@appointments_bp.route('/doctor/<int:doctor_id>/availability')
def get_doctor_availability(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    date_str = request.args.get('date')
    
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        # Get all appointments for the doctor on this date
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            db.func.date(Appointment.datetime) == date,
            Appointment.status != 'cancelled'
        ).all()
        
        # Convert appointments to time slots
        booked_slots = [appt.datetime.strftime("%H:%M") for appt in appointments]
        
        # Get doctor's availability for this day of week
        day_of_week = date.strftime("%A").lower()
        availability = doctor.availability.get(day_of_week, [])
        
        return jsonify({
            'available_slots': availability,
            'booked_slots': booked_slots
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

@appointments_bp.route('/cases/<int:patient_id>')
@doctor_required
def view_patient_cases(patient_id):
    cases = Case.query.filter_by(patient_id=patient_id).all()
    return render_template('cases/list.html', cases=cases)

@appointments_bp.route('/cases/create/<int:appointment_id>', methods=['GET', 'POST'])
@doctor_required
def create_case(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        show_to_patient = request.form.get('show_to_patient') == 'on'
        
        case = Case(
            patient_id=appointment.patient_id,
            doctor_id=doctor.id,
            diagnosis=diagnosis,
            treatment=treatment,
            show_to_patient=show_to_patient
        )
        db.session.add(case)
        
        case_history = CaseHistory(
            case_id=case.id,
            doctor_id=doctor.id,
            notes=f"Initial case created by Dr. {current_user.name}"
        )
        db.session.add(case_history)
        db.session.commit()
        
        flash('Case created successfully', 'success')
        return redirect(url_for('appointments.view_patient_cases', patient_id=appointment.patient_id))
    
    return render_template('cases/create.html', appointment=appointment)

@appointments_bp.route('/cases/<int:case_id>/transfer', methods=['POST'])
@doctor_required
def transfer_case(case_id):
    case = Case.query.get_or_404(case_id)
    new_doctor_id = request.form.get('new_doctor_id')
    transfer_notes = request.form.get('transfer_notes')
    
    case.doctor_id = new_doctor_id
    
    case_history = CaseHistory(
        case_id=case.id,
        doctor_id=current_user.id,
        notes=f"Case transferred to Dr. {User.query.get(new_doctor_id).name}. Notes: {transfer_notes}"
    )
    db.session.add(case_history)
    db.session.commit()
    
    flash('Case transferred successfully', 'success')
    return redirect(url_for('appointments.view_patient_cases', patient_id=case.patient_id))

@appointments_bp.route('/<int:appointment_id>/edit', methods=['GET', 'POST'])
@login_required
def update_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Enhanced permission checking based on appointment status
    can_edit = False
    
    if current_user.role == 'admin':
        can_edit = True
    elif appointment.status == 'completed':
        # Only doctors can edit completed appointments (besides admin)
        if current_user.role == 'doctor' and current_user.doctor.id == appointment.doctor_id:
            can_edit = True
    else:
        # Non-completed appointments: admin, receptionist, or assigned doctor
        if current_user.role in ['admin', 'receptionist'] or \
           (current_user.role == 'doctor' and current_user.doctor.id == appointment.doctor_id):
            can_edit = True
    
    if not can_edit:
        if appointment.status == 'completed' and current_user.role == 'receptionist':
            flash('Completed appointments can only be edited by the assigned doctor or admin', 'warning')
        else:
            flash('You do not have permission to edit this appointment', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    
    if request.method == 'POST':
        try:
            # Update appointment details
            appointment.datetime = datetime.combine(
                datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                datetime.strptime(request.form['time'], '%H:%M').time()
            )
            appointment.doctor_id = request.form['doctor_id']
            appointment.patient_type = request.form.get('patient_type', 'existing')
            appointment.priority = request.form.get('priority', 'medium')
            appointment.notes = request.form.get('notes', '')
            
            # Allow admin/receptionist to change patient and status (if not completed)
            if current_user.role in ['admin', 'receptionist']:
                # Receptionist can only modify non-completed appointments
                if appointment.status != 'completed' or current_user.role == 'admin':
                    appointment.patient_id = request.form.get('patient_id', appointment.patient_id)
                    appointment.status = request.form.get('status', appointment.status)
            
            # Allow doctor to add remarks
            if current_user.role == 'doctor':
                appointment.remarks = request.form.get('remarks', '')
            
            db.session.commit()
            flash('Appointment updated successfully', 'success')
            return redirect(url_for('appointments.list_appointments'))
            
        except ValueError:
            flash('Invalid date or time format', 'danger')
            return redirect(url_for('appointments.update_appointment', appointment_id=appointment_id))
    
    # Get all active doctors and patients for dropdowns
    doctors = Doctor.query.join(User).filter(User.is_active == True).all()
    patients = User.query.filter(User.role == 'patient', User.is_active == True).all()
    
    return render_template('appointments/edit.html', 
                         appointment=appointment,
                         doctors=doctors,
                         patients=patients,
                         now=datetime.now())

@appointments_bp.route('/<int:appointment_id>/delete', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    # Check if user is a receptionist
    if current_user.role != 'receptionist':
        flash('You do not have permission to delete appointments', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Only allow deletion of scheduled appointments
    if appointment.status != 'scheduled':
        flash('Only scheduled appointments can be deleted', 'danger')
        return redirect(url_for('appointments.list_appointments'))
    
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting appointment', 'danger')
    
    return redirect(url_for('appointments.list_appointments'))

@appointments_bp.route('/search-patient')
@login_required
def search_patient():
    search = request.args.get('q', '')
    if not search:
        return jsonify([])
    
    search_term = f"%{search}%"
    patients = User.query.filter(
        User.role == 'patient',
        (User.name.like(search_term)) |
        (User.mobile_number.like(search_term)) |
        (User.patient_number.like(search_term))
    ).limit(10).all()
    
    return jsonify([{
        'id': patient.id,
        'name': patient.name,
        'email': patient.email,
        'mobile_number': patient.mobile_number,
        'patient_number': patient.patient_number
    } for patient in patients]) 