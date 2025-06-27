from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from extensions import db
from models import User, Appointment, Case, Question, Feedback, Doctor
from datetime import datetime, timedelta
from functools import wraps
import jwt
import os
from werkzeug.security import check_password_hash

patient_api_bp = Blueprint('patient_api', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY', 'default-secret-key'), algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user or current_user.role != 'patient':
                return jsonify({'message': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@patient_api_bp.route('/patient/login', methods=['POST'])
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
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400
        
    user = User.query.filter_by(email=data.get('email')).first()
    
    if not user or not user.check_password(data.get('password')):
        return jsonify({'message': 'Invalid credentials'}), 401
        
    if user.role != 'patient':
        return jsonify({'message': 'Not a patient account'}), 403
        
    if not user.is_active:
        return jsonify({'message': 'Account is disabled'}), 403
    
    # Generate token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, os.getenv('SECRET_KEY', 'default-secret-key'), algorithm="HS256")
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'patient_number': user.patient_number
        }
    }), 200

@patient_api_bp.route('/patient/profile', methods=['GET'])
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
    }), 200

@patient_api_bp.route('/api/patient/appointments', methods=['GET', 'POST'])
@token_required
def appointments(current_user):
    """
    Patient Appointments API
    ---
    tags:
      - Appointments
    security:
      - Bearer: []
    get:
      description: Get list of patient appointments
      parameters:
        - in: query
          name: status
          type: string
          enum: [scheduled, completed, cancelled]
          description: Filter appointments by status
      responses:
        200:
          description: List of appointments
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
                patient_type:
                  type: string
                priority:
                  type: string
    post:
      description: Create a new appointment
      parameters:
        - in: body
          name: body
          schema:
            type: object
            required:
              - doctor_id
              - datetime
            properties:
              doctor_id:
                type: integer
              datetime:
                type: string
                format: date-time
              notes:
                type: string
              patient_type:
                type: string
                enum: [new, existing]
              priority:
                type: string
                enum: [low, medium, high]
      responses:
        201:
          description: Appointment created successfully
        400:
          description: Invalid request data
        409:
          description: Time slot already booked
    """
    if request.method == 'GET':
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
            'notes': apt.notes,
            'patient_type': apt.patient_type,
            'priority': apt.priority,
            'created_at': apt.created_at.strftime('%Y-%m-%d %H:%M')
        } for apt in appointments])
    
    else:  # POST - Create appointment
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['doctor_id', 'datetime']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'Missing required field: {field}'}), 400
        
        # Validate doctor exists
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor:
            return jsonify({'message': 'Doctor not found'}), 404
        
        # Parse datetime
        try:
            appointment_datetime = datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M')
        except ValueError:
            return jsonify({'message': 'Invalid datetime format. Use YYYY-MM-DD HH:MM'}), 400
        
        # Check if appointment time is in the future
        if appointment_datetime < datetime.now():
            return jsonify({'message': 'Appointment time must be in the future'}), 400
        
        # Check if the time slot is available
        existing_appointment = Appointment.query.filter_by(
            doctor_id=doctor.id,
            datetime=appointment_datetime,
            status='scheduled'
        ).first()
        
        if existing_appointment:
            return jsonify({'message': 'This time slot is already booked'}), 409
        
        # Create appointment
        appointment = Appointment(
            doctor_id=doctor.id,
            patient_id=current_user.id,
            datetime=appointment_datetime,
            notes=data.get('notes'),
            patient_type=data.get('patient_type', 'existing'),
            priority=data.get('priority', 'medium'),
            status='scheduled'
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment created successfully',
            'appointment': {
                'id': appointment.id,
                'datetime': appointment.datetime.strftime('%Y-%m-%d %H:%M'),
                'doctor': {
                    'id': doctor.id,
                    'name': doctor.user.name
                },
                'status': appointment.status
            }
        }), 201

@patient_api_bp.route('/api/patient/appointments/<int:appointment_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def appointment_detail(current_user, appointment_id):
    """
    Patient Appointment Detail API
    ---
    tags:
      - Appointments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: appointment_id
        required: true
        type: integer
    get:
      description: Get appointment details
      responses:
        200:
          description: Appointment details
          schema:
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
              patient_type:
                type: string
              priority:
                type: string
    put:
      description: Update appointment
      parameters:
        - in: body
          name: body
          schema:
            type: object
            properties:
              datetime:
                type: string
                format: date-time
              notes:
                type: string
              priority:
                type: string
      responses:
        200:
          description: Appointment updated successfully
        404:
          description: Appointment not found
        403:
          description: Not authorized to modify this appointment
    delete:
      description: Cancel appointment
      responses:
        200:
          description: Appointment cancelled successfully
        404:
          description: Appointment not found
        403:
          description: Not authorized to cancel this appointment
    """
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Check if the appointment belongs to the current user
    if appointment.patient_id != current_user.id:
        return jsonify({'message': 'Not authorized to access this appointment'}), 403
    
    if request.method == 'GET':
        return jsonify({
            'id': appointment.id,
            'datetime': appointment.datetime.strftime('%Y-%m-%d %H:%M'),
            'status': appointment.status,
            'doctor': {
                'id': appointment.doctor.id,
                'name': appointment.doctor.user.name,
                'specialization': appointment.doctor.specialization
            },
            'notes': appointment.notes,
            'patient_type': appointment.patient_type,
            'priority': appointment.priority,
            'created_at': appointment.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': appointment.updated_at.strftime('%Y-%m-%d %H:%M') if appointment.updated_at else None
        })
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Only allow updates if appointment is scheduled
        if appointment.status != 'scheduled':
            return jsonify({'message': 'Can only update scheduled appointments'}), 400
        
        # Update datetime if provided
        if data.get('datetime'):
            try:
                new_datetime = datetime.strptime(data['datetime'], '%Y-%m-%d %H:%M')
                if new_datetime < datetime.now():
                    return jsonify({'message': 'Appointment time must be in the future'}), 400
                
                # Check if new time slot is available
                existing_appointment = Appointment.query.filter(
                    Appointment.doctor_id == appointment.doctor_id,
                    Appointment.datetime == new_datetime,
                    Appointment.status == 'scheduled',
                    Appointment.id != appointment.id
                ).first()
                
                if existing_appointment:
                    return jsonify({'message': 'This time slot is already booked'}), 409
                
                appointment.datetime = new_datetime
            except ValueError:
                return jsonify({'message': 'Invalid datetime format. Use YYYY-MM-DD HH:MM'}), 400
        
        # Update other fields
        if data.get('notes') is not None:
            appointment.notes = data['notes']
        
        if data.get('priority') is not None:
            if data['priority'] not in ['low', 'medium', 'high']:
                return jsonify({'message': 'Invalid priority value'}), 400
            appointment.priority = data['priority']
        
        appointment.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'message': 'Appointment updated successfully',
            'appointment': {
                'id': appointment.id,
                'datetime': appointment.datetime.strftime('%Y-%m-%d %H:%M'),
                'status': appointment.status
            }
        })
    
    elif request.method == 'DELETE':
        # Only allow cancellation if appointment is scheduled
        if appointment.status != 'scheduled':
            return jsonify({'message': 'Can only cancel scheduled appointments'}), 400
        
        appointment.status = 'cancelled'
        appointment.updated_at = datetime.now()
        db.session.commit()
        
        return jsonify({'message': 'Appointment cancelled successfully'})

@patient_api_bp.route('/api/patient/appointments/upcoming', methods=['GET'])
@token_required
def upcoming_appointments(current_user):
    """
    Get Upcoming Appointments API
    ---
    tags:
      - Appointments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: days
        type: integer
        default: 7
        description: Number of days to look ahead
    responses:
      200:
        description: List of upcoming appointments
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
    days = request.args.get('days', 7, type=int)
    cutoff_date = datetime.now() + timedelta(days=days)
    
    appointments = Appointment.query.filter(
        Appointment.patient_id == current_user.id,
        Appointment.datetime >= datetime.now(),
        Appointment.datetime <= cutoff_date,
        Appointment.status == 'scheduled'
    ).order_by(Appointment.datetime).all()
    
    return jsonify([{
        'id': apt.id,
        'datetime': apt.datetime.strftime('%Y-%m-%d %H:%M'),
        'status': apt.status,
        'doctor': {
            'id': apt.doctor.id,
            'name': apt.doctor.user.name
        },
        'notes': apt.notes,
        'days_until': (apt.datetime - datetime.now()).days
    } for apt in appointments])

@patient_api_bp.route('/api/patient/appointments/history', methods=['GET'])
@token_required
def appointment_history(current_user):
    """
    Get Appointment History API
    ---
    tags:
      - Appointments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of appointments to return
      - in: query
        name: status
        type: string
        enum: [completed, cancelled]
        description: Filter by status
    responses:
      200:
        description: List of past appointments
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
    limit = request.args.get('limit', 10, type=int)
    status = request.args.get('status')
    
    query = Appointment.query.filter(
        Appointment.patient_id == current_user.id,
        Appointment.datetime < datetime.now()
    )
    
    if status:
        query = query.filter(Appointment.status == status)
    
    appointments = query.order_by(Appointment.datetime.desc()).limit(limit).all()
    
    return jsonify([{
        'id': apt.id,
        'datetime': apt.datetime.strftime('%Y-%m-%d %H:%M'),
        'status': apt.status,
        'doctor': {
            'id': apt.doctor.id,
            'name': apt.doctor.user.name
        },
        'notes': apt.notes,
        'days_ago': (datetime.now() - apt.datetime).days
    } for apt in appointments])

@patient_api_bp.route('/api/patient/doctors', methods=['GET'])
@token_required
def get_doctors(current_user):
    """
    Get Available Doctors API
    ---
    tags:
      - Doctors
    security:
      - Bearer: []
    responses:
      200:
        description: List of available doctors
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              specialization:
                type: string
              email:
                type: string
    """
    doctors = Doctor.query.join(User).filter(User.is_active == True).all()
    
    return jsonify([{
        'id': doctor.id,
        'name': doctor.user.name,
        'specialization': doctor.specialization,
        'email': doctor.user.email
    } for doctor in doctors])

@patient_api_bp.route('/api/patient/cases', methods=['GET'])
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

@patient_api_bp.route('/api/patient/questions', methods=['GET', 'POST'])
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

@patient_api_bp.route('/api/patient/feedback', methods=['POST'])
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
    """
    data = request.get_json()
    
    if not data or not data.get('doctor_id') or not data.get('rating'):
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