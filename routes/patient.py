from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import User, Doctor, Question, Feedback, Case, CaseTransfer
from datetime import datetime
from functools import wraps

patient_bp = Blueprint('patient', __name__)

def patient_required(f):
    @wraps(f)  # This preserves the original function name
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'patient':
            flash('You need to be a patient to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)  # This preserves the original function name
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'doctor':
            flash('You need to be a doctor to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# Patient routes
@patient_bp.route('/my-cases')
@patient_required
def view_my_cases():
    cases = Case.query.filter_by(
        patient_id=current_user.id,
        show_to_patient=True
    ).order_by(Case.created_at.desc()).all()
    return render_template('cases/list.html', cases=cases)

@patient_bp.route('/ask-question', methods=['GET', 'POST'])
@patient_required
def ask_question():
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        question_text = request.form.get('question')
        is_private = bool(request.form.get('is_private'))
        
        if not doctor_id or not question_text:
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('patient.ask_question'))
        
        question = Question(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            question=question_text,
            is_private=is_private,
            created_at=datetime.now()
        )
        
        db.session.add(question)
        db.session.commit()
        
        flash('Your question has been submitted', 'success')
        return redirect(url_for('patient.my_questions'))
    
    doctors = Doctor.query.join(User).filter(User.is_active == True).all()
    return render_template('patient/ask_question.html', doctors=doctors)

@patient_bp.route('/questions')
@patient_required
def my_questions():
    questions = Question.query.filter_by(patient_id=current_user.id).order_by(Question.created_at.desc()).all()
    return render_template('patient/questions.html', questions=questions)

@patient_bp.route('/give-feedback/<int:doctor_id>', methods=['GET', 'POST'])
@patient_required
def give_feedback(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        is_anonymous = bool(request.form.get('is_anonymous'))
        
        if not rating or not comment:
            flash('Please fill in all required fields', 'danger')
            return redirect(url_for('patient.give_feedback', doctor_id=doctor_id))
        
        feedback = Feedback(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            rating=rating,
            comment=comment,
            is_anonymous=is_anonymous,
            created_at=datetime.now()
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback', 'success')
        return redirect(url_for('dashboard.patient_dashboard'))
    
    return render_template('patient/give_feedback.html', doctor=doctor)

# Doctor routes
@patient_bp.route('/doctor/questions')
@login_required
@doctor_required
def doctor_questions():
    questions = Question.query.filter_by(
        doctor_id=current_user.doctor.id
    ).order_by(Question.created_at.desc()).all()
    
    return render_template('doctor/questions.html', questions=questions)

@patient_bp.route('/doctor/answer-question/<int:question_id>', methods=['POST'])
@login_required
@doctor_required
def answer_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    if question.doctor_id != current_user.doctor.id:
        flash('You can only answer questions assigned to you.', 'danger')
        return redirect(url_for('patient.doctor_questions'))
    
    answer = request.form.get('answer')
    if not answer:
        flash('Please provide an answer.', 'danger')
        return redirect(url_for('patient.doctor_questions'))
    
    question.answer = answer
    question.answered_at = datetime.now()
    db.session.commit()
    
    flash('Answer submitted successfully', 'success')
    return redirect(url_for('patient.doctor_questions'))

@patient_bp.route('/patient/<int:patient_id>/history')
@login_required
@doctor_required
def view_history(patient_id):
    # Get the patient
    patient = User.query.filter_by(id=patient_id, role='patient').first_or_404()
    
    # Initialize history list
    history = []
    
    # Add appointments to history
    for appointment in patient.appointments:
        status_color = {
            'scheduled': 'primary',
            'completed': 'success',
            'cancelled': 'danger'
        }.get(appointment.status, 'secondary')
        
        history.append({
            'type': 'appointment',
            'datetime': appointment.datetime,
            'status': appointment.status,
            'status_color': status_color,
            'doctor_name': appointment.doctor.user.name,
            'notes': appointment.notes,
            'remarks': appointment.remarks,
            'id': appointment.id
        })
    
    # Add cases to history
    for case in patient.cases:
        # Get feedback for this case if it exists
        feedback = Feedback.query.filter_by(
            patient_id=patient.id,
            doctor_id=case.doctor_id
        ).first()

        feedback_data = None
        if feedback:
            feedback_data = {
                'rating': feedback.rating,
                'comment': feedback.comment,
                'created_at': feedback.created_at,
                'is_anonymous': feedback.is_anonymous
            }

        status_color = {
            'active': 'success',
            'closed': 'secondary',
            'transferred': 'warning'
        }.get(case.status, 'secondary')
        
        history.append({
            'type': 'case',
            'datetime': case.created_at,
            'status': case.status,
            'status_color': status_color,
            'diagnosis': case.diagnosis,
            'treatment': case.treatment,
            'doctor_name': case.doctor.user.name,
            'feedback': feedback_data,
            'id': case.id
        })
    
    # Add case transfers to history
    transfers = CaseTransfer.query\
        .join(Case, CaseTransfer.case_id == Case.id)\
        .filter(Case.patient_id == patient.id)\
        .options(
            db.joinedload(CaseTransfer.from_doctor).joinedload(Doctor.user),
            db.joinedload(CaseTransfer.to_doctor).joinedload(Doctor.user)
        )\
        .all()
    for transfer in transfers:
        history.append({
            'type': 'transfer',
            'datetime': transfer.created_at,
            'status': transfer.status,
            'from_doctor_name': transfer.from_doctor.user.name,
            'to_doctor_name': transfer.to_doctor.user.name,
            'transfer_reason': transfer.transfer_reason,
            'transfer_notes': transfer.transfer_notes,
            'transfer_priority': transfer.transfer_priority,
            'patient_condition': transfer.patient_condition,
            'current_medications': transfer.current_medications,
            'id': transfer.id
        })
    
    # Add questions to history
    for question in patient.questions:
        history.append({
            'type': 'question',
            'datetime': question.created_at,
            'question': question.question,
            'answer': question.answer,
            'doctor_name': question.doctor.user.name if question.answer else None,
            'answered_at': question.answered_at
        })
    
    # Sort history by datetime in descending order
    history.sort(key=lambda x: x['datetime'], reverse=True)
    
    return render_template('patient/history.html', patient=patient, history=history) 