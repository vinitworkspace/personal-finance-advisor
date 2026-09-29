from datetime import date
from typing import List, Dict, Any, Optional
from models import db, Budget, Expense
from services.finance_service import FinanceService

class BudgetService:
    """Service managing category monthly budgets, threshold evaluations, and overrun alerts."""

    @staticmethod
    def get_user_budgets(user_id: int, month: Optional[int] = None, year: Optional[int] = None) -> List[Budget]:
        """Fetch all budget allocations defined by a user for a given month and year."""
        target_month = month or date.today().month
        target_year = year or date.today().year

        return Budget.query.filter_by(
            user_id=user_id,
            month=target_month,
            year=target_year
        ).order_by(Budget.category.asc()).all()

    @staticmethod
    def set_or_update_budget(user_id: int, category: str, amount: Any,
                             month: Optional[int] = None, year: Optional[int] = None) -> Budget:
        """Create or update a monthly budget ceiling for a specific category."""
        target_month = month or date.today().month
        target_year = year or date.today().year
        validated_amount = FinanceService.validate_amount(amount)
        clean_category = category.strip() if category and category.strip() in Expense.CATEGORIES else 'Other'

        # Look for existing budget for this (user, category, month, year)
        existing = Budget.query.filter_by(
            user_id=user_id,
            category=clean_category,
            month=target_month,
            year=target_year
        ).first()

        if existing:
            existing.amount = validated_amount
            db.session.commit()
            return existing
        else:
            new_budget = Budget(
                user_id=user_id,
                category=clean_category,
                amount=validated_amount,
                month=target_month,
                year=target_year
            )
            db.session.add(new_budget)
            db.session.commit()
            return new_budget

    @staticmethod
    def delete_budget(budget_id: int, user_id: int) -> bool:
        """Remove a budget allocation strictly owned by the specified user."""
        budget = Budget.query.filter_by(id=budget_id, user_id=user_id).first()
        if not budget:
            raise LookupError("Budget record not found or access denied.")
        db.session.delete(budget)
        db.session.commit()
        return True

    @staticmethod
    def get_budget_status(user_id: int, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Evaluate actual spending against budget ceilings and generate real-time alerts.
        
        Threshold rules:
          • Safe: < 75% used
          • Warning: 75% to 99.9% used
          • Danger / Overrun: >= 100% used
        """
        target_month = month or date.today().month
        target_year = year or date.today().year

        budgets = BudgetService.get_user_budgets(user_id, target_month, target_year)
        expenses = FinanceService.get_user_expenses(user_id, month=target_month, year=target_year)

        # Aggregate actual spending by category
        actual_spending: Dict[str, float] = {}
        for exp in expenses:
            actual_spending[exp.category] = round(actual_spending.get(exp.category, 0.0) + exp.amount, 2)

        budget_items: List[Dict[str, Any]] = []
        alerts: List[Dict[str, Any]] = []
        total_budgeted = 0.0
        total_spent_budgeted = 0.0

        for b in budgets:
            budgeted = round(float(b.amount), 2)
            spent = round(actual_spending.get(b.category, 0.0), 2)
            remaining = round(budgeted - spent, 2)
            percent_used = round((spent / budgeted) * 100, 1) if budgeted > 0 else 0.0

            total_budgeted += budgeted
            total_spent_budgeted += spent

            # Determine alert severity
            if spent >= budgeted:
                status = 'danger'
                overrun = round(spent - budgeted, 2)
                alert_msg = f"{b.category} budget exceeded by ₹{overrun:,.2f} ({percent_used}% utilized)."
                alerts.append({
                    'category': b.category,
                    'severity': 'danger',
                    'message': alert_msg,
                    'overrun': overrun
                })
            elif percent_used >= 75.0:
                status = 'warning'
                alert_msg = f"{b.category} budget nearing limit: {percent_used}% utilized (₹{remaining:,.2f} remaining)."
                alerts.append({
                    'category': b.category,
                    'severity': 'warning',
                    'message': alert_msg,
                    'remaining': remaining
                })
            else:
                status = 'safe'

            budget_items.append({
                'id': b.id,
                'category': b.category,
                'budgeted': budgeted,
                'spent': spent,
                'remaining': remaining,
                'percent_used': percent_used,
                'status': status
            })

        # Calculate overall utilization percentage
        overall_utilization = round((total_spent_budgeted / total_budgeted * 100), 1) if total_budgeted > 0 else 0.0

        return {
            'month': target_month,
            'year': target_year,
            'budget_list': budget_items,
            'items': budget_items,
            'alerts': alerts,
            'total_budgeted': round(total_budgeted, 2),
            'total_spent_budgeted': round(total_spent_budgeted, 2),
            'overall_utilization': overall_utilization,
            'budget_count': len(budget_items)
        }
