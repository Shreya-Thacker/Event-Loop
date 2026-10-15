from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db, User, StudentLogin

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# ── Register ──────────────────────────────────────────────────────────────────
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Server-side validation
        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters.')
        if not email or '@' not in email:
            errors.append('Please enter a valid email address.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm:
            errors.append('Passwords do not match.')
        if User.query.filter_by(username=username).first() or StudentLogin.query.filter_by(username=username).first():
            errors.append('Username already taken.')
        if User.query.filter_by(email=email).first() or StudentLogin.query.filter_by(email=email).first():
            errors.append('Email already registered.')

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('auth/register.html',
                                   username=username, email=email)

        # Create user
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# ── Login ─────────────────────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        # If not found in User, check StudentLogin
        if not user:
            student = StudentLogin.query.filter(
                (StudentLogin.email == email) |
                (StudentLogin.username == email) |
                (StudentLogin.student_id == email)
            ).first()
            if student and check_password_hash(student.password_hash, password):
                student.last_login = datetime.utcnow()
                db.session.commit()
                login_user(student, remember=remember)
                flash(f'Welcome to the Student Admission Portal, {student.username}!', 'success')
                return redirect(url_for('student.dashboard'))

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', email=email)

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.username}!', 'success')

        # Redirect to page the user came from, or home
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))

    return render_template('auth/login.html')


# ── Aliases for Student Admission Portal routes ───────────────────────────────
@auth_bp.route('/student-signup')
def student_signup_alias():
    return redirect(url_for('student.signup'))

@auth_bp.route('/student-login')
def student_login_alias():
    return redirect(url_for('student.login'))

@auth_bp.route('/forgot-password')
def forgot_password_alias():
    return redirect(url_for('student.forgot_password'))


# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))
