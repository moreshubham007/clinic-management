from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, MedicineOrder
from datetime import datetime
from functools import wraps

medicines_bp = Blueprint('medicines', __name__)


def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'receptionist']:
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def _generate_order_number(order_id):
    return f"MED-{str(order_id).zfill(5)}"


# ── Public: place order ──────────────────────────────────────────────────────
@medicines_bp.route('/order', methods=['GET', 'POST'])
def order_medicine():
    if request.method == 'POST':
        mobile = request.form.get('mobile_number', '').strip()
        patient_number = request.form.get('patient_number', '').strip()
        duration = request.form.get('duration_days')
        delivery_type = request.form.get('delivery_type')
        pickup_date_str = request.form.get('pickup_date', '').strip()
        delivery_address = request.form.get('delivery_address', '').strip()
        notes = request.form.get('additional_notes', '').strip()

        if not mobile or not duration or not delivery_type:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('medicines.order_medicine'))

        if delivery_type == 'self_pickup' and not pickup_date_str:
            flash('Please select a preferred pickup date.', 'danger')
            return redirect(url_for('medicines.order_medicine'))

        if delivery_type == 'courier' and not delivery_address:
            flash('Please provide a delivery address for courier delivery.', 'danger')
            return redirect(url_for('medicines.order_medicine'))

        # Try to link to an existing patient record
        patient = None
        if patient_number:
            patient = User.query.filter_by(patient_number=patient_number, role='patient').first()
        if not patient and mobile:
            patient = User.query.filter_by(mobile_number=mobile, role='patient').first()

        pickup_date = None
        if pickup_date_str:
            try:
                pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        order = MedicineOrder(
            order_number='TEMP',
            mobile_number=mobile,
            patient_id=patient.id if patient else None,
            patient_number=patient_number or (patient.patient_number if patient else None),
            duration_days=int(duration),
            delivery_type=delivery_type,
            pickup_date=pickup_date,
            delivery_address=delivery_address if delivery_type == 'courier' else None,
            additional_notes=notes,
            status='pending'
        )
        db.session.add(order)
        db.session.flush()  # get auto-incremented id before commit
        order.order_number = _generate_order_number(order.id)
        db.session.commit()

        flash(f'Order placed! Your Order ID is {order.order_number} — save it to track your order.', 'success')
        return redirect(url_for('medicines.track_order', order_number=order.order_number))

    return render_template('medicines/order.html')


# ── Public: track form ───────────────────────────────────────────────────────
@medicines_bp.route('/track', methods=['GET', 'POST'])
def track_medicine():
    order = None
    searched = False
    if request.method == 'POST':
        searched = True
        mobile = request.form.get('mobile_number', '').strip()
        identifier = request.form.get('identifier', '').strip()

        query = MedicineOrder.query.filter_by(mobile_number=mobile)
        if identifier:
            query = query.filter(
                (MedicineOrder.order_number == identifier) |
                (MedicineOrder.patient_number == identifier)
            )
        order = query.order_by(MedicineOrder.created_at.desc()).first()

        if not order:
            flash('No order found with the provided details. Please check the mobile number and Order / Patient ID.', 'warning')

    return render_template('medicines/track.html', order=order, searched=searched)


# ── Public: order status by order number ────────────────────────────────────
@medicines_bp.route('/track/<order_number>')
def track_order(order_number):
    order = MedicineOrder.query.filter_by(order_number=order_number).first_or_404()
    return render_template('medicines/status.html', order=order)


# ── Staff: patient lookup (AJAX) ─────────────────────────────────────────────
@medicines_bp.route('/manage/patient-lookup')
@login_required
@staff_required
def patient_lookup():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify([])
    patients = User.query.filter(
        User.role == 'patient',
        db.or_(
            User.name.ilike(f'%{q}%'),
            User.patient_number.ilike(f'%{q}%'),
            User.mobile_number.ilike(f'%{q}%')
        )
    ).limit(10).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'patient_number': p.patient_number or '',
        'mobile_number': p.mobile_number or '',
        'email': p.email or ''
    } for p in patients])


# ── Staff: create order on behalf of patient ──────────────────────────────────
@medicines_bp.route('/manage/create', methods=['GET', 'POST'])
@login_required
@staff_required
def create_order():
    if request.method == 'POST':
        mobile = request.form.get('mobile_number', '').strip()
        patient_number = request.form.get('patient_number', '').strip()
        patient_id_raw = request.form.get('patient_id', '').strip()
        duration = request.form.get('duration_days')
        delivery_type = request.form.get('delivery_type')
        pickup_date_str = request.form.get('pickup_date', '').strip()
        delivery_address = request.form.get('delivery_address', '').strip()
        notes = request.form.get('additional_notes', '').strip()
        payment_status = request.form.get('payment_status', 'unpaid')
        amount_str = request.form.get('payment_amount', '').strip()
        payment_mode = request.form.get('payment_mode', '').strip() or None

        if not mobile or not duration or not delivery_type:
            flash('Mobile number, duration, and delivery type are required.', 'danger')
            return redirect(url_for('medicines.create_order'))

        if delivery_type == 'self_pickup' and not pickup_date_str:
            flash('Please select a preferred pickup date.', 'danger')
            return redirect(url_for('medicines.create_order'))

        if delivery_type == 'courier' and not delivery_address:
            flash('Please provide a delivery address for courier delivery.', 'danger')
            return redirect(url_for('medicines.create_order'))

        # Resolve linked patient
        patient = None
        if patient_id_raw:
            patient = User.query.get(int(patient_id_raw))
        if not patient and patient_number:
            patient = User.query.filter_by(patient_number=patient_number, role='patient').first()
        if not patient and mobile:
            patient = User.query.filter_by(mobile_number=mobile, role='patient').first()

        pickup_date = None
        if pickup_date_str:
            try:
                pickup_date = datetime.strptime(pickup_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        payment_amount = None
        if amount_str:
            try:
                payment_amount = float(amount_str)
            except ValueError:
                flash('Invalid payment amount.', 'danger')
                return redirect(url_for('medicines.create_order'))

        order = MedicineOrder(
            order_number='TEMP',
            mobile_number=mobile,
            patient_id=patient.id if patient else None,
            patient_number=patient_number or (patient.patient_number if patient else None),
            duration_days=int(duration),
            delivery_type=delivery_type,
            pickup_date=pickup_date,
            delivery_address=delivery_address if delivery_type == 'courier' else None,
            additional_notes=notes,
            status='pending',
            payment_status=payment_status,
            payment_amount=payment_amount,
            payment_mode=payment_mode if payment_status == 'paid' else None,
            created_by_id=current_user.id
        )
        db.session.add(order)
        db.session.flush()
        order.order_number = _generate_order_number(order.id)
        db.session.commit()

        flash(f'Order {order.order_number} created successfully.', 'success')
        return redirect(url_for('medicines.manage_orders'))

    return render_template('medicines/create_order.html')


# ── Staff: list & manage orders ──────────────────────────────────────────────
@medicines_bp.route('/manage')
@login_required
@staff_required
def manage_orders():
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 15

    query = MedicineOrder.query
    if status_filter:
        query = query.filter_by(status=status_filter)

    # Counts per status for stats (unfiltered)
    status_counts = {
        s: MedicineOrder.query.filter_by(status=s).count()
        for s in ['pending', 'processing', 'ready', 'delivered', 'cancelled']
    }

    pagination = query.order_by(MedicineOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template('medicines/manage.html',
                           orders=pagination.items,
                           pagination=pagination,
                           status_filter=status_filter,
                           status_counts=status_counts)


@medicines_bp.route('/manage/<int:order_id>/status', methods=['POST'])
@login_required
@staff_required
def update_order_status(order_id):
    order = MedicineOrder.query.get_or_404(order_id)
    new_status = request.form.get('status')
    valid_statuses = ['pending', 'processing', 'ready', 'delivered', 'cancelled']
    if order.status == 'delivered':
        flash(f'Order {order.order_number} is already Delivered and cannot be changed.', 'warning')
    elif new_status in valid_statuses:
        order.status = new_status
        order.updated_at = datetime.now()
        db.session.commit()
        flash(f'Order {order.order_number} updated to {new_status}.', 'success')
    else:
        flash('Invalid status.', 'danger')
    return redirect(url_for('medicines.manage_orders', status=request.args.get('status', '')))


@medicines_bp.route('/manage/<int:order_id>/payment', methods=['POST'])
@login_required
@staff_required
def update_payment(order_id):
    order = MedicineOrder.query.get_or_404(order_id)

    # Payment amount is locked once order is ready, delivered or cancelled
    locked = order.status in ['ready', 'delivered', 'cancelled']
    if locked:
        flash(f'Payment details for {order.order_number} cannot be changed once the order is Ready or Delivered.', 'warning')
        return redirect(url_for('medicines.manage_orders', status=request.args.get('status', '')))

    payment_status = request.form.get('payment_status', 'unpaid')
    amount_str = request.form.get('payment_amount', '').strip()
    payment_mode = request.form.get('payment_mode', '').strip() or None

    order.payment_status = payment_status
    order.payment_mode = payment_mode
    if amount_str:
        try:
            order.payment_amount = float(amount_str)
        except ValueError:
            flash('Invalid payment amount.', 'danger')
            return redirect(url_for('medicines.manage_orders', status=request.args.get('status', '')))
    else:
        order.payment_amount = None

    order.updated_at = datetime.now()
    db.session.commit()
    flash(f'Payment details updated for order {order.order_number}.', 'success')
    return redirect(url_for('medicines.manage_orders', status=request.args.get('status', '')))


@medicines_bp.route('/manage/<int:order_id>/courier', methods=['POST'])
@login_required
@staff_required
def update_courier_details(order_id):
    order = MedicineOrder.query.get_or_404(order_id)
    order.courier_name = request.form.get('courier_name', '').strip() or None
    order.courier_awb = request.form.get('courier_awb', '').strip() or None
    order.courier_tracking_url = request.form.get('courier_tracking_url', '').strip() or None
    order.updated_at = datetime.now()
    # Auto-set status to processing if still pending
    if order.status == 'pending' and order.courier_awb:
        order.status = 'processing'
    db.session.commit()
    flash(f'Courier details updated for order {order.order_number}.', 'success')
    return redirect(url_for('medicines.manage_orders', status=request.args.get('status', '')))
