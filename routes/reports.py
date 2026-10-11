from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify
from routes.auth import login_required, get_current_user
from routes.subscription import subscription_required
from services.finance_service import FinanceService
from services.budget_service import BudgetService
from services.report_service import ReportService
from models import db, User, Income, Expense, Budget

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports', methods=['GET'])
@login_required
def view_reports():
    """Display monthly executive financial report and historical archive."""
    user = get_current_user()
    today = date.today()

    selected_month = request.args.get('month', type=int) or today.month
    selected_year = request.args.get('year', type=int) or today.year

    # Retrieve or compile report snapshot
    report = ReportService.compile_monthly_report(user.id, selected_month, selected_year)
    history = ReportService.get_user_reports(user.id)
    summary = FinanceService.calculate_monthly_summary(user.id, selected_month, selected_year)
    budget_status = BudgetService.get_budget_status(user.id, selected_month, selected_year)

    return render_template(
        'reports.html',
        report=report,
        history=history,
        summary=summary,
        budget_status=budget_status,
        selected_month=selected_month,
        selected_year=selected_year
    )

@reports_bp.route('/reports/generate', methods=['POST'])
@login_required
@subscription_required
def generate_report():
    """Compile and archive a fresh monthly financial snapshot with updated AI advice."""
    user = get_current_user()
    month = request.form.get('month', type=int) or date.today().month
    year = request.form.get('year', type=int) or date.today().year

    report = ReportService.compile_monthly_report(user.id, month, year, regenerate=True)
    flash(f"Compiled and archived monthly financial report for {month}/{year}!", "success")
    return redirect(url_for('reports.view_reports', month=month, year=year))

@reports_bp.route('/reports/export/csv', methods=['GET'])
@login_required
@subscription_required
def export_csv():
    """Download full ledger export in CSV format."""
    user = get_current_user()
    csv_data = ReportService.export_transactions_csv(user.id)

    filename = f"finance_transactions_{user.id}_{date.today().strftime('%Y%m%d')}.csv"
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@reports_bp.route('/settings', methods=['GET'])
@login_required
def view_settings():
    """Display account settings, currency preferences, and demonstration controls."""
    user = get_current_user()
    return render_template('settings.html', user=user)

@reports_bp.route('/settings/currency', methods=['POST'])
@login_required
def update_currency():
    """Update active user preferred currency symbol."""
    user = get_current_user()
    new_currency = request.form.get('currency', '₹').strip()
    if new_currency in ['₹', '$', '€', '£', '¥']:
        user.currency = new_currency
        db.session.commit()
        flash(f"Preferred currency updated to {new_currency}.", "success")
    else:
        flash("Invalid currency selection.", "danger")
    return redirect(url_for('reports.view_settings'))

@reports_bp.route('/settings/reset-demo', methods=['POST'])
@login_required
def reset_demo_data():
    """Reset user transactions to the standard viva demonstration baseline."""
    user = get_current_user()
    today = date.today()

    # Clear current records
    Income.query.filter_by(user_id=user.id).delete()
    Expense.query.filter_by(user_id=user.id).delete()
    Budget.query.filter_by(user_id=user.id).delete()

    # Re-seed baseline transactions (Scenario 1: Salaried Professional)
    db.session.add(Income(user_id=user.id, amount=50000.0, source="Salary", date=today, description="Monthly Primary Salary"))
    db.session.add_all([
        Expense(user_id=user.id, amount=15000.0, category="Rent", date=today, description="Apartment Rent"),
        Expense(user_id=user.id, amount=7000.0, category="Food", date=today, description="Groceries & Dining"),
        Expense(user_id=user.id, amount=3000.0, category="Utilities", date=today, description="High-speed Internet & Power"),
        Expense(user_id=user.id, amount=4000.0, category="Transport", date=today, description="Metro pass & Fuel"),
        Expense(user_id=user.id, amount=3500.0, category="Entertainment", date=today, description="Movies & Streaming")
    ])
    db.session.add(Budget(user_id=user.id, category="Food", amount=6000.0, month=today.month, year=today.year))
    db.session.commit()

    flash("Account successfully reset with standard baseline demonstration data!", "info")
    return redirect(url_for('dashboard.index'))
