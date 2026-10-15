import os
import time
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    current_app, send_from_directory, abort
)
from flask_login import login_user, logout_user, login_required, current_user
from models import db, StudentLogin, StudentRegistration, DocumentTrack

student_bp = Blueprint('student', __name__, url_prefix='/student')


def allowed_file(filename):
    allowed_exts = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'png', 'jpg', 'jpeg', 'webp'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


# ── 1. Student Sign-up Page ──────────────────────────────────────────────────
@student_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        if getattr(current_user, 'is_student', False):
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        student_id = request.form.get('student_id', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []
        if not full_name or len(full_name) < 2:
            errors.append('Full Name must be at least 2 characters.')
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Please provide a valid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        # Check uniqueness in student_login table
        if StudentLogin.query.filter_by(username=username).first():
            errors.append('Username is already taken by another student.')
        if StudentLogin.query.filter_by(email=email).first():
            errors.append('Email is already registered. Please login instead.')

        # Generate student ID if not entered
        if not student_id:
            rand_suffix = secrets.token_hex(2).upper()
            student_id = f"STU{datetime.utcnow().year}-{rand_suffix}"
        elif StudentLogin.query.filter_by(student_id=student_id).first():
            errors.append('Student ID is already registered.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'student/signup.html',
                full_name=full_name,
                student_id=student_id,
                username=username,
                email=email,
                phone=phone
            )

        # 1. CRUD Create: Student Login Table
        new_student = StudentLogin(
            student_id=student_id,
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            created_at=datetime.utcnow()
        )
        db.session.add(new_student)
        db.session.flush()  # obtain new_student.id

        # 2. CRUD Create: Initial Student Registration Table Record (Draft)
        app_no = f"ADM{datetime.utcnow().year}-{new_student.id:04d}"
        initial_reg = StudentRegistration(
            student_login_id=new_student.id,
            application_no=app_no,
            full_name=full_name,
            email=email,
            phone_number=phone,
            registration_status='Draft'
        )
        db.session.add(initial_reg)
        db.session.commit()

        flash('Student account created successfully! Please log in to complete your registration.', 'success')
        return redirect(url_for('student.login'))

    return render_template('student/signup.html')


# ── 2. Student Login Page ───────────────────────────────────────────────────
@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if getattr(current_user, 'is_student', False):
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('index'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not identifier or not password:
            flash('Please enter your Student ID / Email and Password.', 'danger')
            return render_template('student/login.html', identifier=identifier)

        # Look up in student_login table by email, username, or student_id
        student = StudentLogin.query.filter(
            (StudentLogin.email == identifier.lower()) |
            (StudentLogin.username == identifier) |
            (StudentLogin.student_id == identifier)
        ).first()

        if not student or not check_password_hash(student.password_hash, password):
            flash('Invalid credentials. Please verify your Student ID/Email and password.', 'danger')
            return render_template('student/login.html', identifier=identifier)

        # Update last login timestamp
        student.last_login = datetime.utcnow()
        db.session.commit()

        login_user(student, remember=remember)
        flash(f'Welcome to the Admission Portal, {student.username}!', 'success')

        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('student.dashboard'))

    return render_template('student/login.html')


# ── 3. Forgot Password Page ─────────────────────────────────────────────────
@student_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated and getattr(current_user, 'is_student', False):
        return redirect(url_for('student.dashboard'))

    step = 'request'
    email_or_id = ''
    reset_code_display = None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'request_code':
            email_or_id = request.form.get('email_or_id', '').strip()
            student = StudentLogin.query.filter(
                (StudentLogin.email == email_or_id.lower()) |
                (StudentLogin.student_id == email_or_id) |
                (StudentLogin.username == email_or_id)
            ).first()

            if not student:
                flash('No student account found with that Email or Student ID.', 'danger')
                return render_template('student/forgot_password.html', step='request', email_or_id=email_or_id)

            # Generate 6-char verification reset code
            code = secrets.token_hex(3).upper()
            student.reset_token = code
            student.reset_token_expiry = datetime.utcnow()
            db.session.commit()

            step = 'reset'
            reset_code_display = code
            flash(f'Verification code generated for {student.email}: {code}', 'info')
            return render_template(
                'student/forgot_password.html',
                step='reset',
                email_or_id=student.email,
                reset_code_display=code
            )

        elif action == 'reset_password':
            email_or_id = request.form.get('email_or_id', '').strip()
            reset_code = request.form.get('reset_code', '').strip().upper()
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')

            student = StudentLogin.query.filter(
                (StudentLogin.email == email_or_id.lower()) |
                (StudentLogin.student_id == email_or_id) |
                (StudentLogin.username == email_or_id)
            ).first()

            if not student:
                flash('Student record not found.', 'danger')
                return render_template('student/forgot_password.html', step='request')

            if not student.reset_token or student.reset_token != reset_code:
                flash('Invalid or expired verification reset code.', 'danger')
                return render_template('student/forgot_password.html', step='reset', email_or_id=email_or_id)

            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'danger')
                return render_template('student/forgot_password.html', step='reset', email_or_id=email_or_id)

            if new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
                return render_template('student/forgot_password.html', step='reset', email_or_id=email_or_id)

            # Update password in student_login table (CRUD Update)
            student.password_hash = generate_password_hash(new_password)
            student.reset_token = None
            student.reset_token_expiry = None
            db.session.commit()

            flash('Password successfully reset! You can now log in with your new credentials.', 'success')
            return redirect(url_for('student.login'))

    return render_template('student/forgot_password.html', step=step, email_or_id=email_or_id)


# ── Helper to ensure student role ───────────────────────────────────────────
def require_student():
    if not current_user.is_authenticated:
        flash('Please login to access the Student Admission Portal.', 'warning')
        return redirect(url_for('student.login'))
    if not getattr(current_user, 'is_student', False):
        flash('This section is dedicated for student applicants.', 'info')
        return redirect(url_for('index'))
    return None


# ── Student Admission Dashboard ─────────────────────────────────────────────
@student_bp.route('/dashboard')
@login_required
def dashboard():
    guard = require_student()
    if guard:
        return guard

    registration = StudentRegistration.query.filter_by(student_login_id=current_user.id).first()
    documents = DocumentTrack.query.filter_by(student_login_id=current_user.id).order_by(DocumentTrack.uploaded_at.desc()).all()

    # Calculate admission completion score
    progress_score = 25  # Account created
    if registration and registration.registration_status in ['Submitted', 'Approved', 'Verified']:
        progress_score += 45
    elif registration and registration.full_name and registration.dob:
        progress_score += 25

    if len(documents) >= 3:
        progress_score += 30
    elif len(documents) > 0:
        progress_score += 15

    progress_score = min(100, progress_score)

    return render_template(
        'student/dashboard.html',
        registration=registration,
        documents=documents,
        progress_score=progress_score
    )


# ── 4. Student Registration Page (CRUD: Create/Read/Update) ──────────────────
@student_bp.route('/registration', methods=['GET', 'POST'])
@login_required
def registration():
    guard = require_student()
    if guard:
        return guard

    # CRUD Read: Fetch existing registration or instantiate one
    reg = StudentRegistration.query.filter_by(student_login_id=current_user.id).first()
    if not reg:
        app_no = f"ADM{datetime.utcnow().year}-{current_user.id:04d}"
        reg = StudentRegistration(
            student_login_id=current_user.id,
            application_no=app_no,
            full_name=current_user.username.replace('_', ' ').title(),
            email=current_user.email,
            phone_number=current_user.phone or '',
            registration_status='Draft'
        )
        db.session.add(reg)
        db.session.commit()

    if request.method == 'POST':
        action = request.form.get('action', 'save_draft')

        # Personal details
        reg.full_name = request.form.get('full_name', '').strip() or reg.full_name
        dob_str = request.form.get('dob', '').strip()
        if dob_str:
            try:
                reg.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        reg.gender = request.form.get('gender', '').strip()
        reg.blood_group = request.form.get('blood_group', '').strip()
        reg.nationality = request.form.get('nationality', 'Indian').strip()
        reg.mother_tongue = request.form.get('mother_tongue', '').strip()
        reg.category = request.form.get('category', 'General').strip()

        # Contact details
        reg.phone_number = request.form.get('phone_number', '').strip()
        reg.alternate_phone = request.form.get('alternate_phone', '').strip()
        reg.email = request.form.get('email', '').strip().lower() or current_user.email
        reg.permanent_address = request.form.get('permanent_address', '').strip()
        reg.city = request.form.get('city', '').strip()
        reg.state = request.form.get('state', '').strip()
        reg.pincode = request.form.get('pincode', '').strip()

        # Guardian details
        reg.father_name = request.form.get('father_name', '').strip()
        reg.mother_name = request.form.get('mother_name', '').strip()
        reg.guardian_phone = request.form.get('guardian_phone', '').strip()
        reg.guardian_occupation = request.form.get('guardian_occupation', '').strip()
        reg.family_income = request.form.get('family_income', '').strip()

        # Academic / Admission details
        reg.course_enrolled = request.form.get('course_enrolled', '').strip()
        reg.department = request.form.get('department', '').strip()
        reg.academic_year = request.form.get('academic_year', '2026-2027').strip()
        reg.admission_category = request.form.get('admission_category', 'Merit').strip()
        reg.semester = request.form.get('semester', '1st Semester').strip()

        # Previous qualifications
        reg.tenth_board = request.form.get('tenth_board', '').strip()
        tenth_pct = request.form.get('tenth_percentage', '').strip()
        reg.tenth_percentage = float(tenth_pct) if tenth_pct else None
        tenth_yr = request.form.get('tenth_passing_year', '').strip()
        reg.tenth_passing_year = int(tenth_yr) if tenth_yr else None

        reg.twelfth_board = request.form.get('twelfth_board', '').strip()
        twelfth_pct = request.form.get('twelfth_percentage', '').strip()
        reg.twelfth_percentage = float(twelfth_pct) if twelfth_pct else None
        twelfth_yr = request.form.get('twelfth_passing_year', '').strip()
        reg.twelfth_passing_year = int(twelfth_yr) if twelfth_yr else None

        reg.entrance_exam_name = request.form.get('entrance_exam_name', '').strip()
        reg.entrance_exam_roll = request.form.get('entrance_exam_roll', '').strip()
        exam_score = request.form.get('entrance_exam_score', '').strip()
        reg.entrance_exam_score = float(exam_score) if exam_score else None

        reg.updated_at = datetime.utcnow()

        # Handle Submit vs Draft
        if action == 'submit_final':
            # Validation check for submission
            if not reg.full_name or not reg.course_enrolled or not reg.phone_number:
                flash('Please fill in Full Name, Phone Number, and Admitted Course before submitting.', 'warning')
                return render_template('student/registration.html', reg=reg)

            reg.registration_status = 'Submitted'
            reg.submission_date = datetime.utcnow()
            db.session.commit()
            flash('Registration form submitted successfully! Now please upload your admission documents.', 'success')
            return redirect(url_for('student.documents'))
        else:
            reg.registration_status = 'Draft'
            db.session.commit()
            flash('Registration draft saved successfully! You can resume editing anytime.', 'info')
            return redirect(url_for('student.registration'))

    return render_template('student/registration.html', reg=reg)


# ── 5. Upload Documents Page (CRUD: Create/Read/Update/Delete) ───────────────
@student_bp.route('/documents', methods=['GET', 'POST'])
@login_required
def documents():
    guard = require_student()
    if guard:
        return guard

    reg = StudentRegistration.query.filter_by(student_login_id=current_user.id).first()

    # CRUD Create: Uploading a new admission document
    if request.method == 'POST':
        document_type = request.form.get('document_type', '').strip()
        remarks = request.form.get('remarks', '').strip()

        if not document_type:
            flash('Please select a Document Type.', 'danger')
            return redirect(url_for('student.documents'))

        if 'document_file' not in request.files:
            flash('No file selected for upload.', 'danger')
            return redirect(url_for('student.documents'))

        file = request.files['document_file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('student.documents'))

        if not allowed_file(file.filename):
            flash('Invalid file format. Allowed formats: PDF, PNG, JPG, JPEG, WEBP.', 'danger')
            return redirect(url_for('student.documents'))

        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)

        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'pdf'
        safe_type = document_type.lower().replace(' ', '_').replace('/', '_')
        unique_name = f"stu_{current_user.id}_{safe_type}_{int(time.time())}.{ext}"
        saved_path = os.path.join(upload_dir, unique_name)
        file.save(saved_path)

        file_size_kb = round(os.path.getsize(saved_path) / 1024, 2)

        # CRUD Create in document_track table
        new_doc = DocumentTrack(
            student_login_id=current_user.id,
            student_registration_id=reg.id if reg else None,
            document_type=document_type,
            original_filename=original_filename,
            file_name=unique_name,
            file_path=os.path.join('uploads', 'documents', unique_name).replace('\\', '/'),
            file_size_kb=file_size_kb,
            mime_type=file.mimetype,
            upload_status='Uploaded',
            remarks=remarks,
            uploaded_at=datetime.utcnow()
        )
        db.session.add(new_doc)
        db.session.commit()

        flash(f"Document '{document_type}' uploaded and recorded successfully!", 'success')
        return redirect(url_for('student.documents'))

    # CRUD Read: List of documents uploaded by the student
    docs = DocumentTrack.query.filter_by(student_login_id=current_user.id).order_by(DocumentTrack.uploaded_at.desc()).all()
    
    # Required documents checklist
    STANDARD_DOCS = [
        '10th Standard Marksheet',
        '12th Standard Marksheet',
        'Entrance Exam Scorecard (GUJCET / JEE)',
        'School Leaving Certificate / Transfer Certificate',
        'Aadhaar Card / Photo ID Proof',
        'Passport Size Photograph',
        'Signature Specimen'
    ]
    uploaded_types = {d.document_type for d in docs}

    return render_template(
        'student/documents.html',
        docs=docs,
        standard_docs=STANDARD_DOCS,
        uploaded_types=uploaded_types,
        reg=reg
    )


# ── CRUD Update: Replace/Update Document ─────────────────────────────────────
@student_bp.route('/documents/<int:doc_id>/update', methods=['POST'])
@login_required
def update_document(doc_id):
    guard = require_student()
    if guard:
        return guard

    doc = DocumentTrack.query.filter_by(id=doc_id, student_login_id=current_user.id).first_or_404()

    remarks = request.form.get('remarks', doc.remarks)
    doc.remarks = remarks

    if 'replace_file' in request.files:
        file = request.files['replace_file']
        if file and file.filename != '' and allowed_file(file.filename):
            upload_dir = current_app.config['UPLOAD_FOLDER']
            # Delete old physical file if exists
            old_file_path = os.path.join(upload_dir, doc.file_name)
            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError:
                    pass

            # Save new file
            original_filename = secure_filename(file.filename)
            ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'pdf'
            safe_type = doc.document_type.lower().replace(' ', '_').replace('/', '_')
            unique_name = f"stu_{current_user.id}_{safe_type}_{int(time.time())}.{ext}"
            new_path = os.path.join(upload_dir, unique_name)
            file.save(new_path)

            doc.original_filename = original_filename
            doc.file_name = unique_name
            doc.file_path = os.path.join('uploads', 'documents', unique_name).replace('\\', '/')
            doc.file_size_kb = round(os.path.getsize(new_path) / 1024, 2)
            doc.mime_type = file.mimetype
            doc.upload_status = 'Uploaded'
            doc.updated_at = datetime.utcnow()

    db.session.commit()
    flash(f"Document '{doc.document_type}' updated successfully.", 'success')
    return redirect(url_for('student.documents'))


# ── CRUD Delete: Delete Document ─────────────────────────────────────────────
@student_bp.route('/documents/<int:doc_id>/delete', methods=['POST'])
@login_required
def delete_document(doc_id):
    guard = require_student()
    if guard:
        return guard

    doc = DocumentTrack.query.filter_by(id=doc_id, student_login_id=current_user.id).first_or_404()
    doc_type = doc.document_type

    # Delete physical file
    upload_dir = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_dir, doc.file_name)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass

    # Delete record from DocumentTrack table
    db.session.delete(doc)
    db.session.commit()

    flash(f"Document '{doc_type}' deleted successfully from track records.", 'info')
    return redirect(url_for('student.documents'))


# ── Document View & Download Handlers ────────────────────────────────────────
@student_bp.route('/documents/<int:doc_id>/view')
@login_required
def view_document(doc_id):
    guard = require_student()
    if guard:
        return guard

    doc = DocumentTrack.query.filter_by(id=doc_id, student_login_id=current_user.id).first_or_404()
    upload_dir = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_dir, doc.file_name, as_attachment=False)


@student_bp.route('/documents/<int:doc_id>/download')
@login_required
def download_document(doc_id):
    guard = require_student()
    if guard:
        return guard

    doc = DocumentTrack.query.filter_by(id=doc_id, student_login_id=current_user.id).first_or_404()
    upload_dir = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_dir, doc.file_name, as_attachment=True, download_name=doc.original_filename)


# ── 6. Edit Current Profile Page (CRUD: Update) ─────────────────────────────
@student_bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    guard = require_student()
    if guard:
        return guard

    student = StudentLogin.query.get(current_user.id)
    reg = StudentRegistration.query.filter_by(student_login_id=current_user.id).first()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            full_name = request.form.get('full_name', '').strip()
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            alternate_phone = request.form.get('alternate_phone', '').strip()
            permanent_address = request.form.get('permanent_address', '').strip()
            city = request.form.get('city', '').strip()
            state = request.form.get('state', '').strip()
            pincode = request.form.get('pincode', '').strip()
            blood_group = request.form.get('blood_group', '').strip()
            gender = request.form.get('gender', '').strip()

            father_name = request.form.get('father_name', '').strip()
            mother_name = request.form.get('mother_name', '').strip()
            guardian_phone = request.form.get('guardian_phone', '').strip()
            guardian_occupation = request.form.get('guardian_occupation', '').strip()
            family_income = request.form.get('family_income', '').strip()

            # Validate username uniqueness if changed
            if username != student.username and StudentLogin.query.filter(StudentLogin.username == username, StudentLogin.id != student.id).first():
                flash('Username is already taken by another account.', 'danger')
                return render_template('student/edit_profile.html', student=student, reg=reg)

            # Validate email uniqueness if changed
            if email != student.email and StudentLogin.query.filter(StudentLogin.email == email, StudentLogin.id != student.id).first():
                flash('Email is already in use by another student.', 'danger')
                return render_template('student/edit_profile.html', student=student, reg=reg)

            # Update student_login table (CRUD Update)
            student.username = username or student.username
            student.email = email or student.email
            student.phone = phone

            # Update student_registration table (CRUD Update)
            if reg:
                reg.full_name = full_name or reg.full_name
                reg.email = student.email
                reg.phone_number = phone
                reg.alternate_phone = alternate_phone
                reg.permanent_address = permanent_address
                reg.city = city
                reg.state = state
                reg.pincode = pincode
                reg.blood_group = blood_group
                reg.gender = gender
                reg.father_name = father_name
                reg.mother_name = mother_name
                reg.guardian_phone = guardian_phone
                reg.guardian_occupation = guardian_occupation
                reg.family_income = family_income
                reg.updated_at = datetime.utcnow()

            db.session.commit()
            flash('Your profile has been updated successfully!', 'success')
            return redirect(url_for('student.edit_profile'))

        elif action == 'change_password':
            current_pass = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_new_pass = request.form.get('confirm_new_password', '')

            if not check_password_hash(student.password_hash, current_pass):
                flash('Current password is incorrect.', 'danger')
                return render_template('student/edit_profile.html', student=student, reg=reg)

            if len(new_pass) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return render_template('student/edit_profile.html', student=student, reg=reg)

            if new_pass != confirm_new_pass:
                flash('New passwords do not match.', 'danger')
                return render_template('student/edit_profile.html', student=student, reg=reg)

            # Update password in student_login
            student.password_hash = generate_password_hash(new_pass)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('student.edit_profile'))

    return render_template('student/edit_profile.html', student=student, reg=reg)


# ── Student Logout ───────────────────────────────────────────────────────────
@student_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out of the Student Admission Portal.', 'info')
    return redirect(url_for('student.login'))
