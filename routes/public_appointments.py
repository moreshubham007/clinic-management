from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import User, Doctor, AppointmentRequest
from datetime import datetime
from functools import wraps

public_appt_bp = Blueprint('public_appt', __name__)


def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'receptionist']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def _next_request_number():
    last = AppointmentRequest.query.order_by(AppointmentRequest.id.desc()).first()
    n = (last.id + 1) if last else 1
    return f"APTRQ-{str(n).zfill(5)}"


# ── Public scanner / kiosk landing ───────────────────────────────────────────
@public_appt_bp.route('/scanner')
def scanner_landing():
    return render_template('public/scanner_landing.html')


# ── Public: landing page ──────────────────────────────────────────────────────
@public_appt_bp.route('/')
def book_landing():
    return render_template('public/book.html')


# ── Public: new patient request ──────────────────────────────────────────────
@public_appt_bp.route('/new', methods=['GET', 'POST'])
def book_new_patient():
    if request.method == 'POST':
        mobile = request.form.get('mobile_number', '').strip()
        name = request.form.get('patient_name', '').strip()
        email = request.form.get('patient_email', '').strip()
        gender = request.form.get('patient_gender', '').strip()
        preferred_date_str = request.form.get('preferred_date', '').strip()
        preferred_time = request.form.get('preferred_time', '').strip()
        notes = request.form.get('notes', '').strip()

        if not mobile or not name:
            flash('Name and mobile number are required.', 'danger')
            return redirect(url_for('public_appt.book_new_patient'))

        preferred_date = None
        if preferred_date_str:
            try:
                preferred_date = datetime.strptime(preferred_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        req = AppointmentRequest(
            request_number=_next_request_number(),
            patient_type='new',
            mobile_number=mobile,
            patient_name=name,
            patient_email=email,
            patient_gender=gender,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
            notes=notes,
            status='pending'
        )
        db.session.add(req)
        db.session.commit()

        return render_template('public/book.html',
                               submitted=True,
                               ref=req.request_number,
                               patient_name=name)

    return render_template('public/book_new.html')


# ── Public: existing patient request ─────────────────────────────────────────
@public_appt_bp.route('/existing', methods=['GET', 'POST'])
def book_existing_patient():
    patient = None
    mobile = ''
    patient_number = ''

    if request.method == 'POST':
        action = request.form.get('action')
        mobile = request.form.get('mobile_number', '').strip()
        patient_number = request.form.get('patient_number', '').strip()

        if action == 'search':
            if mobile:
                patient = User.query.filter_by(mobile_number=mobile, role='patient').first()
            if not patient and patient_number:
                patient = User.query.filter_by(patient_number=patient_number, role='patient').first()
            if not patient:
                flash('Patient not found. Please check the details or register as a new patient.', 'warning')
            return render_template('public/book_existing.html',
                                   patient=patient,
                                   mobile=mobile,
                                   patient_number=patient_number)

        elif action == 'submit':
            patient_id = request.form.get('patient_id', '').strip()
            submitted_mobile = request.form.get('submitted_mobile', '').strip()
            preferred_date_str = request.form.get('preferred_date', '').strip()
            preferred_time = request.form.get('preferred_time', '').strip()
            notes = request.form.get('notes', '').strip()

            p = User.query.get(int(patient_id)) if patient_id else None

            preferred_date = None
            if preferred_date_str:
                try:
                    preferred_date = datetime.strptime(preferred_date_str, '%Y-%m-%d').date()
                except ValueError:
                    pass

            req = AppointmentRequest(
                request_number=_next_request_number(),
                patient_type='existing',
                mobile_number=submitted_mobile or (p.mobile_number if p else ''),
                patient_id=p.id if p else None,
                patient_number=p.patient_number if p else None,
                preferred_date=preferred_date,
                preferred_time=preferred_time,
                notes=notes,
                status='pending'
            )
            db.session.add(req)
            db.session.commit()

            return render_template('public/book.html',
                                   submitted=True,
                                   ref=req.request_number,
                                   patient_name=p.name if p else 'Patient')

    return render_template('public/book_existing.html',
                           patient=None,
                           mobile=mobile,
                           patient_number=patient_number)


# ── Staff: view all requests ──────────────────────────────────────────────────
@public_appt_bp.route('/requests')
@login_required
@staff_required
def appointment_requests():
    status_filter = request.args.get('status', '')
    query = AppointmentRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    requests_list = query.order_by(AppointmentRequest.created_at.desc()).all()
    return render_template('public/book_requests.html',
                           requests=requests_list,
                           status_filter=status_filter)


@public_appt_bp.route('/requests/<int:req_id>/confirm', methods=['POST'])
@login_required
@staff_required
def confirm_request(req_id):
    req = AppointmentRequest.query.get_or_404(req_id)
    req.status = 'confirmed'
    db.session.commit()
    flash(f'Request {req.request_number} confirmed.', 'success')
    return redirect(url_for('public_appt.appointment_requests',
                            status=request.args.get('status', '')))


@public_appt_bp.route('/requests/<int:req_id>/cancel', methods=['POST'])
@login_required
@staff_required
def cancel_request(req_id):
    req = AppointmentRequest.query.get_or_404(req_id)
    req.status = 'cancelled'
    db.session.commit()
    flash(f'Request {req.request_number} cancelled.', 'warning')
    return redirect(url_for('public_appt.appointment_requests',
                            status=request.args.get('status', '')))
