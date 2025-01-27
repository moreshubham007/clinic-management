from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    google_id = db.Column(db.String(100), unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    
    # Patient-specific fields
    address = db.Column(db.Text)
    state = db.Column(db.String(50))  # Indian state
    city = db.Column(db.String(50))   # City name
    pin_code = db.Column(db.String(6))  # 6-digit Indian PIN code
    mobile_number = db.Column(db.String(15))  # Format: +91-XXXXXXXXXX
    date_of_birth = db.Column(db.Date)
    aadhar_number = db.Column(db.String(12), unique=True)  # 12-digit Aadhar number
    patient_number = db.Column(db.String(11), unique=True)  # Format: INRI-XXXXX
    gender = db.Column(db.String(10))  # male, female, other
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', 
                                 foreign_keys='Appointment.patient_id')
    cases = db.relationship('Case', backref='patient',
                          foreign_keys='Case.patient_id')
    questions = db.relationship('Question', backref='patient',
                             foreign_keys='Question.patient_id')
    feedback_given = db.relationship('Feedback', backref='patient',
                                  foreign_keys='Feedback.patient_id')

    def set_password(self, password):
        """Set the password hash for the user."""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialization = db.Column(db.String(100))
    availability = db.Column(db.JSON)
    user = db.relationship('User', backref=db.backref('doctor', uselist=False))
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor',
                                foreign_keys='Appointment.doctor_id')
    cases = db.relationship('Case', backref='doctor',
                         foreign_keys='Case.doctor_id')
    questions_received = db.relationship('Question', backref='doctor',
                                     foreign_keys='Question.doctor_id')
    feedback_received = db.relationship('Feedback', backref='doctor',
                                    foreign_keys='Feedback.doctor_id')

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)  # Administrative notes
    remarks = db.Column(db.Text)  # Doctor's remarks for the patient
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    show_to_patient = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')  # active, closed, transferred
    
    history = db.relationship('CaseHistory', backref='case', lazy='dynamic')
    attachments = db.relationship('CaseAttachment', backref='case', lazy='dynamic', cascade='all, delete-orphan')

class CaseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    
    doctor = db.relationship('Doctor', backref='case_history')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    answered_at = db.Column(db.DateTime)
    is_private = db.Column(db.Boolean, default=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    rating = db.Column(db.Integer)  # 1-5 rating
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    is_anonymous = db.Column(db.Boolean, default=False)

class CaseAttachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # e.g., 'pdf', 'doc', 'image'
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    uploaded_at = db.Column(db.DateTime, default=lambda: datetime.now())
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    uploaded_by = db.relationship('User', backref='uploaded_attachments')

class CaseTransfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    from_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    to_doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transfer_reason = db.Column(db.Text)
    transfer_notes = db.Column(db.Text)
    patient_condition = db.Column(db.Text)
    patient_history = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    transfer_priority = db.Column(db.String(20))  # urgent, normal, low
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(), onupdate=lambda: datetime.now())
    
    # Relationships
    case = db.relationship('Case', backref='transfers')
    from_doctor = db.relationship('Doctor', foreign_keys=[from_doctor_id], backref='transfers_sent')
    to_doctor = db.relationship('Doctor', foreign_keys=[to_doctor_id], backref='transfers_received')
    patient = db.relationship('User', foreign_keys=[patient_id], backref='case_transfers') 