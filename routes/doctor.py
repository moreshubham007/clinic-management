from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, Doctor, Appointment, Case, Question
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func, and_

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
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    active_only = request.args.get('active_only', '')
    per_page = 15
    doctor_id = current_user.doctor.id

    # Base query — patients linked to this doctor via appointments OR cases
    query = User.query.filter(
        User.role == 'patient',
        db.or_(
            User.appointments.any(Appointment.doctor_id == doctor_id),
            User.cases.any(Case.doctor_id == doctor_id)
        )
    )

    # Server-side search
    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.patient_number.ilike(f'%{search}%')
            )
        )

    # Active cases filter
    if active_only:
        query = query.filter(
            User.cases.any(
                db.and_(Case.doctor_id == doctor_id, Case.status == 'active')
            )
        )

    pagination = query.order_by(User.name).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Build stats only for the current page (avoids loading all records)
    patient_stats = {}
    for patient in pagination.items:
        total_appointments = Appointment.query.filter_by(
            patient_id=patient.id, doctor_id=doctor_id).count()
        total_cases = Case.query.filter_by(
            patient_id=patient.id, doctor_id=doctor_id).count()
        last_appt = Appointment.query.filter_by(
            patient_id=patient.id, doctor_id=doctor_id, status='completed'
        ).order_by(Appointment.datetime.desc()).first()
        active_cases = Case.query.filter_by(
            patient_id=patient.id, doctor_id=doctor_id, status='active').count()

        patient_stats[patient.id] = {
            'total_appointments': total_appointments,
            'total_cases': total_cases,
            'last_visit': last_appt.datetime if last_appt else None,
            'active_cases': active_cases
        }

    return render_template('doctor/my_patients.html',
                         patients=pagination.items,
                         pagination=pagination,
                         patient_stats=patient_stats,
                         search=search,
                         active_only=active_only) 