from datetime import date
from flask import Blueprint, render_template, request, jsonify
from routes.auth import login_required, get_current_user
from services.finance_service import FinanceService
from services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics', methods=['GET'])
@login_required
def view_analytics():
    """Deep-dive financial analytics and trend visualization view."""
    user = get_current_user()
    today = date.today()
    selected_month = request.args.get('month', type=int) or today.month
    selected_year = request.args.get('year', type=int) or today.year

    summary = FinanceService.calculate_monthly_summary(user.id, selected_month, selected_year)
    velocity = AnalyticsService.get_daily_spending_velocity(user.id, selected_month, selected_year)
    distribution = AnalyticsService.get_category_distribution(user.id, selected_month, selected_year)
    insights = AnalyticsService.get_spending_insights(user.id, selected_month, selected_year)
    trends = AnalyticsService.get_monthly_trends(user.id, months_count=6)

    return render_template(
        'analytics.html',
        summary=summary,
        velocity=velocity,
        distribution=distribution,
        insights=insights,
        trends=trends,
        selected_month=selected_month,
        selected_year=selected_year
    )

@analytics_bp.route('/api/analytics/charts', methods=['GET'])
@login_required
def api_analytics_charts():
    """REST endpoint returning chart-ready data payloads for Chart.js."""
    user = get_current_user()
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    distribution = AnalyticsService.get_category_distribution(user.id, month, year)
    trends = AnalyticsService.get_monthly_trends(user.id, months_count=6)
    velocity = AnalyticsService.get_daily_spending_velocity(user.id, month, year)

    return jsonify({
        'success': True,
        'category_chart': distribution,
        'trend_chart': trends,
        'velocity': velocity
    }), 200
