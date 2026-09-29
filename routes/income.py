from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from routes.auth import login_required, get_current_user
from services.finance_service import FinanceService
from models import Income

income_bp = Blueprint('income', __name__)

@income_bp.route('/income', methods=['GET'])
@login_required
def list_income():
    """Display user income ledger with date and source filtering."""
    user = get_current_user()
    
    # Extract query filters
    today = date.today()
    selected_month = request.args.get('month', type=int) or today.month
    selected_year = request.args.get('year', type=int) or today.year
    selected_source = request.args.get('source', '').strip() or None

    incomes = FinanceService.get_user_incomes(
        user_id=user.id,
        month=selected_month,
        year=selected_year,
        source=selected_source
    )
    
    summary = FinanceService.calculate_monthly_summary(
        user_id=user.id,
        month=selected_month,
        year=selected_year
    )

    return render_template(
        'income.html',
        incomes=incomes,
        summary=summary,
        sources=Income.SOURCES,
        selected_month=selected_month,
        selected_year=selected_year,
        selected_source=selected_source or ''
    )

@income_bp.route('/income', methods=['POST'])
@login_required
def add_income():
    """Create a new income entry."""
    user = get_current_user()
    data = request.get_json(silent=True) if request.is_json else request.form

    amount = data.get('amount')
    source = data.get('source')
    date_val = data.get('date')
    description = data.get('description', '')

    try:
        income = FinanceService.create_income(
            user_id=user.id,
            amount=amount,
            source=source,
            date_val=date_val,
            description=description
        )
        flash(f"Successfully recorded income of {user.currency}{income.amount:,.2f} from {income.source}!", "success")
        if request.is_json:
            return jsonify({'success': True, 'income': income.to_dict()}), 201
        return redirect(url_for('income.list_income', month=income.date.month, year=income.date.year))
    except ValueError as err:
        if request.is_json:
            return jsonify({'success': False, 'error': str(err)}), 400
        flash(str(err), "danger")
        return redirect(url_for('income.list_income'))

@income_bp.route('/income/<int:income_id>/edit', methods=['POST'])
@login_required
def edit_income(income_id: int):
    """Modify an existing income entry strictly owned by the current user."""
    user = get_current_user()
    data = request.get_json(silent=True) if request.is_json else request.form

    try:
        updated = FinanceService.update_income(
            income_id=income_id,
            user_id=user.id,
            amount=data.get('amount'),
            source=data.get('source'),
            date_val=data.get('date'),
            description=data.get('description', '')
        )
        flash("Income record updated successfully.", "success")
        if request.is_json:
            return jsonify({'success': True, 'income': updated.to_dict()}), 200
        return redirect(url_for('income.list_income', month=updated.date.month, year=updated.date.year))
    except (ValueError, LookupError) as err:
        if request.is_json:
            return jsonify({'success': False, 'error': str(err)}), 400
        flash(str(err), "danger")
        return redirect(url_for('income.list_income'))

@income_bp.route('/income/<int:income_id>/delete', methods=['POST'])
@login_required
def delete_income(income_id: int):
    """Delete an income entry owned by the current user."""
    user = get_current_user()
    try:
        FinanceService.delete_income(income_id=income_id, user_id=user.id)
        flash("Income entry deleted successfully.", "info")
        if request.is_json:
            return jsonify({'success': True, 'message': 'Deleted successfully'}), 200
        return redirect(url_for('income.list_income'))
    except LookupError as err:
        if request.is_json:
            return jsonify({'success': False, 'error': str(err)}), 404
        flash(str(err), "danger")
        return redirect(url_for('income.list_income'))

@income_bp.route('/api/income', methods=['GET'])
@login_required
def api_list_income():
    """REST endpoint returning income items in JSON format."""
    user = get_current_user()
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    source = request.args.get('source', '').strip() or None

    incomes = FinanceService.get_user_incomes(user.id, month=month, year=year, source=source)
    return jsonify({
        'success': True,
        'count': len(incomes),
        'incomes': [inc.to_dict() for inc in incomes]
    }), 200
