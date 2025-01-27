from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import User, Doctor, Appointment, Case, Question
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func

doctor_bp = Blueprint('doctor', __name__)

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            flash('You need to be a doctor to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@doctor_bp.route('/my-patients')
@login_required
@doctor_required
def my_patients():
    # Get all patients who have had appointments or cases with this doctor
    patients = User.query.join(Appointment, User.id == Appointment.patient_id)\
        .filter(
            User.role == 'patient',
            Appointment.doctor_id == current_user.doctor.id
        )\
        .union(
            User.query.join(Case, User.id == Case.patient_id)\
            .filter(
                User.role == 'patient',
                Case.doctor_id == current_user.doctor.id
            )
        )\
        .order_by(User.name)\
        .all()

    # For each patient, get additional statistics
    patient_stats = {}
    for patient in patients:
        # Get total appointments
        total_appointments = Appointment.query.filter_by(
            patient_id=patient.id,
            doctor_id=current_user.doctor.id
        ).count()

        # Get total cases
        total_cases = Case.query.filter_by(
            patient_id=patient.id,
            doctor_id=current_user.doctor.id
        ).count()

        # Get last visit date
        last_appointment = Appointment.query.filter_by(
            patient_id=patient.id,
            doctor_id=current_user.doctor.id,
            status='completed'
        ).order_by(Appointment.datetime.desc()).first()

        # Get active cases
        active_cases = Case.query.filter_by(
            patient_id=patient.id,
            doctor_id=current_user.doctor.id,
            status='active'
        ).count()

        patient_stats[patient.id] = {
            'total_appointments': total_appointments,
            'total_cases': total_cases,
            'last_visit': last_appointment.datetime if last_appointment else None,
            'active_cases': active_cases
        }

    return render_template('doctor/my_patients.html', 
                         patients=patients,
                         patient_stats=patient_stats) 