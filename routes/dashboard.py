from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, Doctor, Appointment, Case, Question
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.role == 'doctor':
        return doctor_dashboard()
    elif current_user.role == 'receptionist':
        return receptionist_dashboard()
    elif current_user.role == 'patient':
        return patient_dashboard()
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        flash('Access denied. You must be a doctor to access this page.', 'danger')
        return redirect(url_for('index'))
    
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    
    # Get today's appointments
    today_appointments = Appointment.query.filter(
        Appointment.doctor_id == current_user.doctor.id,
        func.date(Appointment.datetime) == today
    ).order_by(Appointment.datetime).all()
    
    # Get upcoming appointments for next 7 days
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == current_user.doctor.id,
        func.date(Appointment.datetime) > today,
        func.date(Appointment.datetime) <= next_week
    ).order_by(Appointment.datetime).all()
    
    # Get recent cases
    recent_cases = Case.query.filter_by(doctor_id=current_user.doctor.id)\
        .order_by(Case.created_at.desc())\
        .limit(5)\
        .all()
    
    # Get unanswered questions
    unanswered_questions = Question.query.filter_by(
        doctor_id=current_user.doctor.id,
        answer=None
    ).order_by(Question.created_at.desc()).all()
    
    # Get recent patients (last 10) — full list available at /doctor/my-patients
    recent_patients = User.query\
        .filter(
            User.role == 'patient',
            db.or_(
                User.appointments.any(Appointment.doctor_id == current_user.doctor.id),
                User.cases.any(Case.doctor_id == current_user.doctor.id)
            )
        )\
        .order_by(User.name)\
        .limit(10)\
        .all()

    total_patients = User.query\
        .filter(
            User.role == 'patient',
            db.or_(
                User.appointments.any(Appointment.doctor_id == current_user.doctor.id),
                User.cases.any(Case.doctor_id == current_user.doctor.id)
            )
        ).count()

    new_patients_today      = sum(1 for a in today_appointments if a.patient_type == 'new')
    existing_patients_today = sum(1 for a in today_appointments if a.patient_type == 'existing')

    return render_template('dashboard/doctor_dashboard.html',
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         recent_cases=recent_cases,
                         unanswered_questions=unanswered_questions,
                         patients=recent_patients,
                         total_patients=total_patients,
                         new_patients_today=new_patients_today,
                         existing_patients_today=existing_patients_today)

@dashboard_bp.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        flash('Access denied. You must be a patient to view this page.', 'danger')
        return redirect(url_for('index'))
    
    # Get upcoming appointments
    today = datetime.now().date()
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == current_user.id,
        db.func.date(Appointment.datetime) >= today
    ).order_by(Appointment.datetime).all()
    
    # Get recent cases
    recent_cases = Case.query.filter_by(
        patient_id=current_user.id,
        show_to_patient=True
    ).order_by(Case.created_at.desc()).limit(5).all()
    
    # Get recent questions
    recent_questions = Question.query.filter_by(
        patient_id=current_user.id
    ).order_by(Question.created_at.desc()).limit(5).all()
    
    return render_template('dashboard/patient_dashboard.html',
                         upcoming_appointments=upcoming_appointments,
                         recent_cases=recent_cases,
                         recent_questions=recent_questions)

@dashboard_bp.route('/receptionist/dashboard')
@login_required
def receptionist_dashboard():
    if current_user.role != 'receptionist':
        flash('Access denied. You must be a receptionist to view this page.', 'danger')
        return redirect(url_for('index'))
    
    # Get all doctors
    doctors = Doctor.query.all()
    
    # Get today's appointments
    today = datetime.now().date()
    today_appointments = Appointment.query.filter(
        db.func.date(Appointment.datetime) == today
    ).order_by(Appointment.datetime).all()
    
    return render_template('dashboard/receptionist_dashboard.html',
                         doctors=doctors,
                         today_appointments=today_appointments) 