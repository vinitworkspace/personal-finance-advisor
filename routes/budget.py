from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, get_current_user
from services.budget_service import BudgetService
from models import Expense

budget_bp = Blueprint('budget', __name__)

@budget_bp.route('/budget', methods=['GET'])
@login_required
def view_budgets():
    """Display category budget management view with overrun warning banners."""
    user = get_current_user()
    
    today = date.today()
    selected_month = request.args.get('month', type=int) or today.month
    selected_year = request.args.get('year', type=int) or today.year

    status = BudgetService.get_budget_status(
        user_id=user.id,
        month=selected_month,
        year=selected_year
    )

    return render_template(
        'budget.html',
        status=status,
        categories=Expense.CATEGORIES,
        selected_month=selected_month,
        selected_year=selected_year
    )

@budget_bp.route('/budget', methods=['POST'])
@login_required
def save_budget():
    """Set or adjust a monthly spending cap for a category."""
    user = get_current_user()
    data = request.get_json(silent=True) if request.is_json else request.form

    category = data.get('category')
    amount = data.get('amount')
    month = data.get('month', type=int) or date.today().month
    year = data.get('year', type=int) or date.today().year

    try:
        budget = BudgetService.set_or_update_budget(
            user_id=user.id,
            category=category,
            amount=amount,
            month=month,
            year=year
        )
        flash(f"Monthly budget for {budget.category} set to {user.currency}{budget.amount:,.2f}.", "success")
        if request.is_json:
            return jsonify({'success': True, 'budget': budget.to_dict()}), 201
        return redirect(url_for('budget.view_budgets', month=month, year=year))
    except ValueError as err:
        if request.is_json:
            return jsonify({'success': False, 'error': str(err)}), 400
        flash(str(err), "danger")
        return redirect(url_for('budget.view_budgets'))

@budget_bp.route('/budget/<int:budget_id>/delete', methods=['POST'])
@login_required
def delete_budget(budget_id: int):
    """Delete a budget allocation owned by the current user."""
    user = get_current_user()
    try:
        BudgetService.delete_budget(budget_id=budget_id, user_id=user.id)
        flash("Budget allocation removed.", "info")
        if request.is_json:
            return jsonify({'success': True, 'message': 'Budget removed'}), 200
        return redirect(url_for('budget.view_budgets'))
    except LookupError as err:
        if request.is_json:
            return jsonify({'success': False, 'error': str(err)}), 404
        flash(str(err), "danger")
        return redirect(url_for('budget.view_budgets'))

@budget_bp.route('/api/budgets/status', methods=['GET'])
@login_required
def api_budget_status():
    """REST endpoint returning calculated budget utilization and threshold alerts."""
    user = get_current_user()
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    status = BudgetService.get_budget_status(user.id, month=month, year=year)
    return jsonify({
        'success': True,
        'status': status
    }), 200
