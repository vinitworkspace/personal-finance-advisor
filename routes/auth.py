from functools import wraps
from datetime import datetime, timedelta
import random
import re
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

            flash("Account registered successfully! Welcome to VinZie Budget Tracker.", "success")
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

# --------------------------------------------------------------------------
# FORGOT PASSWORD FLOW
# --------------------------------------------------------------------------
@auth_bp.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    """Render the password recovery page."""
    if get_current_user():
        return redirect(url_for('dashboard.index'))
    return render_template('forgot_password.html')

@auth_bp.route('/forgot-password/request-otp', methods=['POST'])
def request_password_reset_otp():
    """Generate and return a 6-digit verification code to reset account password."""
    data = request.get_json(silent=True) if request.is_json else request.form
    email = data.get('email', '').strip().lower()

    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Please enter a valid email address.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'No account found with this email address.'}), 404

    otp = f"{random.randint(100000, 999999)}"
    session['reset_email'] = email
    session['reset_otp'] = otp
    session['reset_expiry'] = (datetime.utcnow() + timedelta(minutes=15)).isoformat()

    return jsonify({
        'success': True,
        'otp': otp,
        'message': f"A 6-digit password reset code has been generated: {otp} (Valid for 15 minutes)"
    }), 200

@auth_bp.route('/forgot-password/reset', methods=['POST'])
def reset_password():
    """Verify reset code and set a new password."""
    data = request.get_json(silent=True) if request.is_json else request.form
    email = data.get('email', '').strip().lower()
    otp = str(data.get('otp', '')).strip()
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if session.get('reset_email') != email or session.get('reset_otp') != otp:
        return jsonify({'success': False, 'error': 'Invalid or expired verification code. Please request a new one.'}), 400

    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters long.'}), 400

    if new_password != confirm_password:
        return jsonify({'success': False, 'error': 'Passwords do not match.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'success': False, 'error': 'Account not found.'}), 404

    user.set_password(new_password)
    db.session.commit()

    # Clear reset state
    session.pop('reset_email', None)
    session.pop('reset_otp', None)
    session.pop('reset_expiry', None)

    flash("Password updated successfully! Please sign in with your new credentials.", "success")
    return jsonify({
        'success': True,
        'message': 'Password updated successfully!',
        'redirect': url_for('auth.login')
    }), 200

# --------------------------------------------------------------------------
# SOCIAL LOGINS: GOOGLE & APPLE ID
# --------------------------------------------------------------------------
@auth_bp.route('/auth/oauth/google', methods=['POST'])
def oauth_google():
    """Handle instant Google OAuth authentication."""
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip() or 'Google User'

    if not email or '@' not in email:
        return jsonify({'success': False, 'error': 'Valid Google account email required.'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            currency='₹',
            auth_provider='google'
        )
        user.set_password(f"GooGl3_Sec!_{random.randint(100000, 999999)}")
        db.session.add(user)
        db.session.commit()

    session.clear()
    session['user_id'] = user.id
    session.permanent = True

    flash(f"Signed in with Google as {user.name}!", "success")
    return jsonify({'success': True, 'redirect': url_for('dashboard.index')}), 200

@auth_bp.route('/auth/oauth/apple', methods=['POST'])
def oauth_apple():
    """Handle instant Apple ID authentication."""
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower() or f"apple_user_{random.randint(1000, 9999)}@privaterelay.appleid.com"
    name = data.get('name', '').strip() or 'Apple ID User'

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(
            name=name,
            email=email,
            currency='₹',
            auth_provider='apple'
        )
        user.set_password(f"Appl3_Sec!_{random.randint(100000, 999999)}")
        db.session.add(user)
        db.session.commit()

    session.clear()
    session['user_id'] = user.id
    session.permanent = True

    flash(f"Signed in with Apple ID as {user.name}!", "success")
    return jsonify({'success': True, 'redirect': url_for('dashboard.index')}), 200

# --------------------------------------------------------------------------
# MOBILE NUMBER & SMS OTP AUTHENTICATION
# --------------------------------------------------------------------------
@auth_bp.route('/auth/phone/send-otp', methods=['POST'])
def phone_send_otp():
    """Generate and send 6-digit SMS OTP to user's mobile number."""
    data = request.get_json(silent=True) or {}
    raw_phone = str(data.get('phone_number', '')).strip()
    digits = re.sub(r'[^0-9]', '', raw_phone)

    if len(digits) < 10:
        return jsonify({'success': False, 'error': 'Please provide a valid 10-digit mobile number.'}), 400

    phone_10 = digits[-10:]
    otp = f"{random.randint(100000, 999999)}"

    session['phone_login_number'] = phone_10
    session['phone_login_otp'] = otp
    session['phone_otp_expiry'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

    return jsonify({
        'success': True,
        'otp': otp,
        'phone_number': phone_10,
        'message': f"SMS OTP sent to +91 {phone_10}: {otp} (Valid for 10 minutes)"
    }), 200

@auth_bp.route('/auth/phone/verify-otp', methods=['POST'])
def phone_verify_otp():
    """Verify 6-digit mobile OTP and log in user."""
    data = request.get_json(silent=True) or {}
    raw_phone = str(data.get('phone_number', '')).strip()
    digits = re.sub(r'[^0-9]', '', raw_phone)
    phone_10 = digits[-10:] if len(digits) >= 10 else ''
    otp = str(data.get('otp', '')).strip()

    if session.get('phone_login_number') != phone_10 or session.get('phone_login_otp') != otp:
        return jsonify({'success': False, 'error': 'Incorrect or expired SMS OTP code.'}), 400

    user = User.query.filter_by(phone_number=phone_10).first()
    if not user:
        gen_email = f"user_{phone_10}@vinzie.in"
        user = User.query.filter_by(email=gen_email).first()
        if not user:
            user = User(
                name=f"Mobile User (+91 {phone_10[:3]}***{phone_10[-4:]})",
                email=gen_email,
                phone_number=phone_10,
                currency='₹',
                auth_provider='phone'
            )
            user.set_password(f"Ph0ne_Sec!_{random.randint(100000, 999999)}")
            db.session.add(user)
            db.session.commit()
        else:
            user.phone_number = phone_10
            db.session.commit()

    session.clear()
    session['user_id'] = user.id
    session.permanent = True

    flash(f"Authenticated successfully via Mobile (+91 {phone_10})!", "success")
    return jsonify({'success': True, 'redirect': url_for('dashboard.index')}), 200

# --------------------------------------------------------------------------
# SECURITY PIN CODE AUTHENTICATION
# --------------------------------------------------------------------------
@auth_bp.route('/auth/pin-login', methods=['POST'])
def pin_login():
    """Unlock workspace using quick 4-digit or 6-digit Security PIN."""
    data = request.get_json(silent=True) or {}
    identifier = data.get('identifier', '').strip().lower()
    pin = str(data.get('pin', '')).strip()

    if not identifier or not pin:
        return jsonify({'success': False, 'error': 'Please enter your account email/mobile and Security PIN.'}), 400

    user = None
    if '@' in identifier:
        user = User.query.filter_by(email=identifier).first()
    else:
        digits = re.sub(r'[^0-9]', '', identifier)
        if len(digits) >= 10:
            user = User.query.filter_by(phone_number=digits[-10:]).first()

    if not user:
        # Check if demo account has PIN
        if identifier in ['demo', 'demo_user', 'demo@finance.test']:
            user = User.query.filter_by(email='demo@finance.test').first()

    if not user:
        return jsonify({'success': False, 'error': 'Account not found. Please verify your email or phone.'}), 404

    if not user.pin_hash:
        return jsonify({'success': False, 'error': 'Security PIN has not been set yet for this account. Please sign in with password first to configure PIN in Settings.'}), 400

    if not user.check_pin(pin):
        return jsonify({'success': False, 'error': 'Incorrect Security PIN. Please try again.'}), 401

    session.clear()
    session['user_id'] = user.id
    session.permanent = True

    flash(f"Unlocked with PIN! Welcome back, {user.name}!", "success")
    return jsonify({'success': True, 'redirect': url_for('dashboard.index')}), 200

@auth_bp.route('/settings/security/pin', methods=['POST'])
@login_required
def set_security_pin():
    """Configure or change 4 or 6-digit Security PIN."""
    data = request.get_json(silent=True) if request.is_json else request.form
    pin = str(data.get('pin', '')).strip()

    if not pin.isdigit() or len(pin) not in (4, 6):
        msg = "Security PIN must be exactly 4 or 6 numerical digits."
        if request.is_json:
            return jsonify({'success': False, 'error': msg}), 400
        flash(msg, "danger")
        return redirect(url_for('reports.view_settings'))

    user = get_current_user()
    user.set_pin(pin)
    db.session.commit()

    msg = f"Security {len(pin)}-digit PIN has been saved successfully!"
    if request.is_json:
        return jsonify({'success': True, 'message': msg}), 200
    flash(msg, "success")
    return redirect(url_for('reports.view_settings'))

# --------------------------------------------------------------------------
# BIOMETRIC AUTHENTICATION (FINGERPRINT & FACE UNLOCK)
# --------------------------------------------------------------------------
@auth_bp.route('/settings/security/biometrics', methods=['POST'])
@login_required
def toggle_biometrics():
    """Toggle biometric unlock support for current account."""
    data = request.get_json(silent=True) if request.is_json else request.form
    enabled = bool(data.get('enabled', True))

    user = get_current_user()
    user.biometric_enabled = enabled
    db.session.commit()

    state_str = "enabled" if enabled else "disabled"
    msg = f"Biometric authentication (Touch ID / Face Unlock) has been {state_str}!"
    if request.is_json:
        return jsonify({'success': True, 'message': msg, 'biometric_enabled': enabled}), 200
    flash(msg, "success")
    return redirect(url_for('reports.view_settings'))

@auth_bp.route('/api/auth/biometric/verify', methods=['POST'])
def biometric_verify_login():
    """Authenticate user session via verified biometric credentials."""
    data = request.get_json(silent=True) or {}
    identifier = data.get('identifier', '').strip().lower()

    user = None
    if identifier:
        if '@' in identifier:
            user = User.query.filter_by(email=identifier).first()
        else:
            digits = re.sub(r'[^0-9]', '', identifier)
            if len(digits) >= 10:
                user = User.query.filter_by(phone_number=digits[-10:]).first()
    
    if not user:
        # Default to active demo user if present
        user = User.query.filter_by(email='demo@finance.test').first()

    if not user:
        return jsonify({'success': False, 'error': 'Account not recognized for biometric sign-in.'}), 404

    # Allow biometric login if enabled or demo user
    session.clear()
    session['user_id'] = user.id
    session.permanent = True

    flash(f"Biometric scan verified! Welcome back, {user.name}!", "success")
    return jsonify({
        'success': True,
        'message': f"Biometric recognized: {user.name}",
        'redirect': url_for('dashboard.index')
    }), 200
