from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from models import Case, Appointment, Doctor, User, CaseAttachment
from datetime import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename

cases_bp = Blueprint('cases', __name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads/case_attachments'
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'png', 'jpg', 'jpeg', 'gif', 'bmp'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['pdf']:
        return 'pdf'
    elif ext in ['doc', 'docx']:
        return 'word'
    elif ext in ['xls', 'xlsx']:
        return 'excel'
    elif ext in ['ppt', 'pptx']:
        return 'powerpoint'
    elif ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
        return 'image'
    return 'other'

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            flash('Access denied. You must be a doctor to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@cases_bp.route('/cases')
@login_required
def list_cases():
    if current_user.role == 'doctor':
        cases = Case.query.filter_by(doctor_id=current_user.doctor.id)\
            .order_by(Case.created_at.desc()).all()
    elif current_user.role == 'patient':
        cases = Case.query.filter_by(patient_id=current_user.id)\
            .filter_by(show_to_patient=True)\
            .order_by(Case.created_at.desc()).all()
    else:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('cases/list.html', cases=cases)

@cases_bp.route('/api/search_patients')
@login_required
@doctor_required
def search_patients():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
    
    patients = User.query.filter_by(role='patient')\
        .filter(
            (User.name.ilike(f'%{query}%')) |
            (User.email.ilike(f'%{query}%'))
        )\
        .limit(10)\
        .all()
    
    return jsonify([{
        'id': patient.id,
        'name': patient.name,
        'email': patient.email
    } for patient in patients])

@cases_bp.route('/cases/create', methods=['GET', 'POST'])
@login_required
@doctor_required
def create_case_without_appointment():
    if request.method == 'POST':
        try:
            patient_id = request.form.get('patient_id')
            diagnosis = request.form.get('diagnosis')
            treatment = request.form.get('treatment')
            show_to_patient = bool(request.form.get('show_to_patient'))
            
            if not all([patient_id, diagnosis, treatment]):
                flash('Please fill in all required fields.', 'danger')
                return redirect(url_for('cases.create_case_without_appointment'))
            
            # Verify patient exists
            patient = User.query.filter_by(id=patient_id, role='patient').first()
            if not patient:
                flash('Invalid patient selected.', 'danger')
                return redirect(url_for('cases.create_case_without_appointment'))
            
            case = Case(
                patient_id=patient_id,
                doctor_id=current_user.doctor.id,
                diagnosis=diagnosis,
                treatment=treatment,
                show_to_patient=show_to_patient,
                status='active'
            )
            
            db.session.add(case)
            db.session.commit()
            
            flash('Case created successfully.', 'success')
            return redirect(url_for('cases.list_cases'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating case: {str(e)}', 'danger')
            return redirect(url_for('cases.create_case_without_appointment'))
    
    return render_template('cases/create_without_appointment.html')

@cases_bp.route('/cases/create/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
@doctor_required
def create_case(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Verify the appointment belongs to the current doctor
    if appointment.doctor_id != current_user.doctor.id:
        flash('Access denied. This appointment is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            diagnosis = request.form.get('diagnosis')
            treatment = request.form.get('treatment')
            show_to_patient = bool(request.form.get('show_to_patient'))
            
            if not all([diagnosis, treatment]):
                flash('Please fill in all required fields.', 'danger')
                return redirect(url_for('cases.create_case', appointment_id=appointment_id))
            
            case = Case(
                patient_id=appointment.patient_id,
                doctor_id=current_user.doctor.id,
                diagnosis=diagnosis,
                treatment=treatment,
                show_to_patient=show_to_patient,
                status='active'
            )
            
            # Link the case to the appointment after creation
            db.session.add(case)
            db.session.flush()  # This gets us the case.id
            
            # Update the appointment with the case_id and mark it as completed
            appointment.case_id = case.id
            appointment.status = 'completed'
            
            db.session.commit()
            
            flash('Case created successfully.', 'success')
            return redirect(url_for('cases.list_cases'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating case: {str(e)}', 'danger')
            return redirect(url_for('cases.create_case', appointment_id=appointment_id))
    
    return render_template('cases/create.html', appointment=appointment)

@cases_bp.route('/cases/<int:case_id>')
@login_required
def view_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Check access permissions
    if current_user.role == 'doctor' and case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    elif current_user.role == 'patient' and case.patient_id != current_user.id:
        flash('Access denied. This case does not belong to you.', 'danger')
        return redirect(url_for('index'))
    elif current_user.role not in ['doctor', 'patient']:
        flash('Access denied.', 'danger')
        return redirect(url_for('index'))
    
    # Get list of doctors for transfer modal
    doctors = Doctor.query.join(User).filter(User.is_active == True).all() if current_user.role == 'doctor' else None
    
    return render_template('cases/view.html', case=case, doctors=doctors)

@cases_bp.route('/cases/<int:case_id>/feedback', methods=['POST'])
@login_required
def submit_feedback(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Verify the case belongs to the current patient
    if current_user.role != 'patient' or case.patient_id != current_user.id:
        flash('Access denied. You cannot submit feedback for this case.', 'danger')
        return redirect(url_for('index'))
    
    try:
        rating = int(request.form.get('rating'))
        feedback_text = request.form.get('feedback_text')
        
        if not all([rating, feedback_text]) or rating not in range(1, 6):
            flash('Please provide both rating and feedback.', 'danger')
            return redirect(url_for('cases.view_case', case_id=case_id))
        
        case.feedback_rating = rating
        case.feedback_text = feedback_text
        case.feedback_date = datetime.now()
        
        db.session.commit()
        flash('Feedback submitted successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting feedback: {str(e)}', 'danger')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/cases/<int:case_id>/toggle-visibility', methods=['POST'])
@login_required
@doctor_required
def toggle_visibility(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Verify the case belongs to the current doctor
    if case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    try:
        case.show_to_patient = not case.show_to_patient
        db.session.commit()
        
        status = 'visible to' if case.show_to_patient else 'hidden from'
        flash(f'Case is now {status} the patient.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating case visibility: {str(e)}', 'danger')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/cases/<int:case_id>/reopen', methods=['POST'])
@login_required
@doctor_required
def reopen_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Verify the case belongs to the current doctor
    if case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    try:
        if case.status != 'closed':
            flash('Only closed cases can be reopened.', 'danger')
            return redirect(url_for('cases.view_case', case_id=case_id))
        
        case.status = 'active'
        case.updated_at = datetime.now()
        db.session.commit()
        
        flash('Case reopened successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error reopening case: {str(e)}', 'danger')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/cases/<int:case_id>/close', methods=['POST'])
@login_required
@doctor_required
def close_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Verify the case belongs to the current doctor
    if case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    try:
        if case.status == 'closed':
            flash('Case is already closed.', 'danger')
            return redirect(url_for('cases.view_case', case_id=case_id))
        
        notes = request.form.get('notes', '')
        case.status = 'closed'
        case.updated_at = datetime.now()
        case.closing_notes = notes
        db.session.commit()
        
        flash('Case closed successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error closing case: {str(e)}', 'danger')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/cases/<int:case_id>/edit')
@login_required
@doctor_required
def edit_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Verify the case belongs to the current doctor
    if case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('cases/edit.html', case=case)

@cases_bp.route('/cases/<int:case_id>/update', methods=['POST'])
@login_required
@doctor_required
def update_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Verify the case belongs to the current doctor
    if case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    try:
        case.diagnosis = request.form.get('diagnosis')
        case.treatment = request.form.get('treatment')
        case.show_to_patient = 'show_to_patient' in request.form
        case.updated_at = datetime.now()
        
        db.session.commit()
        flash('Case updated successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating case: {str(e)}', 'danger')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/cases/<int:case_id>/transfer', methods=['POST'])
@login_required
@doctor_required
def transfer_case(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Verify the case belongs to the current doctor
    if case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    try:
        new_doctor_id = request.form.get('new_doctor_id')
        transfer_notes = request.form.get('transfer_notes')
        
        if not new_doctor_id:
            flash('Please select a doctor to transfer the case to.', 'danger')
            return redirect(url_for('cases.view_case', case_id=case_id))
        
        case.doctor_id = new_doctor_id
        case.status = 'transferred'
        case.updated_at = datetime.now()
        
        db.session.commit()
        
        flash('Case transferred successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error transferring case: {str(e)}', 'danger')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/cases/<int:case_id>/upload', methods=['POST'])
@login_required
@doctor_required
def upload_attachment(case_id):
    case = Case.query.get_or_404(case_id)
    
    # Verify the case belongs to the current doctor
    if case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('cases.view_case', case_id=case_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('cases.view_case', case_id=case_id))
    
    if file and allowed_file(file.filename):
        try:
            # Create upload directory if it doesn't exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # Create attachment record
            attachment = CaseAttachment(
                case_id=case_id,
                filename=unique_filename,
                original_filename=filename,
                file_type=get_file_type(filename),
                file_size=os.path.getsize(file_path),
                uploaded_by_id=current_user.id
            )
            
            db.session.add(attachment)
            db.session.commit()
            
            flash('File uploaded successfully', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading file: {str(e)}', 'danger')
            
    else:
        flash(f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}', 'danger')
    
    return redirect(url_for('cases.view_case', case_id=case_id))

@cases_bp.route('/cases/attachments/<int:attachment_id>')
@login_required
def view_attachment(attachment_id):
    attachment = CaseAttachment.query.get_or_404(attachment_id)
    case = attachment.case
    
    # Check access permissions
    if current_user.role == 'doctor' and case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    elif current_user.role == 'patient' and case.patient_id != current_user.id:
        flash('Access denied. This case does not belong to you.', 'danger')
        return redirect(url_for('index'))
    
    file_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
    if not os.path.exists(file_path):
        flash('File not found', 'danger')
        return redirect(url_for('cases.view_case', case_id=case.id))
    
    # For inline viewing
    if 'view' in request.args:
        if attachment.file_type == 'pdf':
            return send_file(file_path, mimetype='application/pdf')
        elif attachment.file_type == 'image':
            return send_file(file_path)
        elif attachment.file_type in ['word', 'excel', 'powerpoint']:
            # Try Microsoft Office Online Viewer first
            file_url = request.host_url.rstrip('/') + url_for('cases.view_attachment', attachment_id=attachment_id)
            if request.args.get('viewer') == 'google':
                # Use Google Docs Viewer as fallback
                viewer_url = f"https://docs.google.com/viewer?url={file_url}&embedded=true"
            else:
                viewer_url = f"https://view.officeapps.live.com/op/embed.aspx?src={file_url}"
            return redirect(viewer_url)
    
    # For direct download
    return send_file(file_path, 
                    download_name=attachment.original_filename,
                    as_attachment=True)

@cases_bp.route('/cases/attachments/<int:attachment_id>/delete', methods=['POST'])
@login_required
@doctor_required
def delete_attachment(attachment_id):
    attachment = CaseAttachment.query.get_or_404(attachment_id)
    case = attachment.case
    
    # Verify the case belongs to the current doctor
    if case.doctor_id != current_user.doctor.id:
        flash('Access denied. This case is not assigned to you.', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Delete the file
        file_path = os.path.join(UPLOAD_FOLDER, attachment.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the record
        db.session.delete(attachment)
        db.session.commit()
        
        flash('File deleted successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting file: {str(e)}', 'danger')
    
    return redirect(url_for('cases.view_case', case_id=case.id)) 