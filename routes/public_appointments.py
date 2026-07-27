from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from extensions import db
from models import User, AppointmentRequest
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


def _generate_request_number(req_id):
    return f"APTRQ-{str(req_id).zfill(5)}"


# ── Public scanner / kiosk landing ───────────────────────────────────────────
@public_appt_bp.route('/scanner')
def scanner_landing():
    return render_template('public/scanner_landing.html')


# ── Public: landing page ──────────────────────────────────────────────────────
@public_appt_bp.route('/')
def book_landing():
    return render_template('public/book.html')


# ── Public: confirmation page (PRG pattern — GET only) ────────────────────────
@public_appt_bp.route('/confirmed')
def book_confirmed():
    ref = session.pop('appt_ref', None)
    patient_name = session.pop('appt_patient_name', None)
    if not ref:
        # Guard: if someone lands here directly without a submission, redirect home
        return redirect(url_for('public_appt.book_landing'))
    return render_template('public/book.html',
                           submitted=True,
                           ref=ref,
                           patient_name=patient_name)


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
            request_number='TEMP',
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
        db.session.flush()
        req.request_number = _generate_request_number(req.id)
        db.session.commit()

        session['appt_ref'] = req.request_number
        session['appt_patient_name'] = name
        return redirect(url_for('public_appt.book_confirmed'))

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

            mobile_for_req = submitted_mobile or (p.mobile_number if p else '')
            if not mobile_for_req:
                flash('Mobile number is required.', 'danger')
                return redirect(url_for('public_appt.book_existing_patient'))

            req = AppointmentRequest(
                request_number='TEMP',
                patient_type='existing',
                mobile_number=mobile_for_req,
                patient_id=p.id if p else None,
                patient_number=p.patient_number if p else None,
                preferred_date=preferred_date,
                preferred_time=preferred_time,
                notes=notes,
                status='pending'
            )
            db.session.add(req)
            db.session.flush()
            req.request_number = _generate_request_number(req.id)
            db.session.commit()

            session['appt_ref'] = req.request_number
            session['appt_patient_name'] = p.name if p else 'Patient'
            return redirect(url_for('public_appt.book_confirmed'))

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
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = AppointmentRequest.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    status_counts = {
        s: AppointmentRequest.query.filter_by(status=s).count()
        for s in ['pending', 'confirmed', 'cancelled']
    }

    pagination = query.order_by(AppointmentRequest.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template('public/book_requests.html',
                           requests=pagination.items,
                           pagination=pagination,
                           status_filter=status_filter,
                           status_counts=status_counts)


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
