from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Appointment, Case, Question, Feedback, Doctor
from datetime import datetime, timedelta
from functools import wraps
import jwt
import os
from werkzeug.security import check_password_hash

patient_api = Blueprint('patient_api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['user_id']).first()
            if not current_user or current_user.role != 'patient':
                return jsonify({'message': 'Invalid token or not a patient'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@patient_api.route('/api/patient/login', methods=['POST'])
def login():
    """
    Patient Login API
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              description: Patient's email address
            password:
              type: string
              description: Patient's password
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            token:
              type: string
            user:
              type: object
              properties:
                id: 
                  type: integer
                name:
                  type: string
                email:
                  type: string
      401:
        description: Invalid credentials
    """
    auth = request.get_json()
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({'message': 'Missing credentials'}), 401

    user = User.query.filter_by(email=auth.get('email')).first()
    if not user or not check_password_hash(user.password_hash, auth.get('password')):
        return jsonify({'message': 'Invalid credentials'}), 401

    if user.role != 'patient':
        return jsonify({'message': 'Not authorized as patient'}), 401

    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    }, os.getenv('SECRET_KEY'), algorithm="HS256")

    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'patient_number': user.patient_number
        }
    })

@patient_api.route('/api/patient/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Get Patient Profile API
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    responses:
      200:
        description: Patient profile data
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            email:
              type: string
            patient_number:
              type: string
            mobile_number:
              type: string
            gender:
              type: string
            date_of_birth:
              type: string
            address:
              type: string
            city:
              type: string
            state:
              type: string
            pin_code:
              type: string
    """
    return jsonify({
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'patient_number': current_user.patient_number,
        'mobile_number': current_user.mobile_number,
        'gender': current_user.gender,
        'date_of_birth': current_user.date_of_birth.strftime('%Y-%m-%d') if current_user.date_of_birth else None,
        'address': current_user.address,
        'city': current_user.city,
        'state': current_user.state,
        'pin_code': current_user.pin_code
    })

@patient_api.route('/api/patient/appointments', methods=['GET'])
@token_required
def get_appointments(current_user):
    """
    Get Patient Appointments API
    ---
    tags:
      - Appointments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [scheduled, completed, cancelled]
        description: Filter appointments by status
    responses:
      200:
        description: List of patient appointments
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              datetime:
                type: string
              status:
                type: string
              doctor:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
              notes:
                type: string
    """
    status = request.args.get('status')
    query = Appointment.query.filter_by(patient_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(Appointment.datetime.desc()).all()
    
    return jsonify([{
        'id': apt.id,
        'datetime': apt.datetime.strftime('%Y-%m-%d %H:%M'),
        'status': apt.status,
        'doctor': {
            'id': apt.doctor.id,
            'name': apt.doctor.user.name
        },
        'notes': apt.notes
    } for apt in appointments])

@patient_api.route('/api/patient/cases', methods=['GET'])
@token_required
def get_cases(current_user):
    """
    Get Patient Cases API
    ---
    tags:
      - Cases
    security:
      - Bearer: []
    responses:
      200:
        description: List of patient cases
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              created_at:
                type: string
              doctor:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
              diagnosis:
                type: string
              treatment:
                type: string
              status:
                type: string
    """
    cases = Case.query.filter_by(
        patient_id=current_user.id,
        show_to_patient=True
    ).order_by(Case.created_at.desc()).all()
    
    return jsonify([{
        'id': case.id,
        'created_at': case.created_at.strftime('%Y-%m-%d %H:%M'),
        'doctor': {
            'id': case.doctor.id,
            'name': case.doctor.user.name
        },
        'diagnosis': case.diagnosis,
        'treatment': case.treatment,
        'status': case.status
    } for case in cases])

@patient_api.route('/api/patient/questions', methods=['GET', 'POST'])
@token_required
def questions(current_user):
    """
    Patient Questions API
    ---
    tags:
      - Questions
    security:
      - Bearer: []
    get:
      description: Get list of patient questions
      responses:
        200:
          description: List of questions
          schema:
            type: array
            items:
              type: object
              properties:
                id:
                  type: integer
                question:
                  type: string
                answer:
                  type: string
                created_at:
                  type: string
                doctor:
                  type: object
                  properties:
                    id:
                      type: integer
                    name:
                      type: string
    post:
      description: Create a new question
      parameters:
        - in: body
          name: body
          schema:
            type: object
            required:
              - doctor_id
              - question
            properties:
              doctor_id:
                type: integer
              question:
                type: string
              is_private:
                type: boolean
      responses:
        201:
          description: Question created successfully
    """
    if request.method == 'GET':
        questions = Question.query.filter_by(patient_id=current_user.id)\
            .order_by(Question.created_at.desc()).all()
        
        return jsonify([{
            'id': q.id,
            'question': q.question,
            'answer': q.answer,
            'created_at': q.created_at.strftime('%Y-%m-%d %H:%M'),
            'answered_at': q.answered_at.strftime('%Y-%m-%d %H:%M') if q.answered_at else None,
            'doctor': {
                'id': q.doctor.id,
                'name': q.doctor.user.name
            }
        } for q in questions])
    
    else:  # POST
        data = request.get_json()
        if not data or not data.get('doctor_id') or not data.get('question'):
            return jsonify({'message': 'Missing required fields'}), 400
        
        doctor = Doctor.query.get_or_404(data['doctor_id'])
        
        question = Question(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            question=data['question'],
            is_private=data.get('is_private', False)
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'message': 'Question submitted successfully',
            'id': question.id
        }), 201

@patient_api.route('/api/patient/feedback', methods=['POST'])
@token_required
def submit_feedback(current_user):
    """
    Submit Doctor Feedback API
    ---
    tags:
      - Feedback
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - doctor_id
            - rating
          properties:
            doctor_id:
              type: integer
            rating:
              type: integer
              minimum: 1
              maximum: 5
            comment:
              type: string
            is_anonymous:
              type: boolean
    responses:
      201:
        description: Feedback submitted successfully
      400:
        description: Invalid input
    """
    data = request.get_json()
    if not data or 'doctor_id' not in data or 'rating' not in data:
        return jsonify({'message': 'Missing required fields'}), 400
    
    if not 1 <= data['rating'] <= 5:
        return jsonify({'message': 'Rating must be between 1 and 5'}), 400
    
    doctor = Doctor.query.get_or_404(data['doctor_id'])
    
    feedback = Feedback(
        patient_id=current_user.id,
        doctor_id=doctor.id,
        rating=data['rating'],
        comment=data.get('comment'),
        is_anonymous=data.get('is_anonymous', False)
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    return jsonify({'message': 'Feedback submitted successfully'}), 201