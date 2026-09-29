from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, get_current_user
from services.finance_service import FinanceService
from models import Expense

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/expenses', methods=['GET'])
@login_required
def list_expenses():
    """Display user expense ledger with category and date filtering."""
    user = get_current_user()
    
    today = date.today()
    selected_month = request.args.get('month', type=int) or today.month
    selected_year = request.args.get('year', type=int) or today.year
    selected_category = request.args.get('category', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None

    expenses = FinanceService.get_user_expenses(
        user_id=user.id,
        month=selected_month,
        year=selected_year,
        category=selected_category,
        start_date=start_date,
        end_date=end_date
    )

    summary = FinanceService.calculate_monthly_summary(
        user_id=user.id,
        month=selected_month,
        year=selected_year
    )

    return render_template(
        'expenses.html',
        expenses=expenses,
        summary=summary,
        categories=Expense.CATEGORIES,
        payment_methods=Expense.PAYMENT_METHODS,
        selected_month=selected_month,
        selected_year=selected_year,
        selected_category=selected_category or '',
        start_date=start_date or '',
        end_date=end_date or ''
    )

@expenses_bp.route('/expenses', methods=['POST'])
@login_required
def add_expense():
    """Create a new expense transaction."""
    user = get_current_user()
    data = request.get_json(silent=True) if request.is_json else request.form

    amount = data.get('amount')
    category = data.get('category')
    date_val = data.get('date')
    description = data.get('description', '')
    payment_method = data.get('payment_method', 'UPI/Card')

    try:
        expense = FinanceService.create_expense(
            user_id=user.id,
            amount=amount,
            category=category,
            date_val=date_val,
            description=description,
            payment_method=payment_method
        )
        flash(f"Recorded expense of {user.currency}{expense.amount:,.2f} for {expense.category}.", "success")
        if request.is_json:
            return jsonify({'success': True, 'expense': expense.to_dict()}), 201
        return redirect(url_for('expenses.list_expenses', month=expense.date.month, year=expense.date.year))
    except ValueError as err:
        if request.is_json:
            return jsonify({'success': False, 'error': str(err)}), 400
        flash(str(err), "danger")
        return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/expenses/<int:expense_id>/edit', methods=['POST'])
@login_required
def edit_expense(expense_id: int):
    """Modify an existing expense entry strictly owned by the current user."""
    user = get_current_user()
    data = request.get_json(silent=True) if request.is_json else request.form

    try:
        updated = FinanceService.update_expense(
            expense_id=expense_id,
            user_id=user.id,
            amount=data.get('amount'),
            category=data.get('category'),
            date_val=data.get('date'),
            description=data.get('description', ''),
            payment_method=data.get('payment_method', 'UPI/Card')
        )
        flash("Expense transaction updated successfully.", "success")
        if request.is_json:
            return jsonify({'success': True, 'expense': updated.to_dict()}), 200
        return redirect(url_for('expenses.list_expenses', month=updated.date.month, year=updated.date.year))
    except (ValueError, LookupError) as err:
        if request.is_json:
            return jsonify({'success': False, 'error': str(err)}), 400
        flash(str(err), "danger")
        return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/expenses/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(expense_id: int):
    """Delete an expense entry owned by the current user."""
    user = get_current_user()
    try:
        FinanceService.delete_expense(expense_id=expense_id, user_id=user.id)
        flash("Expense entry removed successfully.", "info")
        if request.is_json:
            return jsonify({'success': True, 'message': 'Deleted successfully'}), 200
        return redirect(url_for('expenses.list_expenses'))
    except LookupError as err:
        if request.is_json:
            return jsonify({'success': False, 'error': str(err)}), 404
        flash(str(err), "danger")
        return redirect(url_for('expenses.list_expenses'))

@expenses_bp.route('/api/expenses', methods=['GET'])
@login_required
def api_list_expenses():
    """REST endpoint returning expense items in JSON format."""
    user = get_current_user()
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    category = request.args.get('category', '').strip() or None
    start_date = request.args.get('start_date', '').strip() or None
    end_date = request.args.get('end_date', '').strip() or None

    expenses = FinanceService.get_user_expenses(
        user.id,
        month=month,
        year=year,
        category=category,
        start_date=start_date,
        end_date=end_date
    )
    return jsonify({
        'success': True,
        'count': len(expenses),
        'expenses': [exp.to_dict() for exp in expenses]
    }), 200
