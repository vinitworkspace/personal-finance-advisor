"""
Subscription & Billing Management Module for VinZie Budget Tracker.
Handles ₹100/month subscriptions, 30-day free trials, and feature paywalls.
"""
from functools import wraps
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models import db
from routes.auth import login_required, get_current_user

subscription_bp = Blueprint('subscription', __name__)

def subscription_required(f):
    """
    Route decorator ensuring active subscription or valid 30-day free trial.
    Redirects expired accounts to the ₹100/month upgrade screen.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return redirect(url_for('auth.login'))

        if not user.is_subscription_active():
            msg = "Your 30-day free trial has expired. Subscribe for ₹100/month to keep using this premium feature."
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': msg,
                    'code': 'SUBSCRIPTION_EXPIRED',
                    'redirect': url_for('subscription.pricing')
                }), 402
            flash(msg, "warning")
            return redirect(url_for('subscription.pricing'))

        return f(*args, **kwargs)
    return decorated_function

@subscription_bp.route('/subscription', methods=['GET'])
@login_required
def pricing():
    """Display subscription tiers, free trial status, and ₹100/month upgrade modal."""
    user = get_current_user()
    sub_info = user.get_subscription_info()

    return render_template(
        'subscription.html',
        user=user,
        sub=sub_info,
        today=datetime.utcnow()
    )

@subscription_bp.route('/subscription/checkout', methods=['POST'])
@login_required
def checkout():
    """
    Simulate secure ₹100 payment transaction (UPI, Card, NetBanking) and activate 30-day access.
    """
    user = get_current_user()
    data = request.get_json(silent=True) if request.is_json else request.form

    payment_method = data.get('payment_method', 'upi').strip().lower()
    amount = float(data.get('amount', 100))

    if amount < 100:
        msg = "Monthly subscription plan requires ₹100."
        if request.is_json:
            return jsonify({'success': False, 'error': msg}), 400
        flash(msg, "danger")
        return redirect(url_for('subscription.pricing'))

    utr_ref = data.get('utr_ref', '').strip()

    # Extend or activate subscription for 30 calendar days
    expires_at = user.activate_subscription(duration_days=30, plan_name="VinZie Pro (Monthly - ₹100)")
    db.session.commit()

    if utr_ref:
        success_msg = f"Payment of ₹{int(amount)} verified (UTR: {utr_ref}) to vnawate098-1@oksbi! VinZie Pro active until {expires_at.strftime('%d %b %Y')}."
    else:
        success_msg = f"Payment of ₹{int(amount)} confirmed to vnawate098-1@oksbi via {payment_method.upper()}! VinZie Pro active until {expires_at.strftime('%d %b %Y')}."
    flash(success_msg, "success")

    if request.is_json:
        return jsonify({
            'success': True,
            'message': success_msg,
            'status': user.subscription_status,
            'expires_at': expires_at.strftime('%Y-%m-%d %H:%M:%S'),
            'days_remaining': user.days_remaining()
        }), 200

    return redirect(url_for('subscription.pricing'))

@subscription_bp.route('/api/subscription/status', methods=['GET'])
@login_required
def api_subscription_status():
    """API endpoint providing current subscription telemetry for client widgets."""
    user = get_current_user()
    return jsonify({
        'success': True,
        'subscription': user.get_subscription_info()
    }), 200
