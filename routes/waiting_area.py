from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, Appointment, Doctor, WaitingArea
from datetime import datetime, date, time, timedelta
from functools import wraps

waiting_area_bp = Blueprint('waiting_area', __name__)

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in allowed_roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def today_range():
    """Return (start, end) datetimes covering the current local calendar day."""
    start = datetime.combine(date.today(), time.min)
    return start, start + timedelta(days=1)


def todays_waiting_query(doctor_id=None):
    """
    Waiting-area entries for appointments scheduled today only.
    Filtering by appointment.datetime (not check_in_time) keeps the board
    aligned with Today's Appointments and avoids stale/previous-day rows.
    """
    start, end = today_range()
    q = WaitingArea.query.join(
        Appointment, WaitingArea.appointment_id == Appointment.id
    ).filter(
        Appointment.datetime >= start,
        Appointment.datetime < end,
    )
    if doctor_id is not None:
        q = q.filter(WaitingArea.doctor_id == doctor_id)
    return q


def sync_waiting_on_complete(appointment, actor_user_id=None):
    """
    Keep waiting-area board in sync when an appointment is marked completed
    (from dashboard, edit form, case creation, etc.).
    Updates an existing entry, or creates a completed entry for today.
    Does NOT commit — caller owns the transaction.
    """
    now = datetime.now()
    waiting_entry = WaitingArea.query.filter_by(
        appointment_id=appointment.id
    ).first()

    if waiting_entry:
        if waiting_entry.status != 'completed':
            waiting_entry.status = 'completed'
            waiting_entry.completion_time = now
            waiting_entry.updated_at = now
            if not waiting_entry.actual_start_time:
                waiting_entry.actual_start_time = now
        return waiting_entry

    if not appointment.doctor_id:
        return None

    new_entry = WaitingArea(
        appointment_id=appointment.id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        expected_appointment_time=appointment.datetime,
        check_in_time=now,
        actual_start_time=now,
        completion_time=now,
        status='completed',
        priority=appointment.priority or 'normal',
        added_by_id=actor_user_id,
    )
    db.session.add(new_entry)
    return new_entry


def cleanup_completed_appointments():
    """Sync waiting-area status when the linked appointment is already completed."""
    try:
        completed_waiting_entries = WaitingArea.query.join(Appointment).filter(
            Appointment.status == 'completed',
            WaitingArea.status.in_(['waiting', 'in_progress'])
        ).all()

        removed_count = 0
        now = datetime.now()
        for entry in completed_waiting_entries:
            if entry.status != 'completed':
                entry.status = 'completed'
                entry.completion_time = now
                entry.updated_at = now
                if not entry.actual_start_time:
                    entry.actual_start_time = now
                removed_count += 1

        if removed_count > 0:
            db.session.commit()
            print(f"Automatically updated {removed_count} waiting area entries for completed appointments")

        return removed_count
    except Exception as e:
        print(f"Error cleaning up completed appointments: {e}")
        db.session.rollback()
        return 0

@waiting_area_bp.route('/receptionist/waiting-area')
@login_required
@role_required(['receptionist', 'admin'])
def receptionist_waiting_area():
    """Receptionist view of waiting area"""
    cleanup_completed_appointments()

    start, end = today_range()

    # Today's scheduled appointments that can be added to waiting area
    scheduled_appointments = Appointment.query.filter(
        Appointment.datetime >= start,
        Appointment.datetime < end,
        Appointment.status == 'scheduled'
    ).join(Doctor).join(User, Doctor.user_id == User.id).all()

    # Today's waiting area entries (active + completed) — appointment date = today
    waiting_entries = todays_waiting_query().order_by(
        WaitingArea.check_in_time.asc()
    ).all()

    doctors = Doctor.query.join(User).filter(User.role == 'doctor').all()

    return render_template('waiting_area/receptionist.html',
                         scheduled_appointments=scheduled_appointments,
                         waiting_entries=waiting_entries,
                         doctors=doctors)

@waiting_area_bp.route('/receptionist/add-to-waiting', methods=['POST'])
@login_required
@role_required(['receptionist', 'admin'])
def add_to_waiting():
    """Add appointment to waiting area"""
    appointment_id = request.form.get('appointment_id')
    notes = request.form.get('notes', '')
    priority = request.form.get('priority', 'normal')
    
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if already in waiting area
    existing_entry = WaitingArea.query.filter_by(appointment_id=appointment_id).first()
    if existing_entry:
        flash('Patient is already in the waiting area.', 'warning')
        return redirect(url_for('waiting_area.receptionist_waiting_area'))
    
    # Create waiting area entry
    waiting_entry = WaitingArea(
        appointment_id=appointment_id,
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        expected_appointment_time=appointment.datetime,
        notes=notes,
        priority=priority,
        added_by_id=current_user.id
    )
    
    db.session.add(waiting_entry)
    db.session.commit()
    
    flash(f'Patient {appointment.patient.name} added to waiting area.', 'success')
    return redirect(url_for('waiting_area.receptionist_waiting_area'))

@waiting_area_bp.route('/receptionist/update-waiting/<int:entry_id>', methods=['POST'])
@login_required
@role_required(['receptionist', 'admin'])
def update_waiting_entry(entry_id):
    """Update waiting area entry"""
    entry = WaitingArea.query.get_or_404(entry_id)
    
    entry.notes = request.form.get('notes', entry.notes)
    entry.priority = request.form.get('priority', entry.priority)
    entry.updated_at = datetime.now()
    
    db.session.commit()
    flash('Waiting area entry updated successfully.', 'success')
    return redirect(url_for('waiting_area.receptionist_waiting_area'))

@waiting_area_bp.route('/receptionist/remove-from-waiting/<int:entry_id>', methods=['POST'])
@login_required
@role_required(['receptionist', 'admin'])
def remove_from_waiting(entry_id):
    """Remove patient from waiting area"""
    entry = WaitingArea.query.get_or_404(entry_id)
    patient_name = entry.patient.name
    
    db.session.delete(entry)
    db.session.commit()
    
    flash(f'Patient {patient_name} removed from waiting area.', 'success')
    return redirect(url_for('waiting_area.receptionist_waiting_area'))

@waiting_area_bp.route('/doctor/waiting-area')
@login_required
@role_required(['doctor', 'admin'])
def doctor_waiting_area():
    """Doctor view of waiting area"""
    cleanup_completed_appointments()

    if current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            flash('Doctor profile not found.', 'error')
            return redirect(url_for('dashboard.index'))

        waiting_entries = todays_waiting_query(doctor_id=doctor.id).order_by(
            WaitingArea.priority.desc(),
            WaitingArea.check_in_time.asc()
        ).all()
    else:
        waiting_entries = todays_waiting_query().order_by(
            WaitingArea.priority.desc(),
            WaitingArea.check_in_time.asc()
        ).all()

    return render_template('waiting_area/doctor.html', waiting_entries=waiting_entries)

@waiting_area_bp.route('/doctor/start-appointment/<int:entry_id>', methods=['POST'])
@login_required
@role_required(['doctor', 'admin'])
def start_appointment(entry_id):
    """Start appointment - move patient from waiting to in_progress"""
    entry = WaitingArea.query.get_or_404(entry_id)
    
    # Verify doctor owns this appointment
    if current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if entry.doctor_id != doctor.id:
            flash('You can only start your own appointments.', 'error')
            return redirect(url_for('waiting_area.doctor_waiting_area'))
    
    entry.status = 'in_progress'
    entry.actual_start_time = datetime.now()
    entry.updated_at = datetime.now()
    
    db.session.commit()
    
    flash(f'Started appointment with {entry.patient.name}.', 'success')
    return redirect(url_for('waiting_area.doctor_waiting_area'))

@waiting_area_bp.route('/doctor/complete-appointment/<int:entry_id>', methods=['POST'])
@login_required
@role_required(['doctor', 'admin'])
def complete_appointment(entry_id):
    """Complete appointment"""
    entry = WaitingArea.query.get_or_404(entry_id)
    
    # Verify doctor owns this appointment
    if current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if entry.doctor_id != doctor.id:
            flash('You can only complete your own appointments.', 'error')
            return redirect(url_for('waiting_area.doctor_waiting_area'))
    
    entry.status = 'completed'
    entry.completion_time = datetime.now()
    entry.doctor_notes = request.form.get('doctor_notes', '')
    entry.updated_at = datetime.now()
    
    # Update appointment status
    entry.appointment.status = 'completed'
    entry.appointment.updated_at = datetime.now()
    
    db.session.commit()
    
    flash(f'Completed appointment with {entry.patient.name}.', 'success')
    return redirect(url_for('waiting_area.doctor_waiting_area'))

@waiting_area_bp.route('/api/waiting-stats')
@login_required
@role_required(['doctor', 'receptionist', 'admin'])
def waiting_stats():
    """API endpoint for waiting area statistics (today's appointments only)."""
    cleanup_completed_appointments()

    doctor_id = None
    if current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if doctor:
            doctor_id = doctor.id

    waiting_entries = todays_waiting_query(doctor_id=doctor_id).all()

    total_waiting = len([e for e in waiting_entries if e.status == 'waiting'])
    total_in_progress = len([e for e in waiting_entries if e.status == 'in_progress'])
    total_completed = len([e for e in waiting_entries if e.status == 'completed'])

    long_waits = [e for e in waiting_entries if e.is_long_wait() and e.status == 'waiting']
    very_long_waits = [e for e in waiting_entries if e.is_very_long_wait() and e.status == 'waiting']

    completed_entries = [e for e in waiting_entries if e.status == 'completed' and e.actual_start_time]
    avg_wait_time = 0
    if completed_entries:
        total_wait_time = sum(e.calculate_wait_time() for e in completed_entries)
        avg_wait_time = total_wait_time / len(completed_entries)

    return jsonify({
        'total_waiting': total_waiting,
        'total_in_progress': total_in_progress,
        'total_completed': total_completed,
        'long_waits': len(long_waits),
        'very_long_waits': len(very_long_waits),
        'average_wait_time': round(avg_wait_time, 1),
        'long_wait_patients': [
            {
                'id': e.id,
                'patient_name': e.patient.name,
                'wait_time': e.calculate_wait_time(),
                'doctor_name': e.doctor.user.name
            } for e in long_waits
        ]
    })

@waiting_area_bp.route('/api/cleanup-completed', methods=['POST'])
@login_required
@role_required(['admin', 'receptionist'])
def api_cleanup_completed():
    """Manual cleanup of completed appointments from waiting area"""
    try:
        removed_count = cleanup_completed_appointments()
        return jsonify({
            'success': True,
            'message': f'Cleaned up {removed_count} completed appointments from waiting area',
            'removed_count': removed_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@waiting_area_bp.route('/api/doctor-waiting-list')
@login_required
@role_required(['doctor', 'admin'])
def doctor_waiting_list():
    """API endpoint for doctor's waiting list (today's appointments only)."""
    # Keep board in sync with appointments completed outside the waiting area UI
    cleanup_completed_appointments()

    if current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            return jsonify({'error': 'Doctor profile not found'}), 404

        waiting_entries = todays_waiting_query(doctor_id=doctor.id).order_by(
            WaitingArea.priority.desc(),
            WaitingArea.check_in_time.asc()
        ).all()
    else:
        waiting_entries = todays_waiting_query().order_by(
            WaitingArea.priority.desc(),
            WaitingArea.check_in_time.asc()
        ).all()

    return jsonify({
        'waiting_list': [
            {
                'id': e.id,
                'patient_name': e.patient.name,
                'patient_number': e.patient.patient_number,
                'check_in_time': e.check_in_time.strftime('%H:%M') if e.check_in_time else '',
                'expected_time': e.expected_appointment_time.strftime('%H:%M') if e.expected_appointment_time else '',
                'wait_time': e.calculate_wait_time(),
                'priority': e.priority,
                'status': e.status,
                'notes': e.notes,
                'is_long_wait': e.is_long_wait(),
                'is_very_long_wait': e.is_very_long_wait()
            } for e in waiting_entries
        ]
    }) 