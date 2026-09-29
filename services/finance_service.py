from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import extract
from models import db, Income, Expense

class FinanceService:
    """Core financial management service providing calculations and transaction operations."""

    @staticmethod
    def validate_amount(amount: Any) -> float:
        """Validate that transaction amount is a positive numerical value."""
        try:
            val = float(amount)
        except (ValueError, TypeError):
            raise ValueError("Amount must be a valid number.")
        if val <= 0:
            raise ValueError("Amount must be greater than zero.")
        return round(val, 2)

    @staticmethod
    def parse_date(date_val: Any) -> date:
        """Safely parse date string in YYYY-MM-DD format or return current date."""
        if isinstance(date_val, date):
            return date_val
        if isinstance(date_val, str) and date_val.strip():
            try:
                return datetime.strptime(date_val.strip(), '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Invalid date format. Please use YYYY-MM-DD.")
        return date.today()

    # =========================================================================
    # INCOME OPERATIONS (TENANT-ISOLATED)
    # =========================================================================

    @staticmethod
    def get_user_incomes(user_id: int, month: Optional[int] = None, year: Optional[int] = None, source: Optional[str] = None) -> List[Income]:
        """Fetch income records for a specific user with optional date and source filtering."""
        query = Income.query.filter(Income.user_id == user_id)
        if month:
            query = query.filter(extract('month', Income.date) == month)
        if year:
            query = query.filter(extract('year', Income.date) == year)
        if source and source.strip():
            query = query.filter(Income.source == source.strip())
        return query.order_by(Income.date.desc(), Income.id.desc()).all()

    @staticmethod
    def create_income(user_id: int, amount: Any, source: str, date_val: Any, description: str = "") -> Income:
        """Create and persist a new income record."""
        validated_amount = FinanceService.validate_amount(amount)
        parsed_date = FinanceService.parse_date(date_val)
        source_clean = source.strip() if source and source.strip() in Income.SOURCES else 'Other'

        income = Income(
            user_id=user_id,
            amount=validated_amount,
            source=source_clean,
            date=parsed_date,
            description=(description or "").strip()
        )
        db.session.add(income)
        db.session.commit()
        return income

    @staticmethod
    def update_income(income_id: int, user_id: int, amount: Any, source: str, date_val: Any, description: str = "") -> Income:
        """Update an existing income record strictly owned by the specified user."""
        income = Income.query.filter_by(id=income_id, user_id=user_id).first()
        if not income:
            raise LookupError("Income record not found or access denied.")

        income.amount = FinanceService.validate_amount(amount)
        income.date = FinanceService.parse_date(date_val)
        if source and source.strip() in Income.SOURCES:
            income.source = source.strip()
        income.description = (description or "").strip()

        db.session.commit()
        return income

    @staticmethod
    def delete_income(income_id: int, user_id: int) -> bool:
        """Delete an income record strictly owned by the specified user."""
        income = Income.query.filter_by(id=income_id, user_id=user_id).first()
        if not income:
            raise LookupError("Income record not found or access denied.")
        db.session.delete(income)
        db.session.commit()
        return True

    # =========================================================================
    # EXPENSE OPERATIONS (TENANT-ISOLATED)
    # =========================================================================

    @staticmethod
    def get_user_expenses(user_id: int, month: Optional[int] = None, year: Optional[int] = None,
                          category: Optional[str] = None, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> List[Expense]:
        """Fetch expense records for a specific user with optional filters."""
        query = Expense.query.filter(Expense.user_id == user_id)
        if month:
            query = query.filter(extract('month', Expense.date) == month)
        if year:
            query = query.filter(extract('year', Expense.date) == year)
        if category and category.strip():
            query = query.filter(Expense.category == category.strip())
        if start_date:
            s_date = FinanceService.parse_date(start_date)
            query = query.filter(Expense.date >= s_date)
        if end_date:
            e_date = FinanceService.parse_date(end_date)
            query = query.filter(Expense.date <= e_date)

        return query.order_by(Expense.date.desc(), Expense.id.desc()).all()

    @staticmethod
    def create_expense(user_id: int, amount: Any, category: str, date_val: Any,
                       description: str = "", payment_method: str = "UPI/Card") -> Expense:
        """Create and persist a new expense record."""
        validated_amount = FinanceService.validate_amount(amount)
        parsed_date = FinanceService.parse_date(date_val)
        clean_category = category.strip() if category and category.strip() in Expense.CATEGORIES else 'Other'
        clean_payment = payment_method.strip() if payment_method and payment_method.strip() in Expense.PAYMENT_METHODS else 'UPI/Card'

        expense = Expense(
            user_id=user_id,
            amount=validated_amount,
            category=clean_category,
            date=parsed_date,
            description=(description or "").strip(),
            payment_method=clean_payment
        )
        db.session.add(expense)
        db.session.commit()
        return expense

    @staticmethod
    def update_expense(expense_id: int, user_id: int, amount: Any, category: str,
                       date_val: Any, description: str = "", payment_method: str = "UPI/Card") -> Expense:
        """Update an existing expense record strictly owned by the specified user."""
        expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
        if not expense:
            raise LookupError("Expense record not found or access denied.")

        expense.amount = FinanceService.validate_amount(amount)
        expense.date = FinanceService.parse_date(date_val)
        if category and category.strip() in Expense.CATEGORIES:
            expense.category = category.strip()
        if payment_method and payment_method.strip() in Expense.PAYMENT_METHODS:
            expense.payment_method = payment_method.strip()
        expense.description = (description or "").strip()

        db.session.commit()
        return expense

    @staticmethod
    def delete_expense(expense_id: int, user_id: int) -> bool:
        """Delete an expense record strictly owned by the specified user."""
        expense = Expense.query.filter_by(id=expense_id, user_id=user_id).first()
        if not expense:
            raise LookupError("Expense record not found or access denied.")
        db.session.delete(expense)
        db.session.commit()
        return True

    # =========================================================================
    # CORE FINANCIAL CALCULATIONS
    # =========================================================================

    @staticmethod
    def calculate_monthly_summary(user_id: int, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Calculate total income, expenses, net balance, savings rate, and category distributions.
        
        Formulas:
          • Net Balance = Total Income - Total Expenses
          • Savings Percentage = (Total Savings / Total Income) * 100
        """
        target_month = month or date.today().month
        target_year = year or date.today().year

        incomes = FinanceService.get_user_incomes(user_id, month=target_month, year=target_year)
        expenses = FinanceService.get_user_expenses(user_id, month=target_month, year=target_year)

        total_income = round(sum(i.amount for i in incomes), 2)
        total_expenses = round(sum(e.amount for e in expenses), 2)
        net_balance = round(total_income - total_expenses, 2)

        # Savings rate calculation: if income <= 0, savings rate is 0.0%
        if total_income > 0:
            savings_pct = round((net_balance / total_income) * 100, 2)
        else:
            savings_pct = 0.0

        # Category breakdown
        category_breakdown: Dict[str, float] = {}
        for exp in expenses:
            category_breakdown[exp.category] = round(category_breakdown.get(exp.category, 0.0) + exp.amount, 2)

        sorted_categories = sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True)
        highest_category = sorted_categories[0][0] if sorted_categories else "None"
        highest_category_amount = sorted_categories[0][1] if sorted_categories else 0.0

        # Income sources breakdown
        source_breakdown: Dict[str, float] = {}
        for inc in incomes:
            source_breakdown[inc.source] = round(source_breakdown.get(inc.source, 0.0) + inc.amount, 2)

        return {
            'month': target_month,
            'year': target_year,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'savings_percentage': savings_pct,
            'category_breakdown': dict(sorted_categories),
            'highest_category': highest_category,
            'highest_category_amount': highest_category_amount,
            'income_sources': source_breakdown,
            'income_count': len(incomes),
            'expense_count': len(expenses)
        }
