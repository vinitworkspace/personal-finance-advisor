from datetime import date
from flask import Blueprint, render_template, request, jsonify
from routes.auth import login_required, get_current_user
from routes.subscription import subscription_required
from services.finance_service import FinanceService
from services.budget_service import BudgetService
from services.analytics_service import AnalyticsService
from services.gemini_service import GeminiService

ai_bp = Blueprint('ai', __name__)

def _build_user_financial_context(user_id: int, month: int = None, year: int = None) -> dict:
    """Build structured, aggregated financial context for AI grounding (no private user secrets)."""
    user = get_current_user()
    target_month = month or date.today().month
    target_year = year or date.today().year

    summary = FinanceService.calculate_monthly_summary(user_id, target_month, target_year)
    velocity = AnalyticsService.get_daily_spending_velocity(user_id, target_month, target_year)
    budget_status = BudgetService.get_budget_status(user_id, target_month, target_year)

    return {
        'currency': user.currency,
        'user_name': user.name,
        'month': target_month,
        'year': target_year,
        'total_income': summary['total_income'],
        'total_expenses': summary['total_expenses'],
        'net_balance': summary['net_balance'],
        'savings_percentage': summary['savings_percentage'],
        'category_breakdown': summary['category_breakdown'],
        'income_sources': summary['income_sources'],
        'average_daily_spend': velocity['average_daily_spend'],
        'projected_spend': velocity['projected_spend'],
        'alerts': [a['message'] for a in budget_status.get('alerts', [])]
    }

@ai_bp.route('/advisor', methods=['GET'])
@login_required
@subscription_required
def view_advisor():
    """Interactive conversational AI Financial Advisor interface."""
    user = get_current_user()
    today = date.today()
    summary = FinanceService.calculate_monthly_summary(user.id, today.month, today.year)

    return render_template(
        'advisor.html',
        summary=summary,
        today=today
    )

@ai_bp.route('/api/ai/categorize', methods=['POST'])
@login_required
def api_categorize():
    """Predict and categorize expense from a plain-text description."""
    data = request.get_json(silent=True) or {}
    description = data.get('description', '').strip()

    if not description:
        return jsonify({'success': False, 'error': 'Description is required'}), 400

    result = GeminiService.categorize_expense(description)
    return jsonify({
        'success': True,
        'description': description,
        'category': result['category'],
        'confidence': result['confidence'],
        'source': result['source']
    }), 200

@ai_bp.route('/api/ai/advice', methods=['POST'])
@login_required
def api_generate_advice():
    """Generate structured monthly financial recommendations and saving strategies."""
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    raw_month = data.get('month')
    raw_year = data.get('year')
    try:
        month = int(raw_month) if raw_month else date.today().month
    except (ValueError, TypeError):
        month = date.today().month

    try:
        year = int(raw_year) if raw_year else date.today().year
    except (ValueError, TypeError):
        year = date.today().year

    context = _build_user_financial_context(user.id, month, year)
    advice_markdown = GeminiService.generate_financial_advice(context)

    return jsonify({
        'success': True,
        'month': month,
        'year': year,
        'advice': advice_markdown
    }), 200

@ai_bp.route('/api/ai/chat', methods=['POST'])
@login_required
@subscription_required
def api_chat():
    """Interactive natural language financial Q&A grounded in user data."""
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    message = data.get('message', '').strip()
    
    raw_month = data.get('month')
    raw_year = data.get('year')
    try:
        month = int(raw_month) if raw_month else date.today().month
    except (ValueError, TypeError):
        month = date.today().month

    try:
        year = int(raw_year) if raw_year else date.today().year
    except (ValueError, TypeError):
        year = date.today().year

    if not message:
        return jsonify({'success': False, 'error': 'Message cannot be empty'}), 400

    context = _build_user_financial_context(user.id, month, year)
    reply = GeminiService.chat_with_advisor(message, context)

    return jsonify({
        'success': True,
        'reply': reply
    }), 200
