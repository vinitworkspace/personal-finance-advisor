from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, g
from models import db, User

auth_bp = Blueprint('auth', __name__)

def get_current_user():
    """Retrieve currently authenticated user from session or request cache."""
    if 'user_id' not in session:
        return None
    if not hasattr(g, 'current_user') or g.current_user is None:
        g.current_user = db.session.get(User, session['user_id'])
    return g.current_user

def login_required(f):
    """Decorator ensuring that only authenticated users can access the endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            # Handle API/JSON requests
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({'error': 'Unauthorized. Please log in to proceed.', 'status': 401}), 401
            
            # Handle browser page requests
            flash("Please sign in to access your financial dashboard.", "warning")
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration with client/server validation."""
    if get_current_user():
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        # Accept JSON or Form submissions
        data = request.get_json(silent=True) if request.is_json else request.form
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        currency = data.get('currency', '₹').strip() or '₹'

        errors = []
        if not name or len(name) < 2:
            errors.append("Please provide a valid full name (minimum 2 characters).")
        if not email or '@' not in email or '.' not in email:
            errors.append("Please provide a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if errors:
            if request.is_json:
                return jsonify({'success': False, 'errors': errors}), 400
            for err in errors:
                flash(err, "danger")
            return render_template('register.html', name=name, email=email, currency=currency)

        # Check for duplicate email
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            msg = "An account with this email address already exists. Please sign in."
            if request.is_json:
                return jsonify({'success': False, 'errors': [msg]}), 400
            flash(msg, "warning")
            return render_template('register.html', name=name, email=email, currency=currency)

        try:
            new_user = User(name=name, email=email, currency=currency)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            # Initialize session for new user
            session.clear()
            session['user_id'] = new_user.id
            session.permanent = True

            flash("Account registered successfully! Welcome to your Personal Finance Advisor.", "success")
            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('dashboard.index')}), 201
            return redirect(url_for('dashboard.index'))

        except Exception as e:
            db.session.rollback()
            msg = "Failed to create account due to a database error. Please try again."
            if request.is_json:
                return jsonify({'success': False, 'errors': [msg]}), 500
            flash(msg, "danger")
            return render_template('register.html', name=name, email=email, currency=currency)

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate user and initialize session."""
    if get_current_user():
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        data = request.get_json(silent=True) if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = bool(data.get('remember'))

        if not email or not password:
            msg = "Please enter both email and password."
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 400
            flash(msg, "danger")
            return render_template('login.html', email=email)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            msg = "Invalid email or password. Please verify your credentials."
            if request.is_json:
                return jsonify({'success': False, 'error': msg}), 401
            flash(msg, "danger")
            return render_template('login.html', email=email)

        # Authentication succeeded: reset session to prevent session fixation
        session.clear()
        session['user_id'] = user.id
        session.permanent = remember

        next_page = request.args.get('next')
        # Validate next_page to prevent open redirect vulnerabilities
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard.index')

        flash(f"Welcome back, {user.name}!", "success")
        if request.is_json:
            return jsonify({'success': True, 'redirect': next_page}), 200
        return redirect(next_page)

    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Terminate user session and clear security tokens."""
    session.clear()
    flash("You have been signed out safely.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/api/auth/me', methods=['GET'])
@login_required
def get_current_user_profile():
    """Return JSON representation of authenticated user."""
    user = get_current_user()
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200
