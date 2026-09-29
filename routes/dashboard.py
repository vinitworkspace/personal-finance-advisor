from datetime import date
from flask import Blueprint, render_template, redirect, url_for
from routes.auth import login_required, get_current_user
from services.finance_service import FinanceService
from services.budget_service import BudgetService
from services.analytics_service import AnalyticsService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def home():
    """Root redirector: sends authenticated users to dashboard, visitors to login."""
    if get_current_user():
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main financial command center view with live aggregated metrics."""
    user = get_current_user()
    today = date.today()

    summary = FinanceService.calculate_monthly_summary(user.id, today.month, today.year)
    budget_status = BudgetService.get_budget_status(user.id, today.month, today.year)
    velocity = AnalyticsService.get_daily_spending_velocity(user.id, today.month, today.year)

    # Fetch recent transactions combining income and expense records
    incomes = FinanceService.get_user_incomes(user.id)[:5]
    expenses = FinanceService.get_user_expenses(user.id)[:5]

    combined_transactions = []
    for inc in incomes:
        combined_transactions.append({
            'type': 'income',
            'title': inc.source,
            'description': inc.description,
            'amount': inc.amount,
            'date': inc.date,
            'category_or_source': inc.source
        })

    for exp in expenses:
        combined_transactions.append({
            'type': 'expense',
            'title': exp.category,
            'description': exp.description,
            'amount': exp.amount,
            'date': exp.date,
            'category_or_source': exp.category
        })

    # Sort recent transactions by date descending
    combined_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = combined_transactions[:6]

    return render_template(
        'dashboard.html',
        user=user,
        summary=summary,
        budget_status=budget_status,
        velocity=velocity,
        recent_transactions=recent_transactions,
        today=today
    )
