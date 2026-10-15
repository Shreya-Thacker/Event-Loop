from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Represents a registered student user."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    registrations = db.relationship('Registration', backref='user', lazy=True)
    saved_events = db.relationship('SavedEvent', backref='user', lazy=True)

    def get_id(self):
        return f"user_{self.id}"

    @property
    def is_student(self):
        return False

    def __repr__(self):
        return f'<User {self.username}>'


# ═══════════════════════════════════════════════════════════════════════════════
# Student Admission & Registration Models (Mini Project Requirements)
# ═══════════════════════════════════════════════════════════════════════════════

class StudentLogin(UserMixin, db.Model):
    """
    1. Student Login Table:
    Contains login credentials and authentication state for newly admitted students.
    """
    __tablename__ = 'student_login'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), unique=True, nullable=False) # e.g. STU2026-0001
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    registration = db.relationship('StudentRegistration', backref='student_login', uselist=False, cascade='all, delete-orphan')
    documents = db.relationship('DocumentTrack', backref='student_login', lazy=True, cascade='all, delete-orphan')

    def get_id(self):
        return f"student_{self.id}"

    @property
    def is_student(self):
        return True

    def __repr__(self):
        return f'<StudentLogin {self.username} ({self.student_id})>'


class StudentRegistration(db.Model):
    """
    2. Student Registration Table:
    Contains all the admission and personal information provided by the student through the registration page.
    """
    __tablename__ = 'student_registration'

    id = db.Column(db.Integer, primary_key=True)
    student_login_id = db.Column(db.Integer, db.ForeignKey('student_login.id'), unique=True, nullable=False)
    application_no = db.Column(db.String(50), unique=True, nullable=False)

    # Personal Information
    full_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(10), nullable=True)
    nationality = db.Column(db.String(50), default='Indian')
    mother_tongue = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(50), default='General') # General / OBC / SC / ST / EWS

    # Contact Details
    phone_number = db.Column(db.String(20), nullable=True)
    alternate_phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    permanent_address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), default='Gujarat')
    pincode = db.Column(db.String(20), nullable=True)

    # Parent / Guardian Details
    father_name = db.Column(db.String(150), nullable=True)
    mother_name = db.Column(db.String(150), nullable=True)
    guardian_phone = db.Column(db.String(20), nullable=True)
    guardian_occupation = db.Column(db.String(100), nullable=True)
    family_income = db.Column(db.String(50), nullable=True)

    # Academic & College Details (EventLoop Campus Platform)
    college_name = db.Column(db.String(150), default='ADIT - A.D. Patel Institute of Technology')
    enrollment_no = db.Column(db.String(50), nullable=True) # e.g. 230010116001
    course_enrolled = db.Column(db.String(150), nullable=True) # e.g. B.Tech Computer Engineering
    department = db.Column(db.String(100), nullable=True)
    academic_year = db.Column(db.String(20), default='2026-2027')
    admission_category = db.Column(db.String(50), default='Merit') # Merit / ACPC, Management, NRI, TFWS
    semester = db.Column(db.String(20), default='1st Semester')
    primary_interests = db.Column(db.String(200), nullable=True) # e.g. Hackathon, Workshop, Tech Talk
    skills = db.Column(db.String(250), nullable=True) # e.g. Python, AI, Public Speaking

    # Prior Educational Qualifications
    tenth_board = db.Column(db.String(100), nullable=True)
    tenth_percentage = db.Column(db.Float, nullable=True)
    tenth_passing_year = db.Column(db.Integer, nullable=True)

    twelfth_board = db.Column(db.String(100), nullable=True)
    twelfth_percentage = db.Column(db.Float, nullable=True)
    twelfth_passing_year = db.Column(db.Integer, nullable=True)

    entrance_exam_name = db.Column(db.String(50), nullable=True) # GUJCET / JEE Main / Other
    entrance_exam_roll = db.Column(db.String(50), nullable=True)
    entrance_exam_score = db.Column(db.Float, nullable=True)

    # Registration Status & Tracking
    registration_status = db.Column(db.String(30), default='Draft') # 'Draft', 'Submitted', 'Verified', 'Approved'
    submission_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to DocumentTrack
    documents = db.relationship('DocumentTrack', backref='registration', lazy=True)

    def __repr__(self):
        return f'<StudentRegistration app={self.application_no} student={self.full_name}>'


class DocumentTrack(db.Model):
    """
    3. Document Track Table:
    This table contains a track of documents uploaded by the student.
    """
    __tablename__ = 'document_track'

    id = db.Column(db.Integer, primary_key=True)
    student_login_id = db.Column(db.Integer, db.ForeignKey('student_login.id'), nullable=False)
    student_registration_id = db.Column(db.Integer, db.ForeignKey('student_registration.id'), nullable=True)

    document_type = db.Column(db.String(100), nullable=False) 
    # e.g. '10th Marksheet', '12th Marksheet', 'Entrance Exam Scorecard', 'School Leaving Certificate', 'Aadhaar Card / ID Proof', 'Passport Photo', 'Signature Specimen'

    original_filename = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    file_size_kb = db.Column(db.Float, nullable=False, default=0.0)
    mime_type = db.Column(db.String(100), nullable=True)
    upload_status = db.Column(db.String(50), default='Uploaded') # 'Uploaded', 'Under Verification', 'Verified', 'Rejected'
    remarks = db.Column(db.Text, nullable=True)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DocumentTrack {self.document_type} file={self.file_name} status={self.upload_status}>'



class Event(db.Model):
    """Represents a campus/community event."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)       # e.g. Workshop, Hackathon, Sports
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=50)
    image_url = db.Column(db.String(300), nullable=True)      # Optional banner image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    organizer = db.relationship('User', foreign_keys=[created_by], backref='organized_events')
    registrations = db.relationship('Registration', backref='event', lazy=True)
    saved_by = db.relationship('SavedEvent', backref='event', lazy=True)

    @property
    def spots_left(self):
        return self.capacity - len(self.registrations)

    @property
    def is_full(self):
        return self.spots_left <= 0

    def __repr__(self):
        return f'<Event {self.title}>'


class Registration(db.Model):
    """Tracks which user registered for which event (CRUD: participate history)."""
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Registration user={self.user_id} event={self.event_id}>'


class SavedEvent(db.Model):
    """Tracks events bookmarked/saved by a user."""
    __tablename__ = 'saved_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedEvent user={self.user_id} event={self.event_id}>'
