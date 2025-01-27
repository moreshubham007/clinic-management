from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
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
    
    return render_template('dashboard/doctor_dashboard.html',
                         today_appointments=today_appointments,
                         upcoming_appointments=upcoming_appointments,
                         recent_cases=recent_cases,
                         unanswered_questions=unanswered_questions,
                         patients=patients)

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