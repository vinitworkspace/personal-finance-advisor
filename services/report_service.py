import csv
import io
import calendar
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from models import db, FinancialReport, Income, Expense, User
from services.finance_service import FinanceService
from services.budget_service import BudgetService
from services.analytics_service import AnalyticsService
from services.gemini_service import GeminiService

class ReportService:
    """Service handling compilation, caching, and exporting of monthly financial reports."""

    @staticmethod
    def compile_monthly_report(user_id: int, month: int, year: int, regenerate: bool = False) -> FinancialReport:
        """
        Compile and persist a comprehensive monthly financial report with cached AI insights.
        """
        existing = FinancialReport.query.filter_by(
            user_id=user_id,
            month=month,
            year=year
        ).first()

        if existing and not regenerate:
            return existing

        summary = FinanceService.calculate_monthly_summary(user_id, month=month, year=year)
        velocity = AnalyticsService.get_daily_spending_velocity(user_id, month=month, year=year)
        budget_status = BudgetService.get_budget_status(user_id, month=month, year=year)
        user = db.session.get(User, user_id)

        # Build context for AI advice generation
        context = {
            'currency': user.currency if user else '₹',
            'user_name': user.name if user else 'User',
            'month': month,
            'year': year,
            'total_income': summary['total_income'],
            'total_expenses': summary['total_expenses'],
            'net_balance': summary['net_balance'],
            'savings_percentage': summary['savings_percentage'],
            'category_breakdown': summary['category_breakdown'],
            'average_daily_spend': velocity['average_daily_spend'],
            'alerts': [a['message'] for a in budget_status.get('alerts', [])]
        }

        ai_advice = GeminiService.generate_financial_advice(context)

        if existing:
            existing.total_income = summary['total_income']
            existing.total_expenses = summary['total_expenses']
            existing.total_savings = summary['net_balance']
            existing.savings_percentage = summary['savings_percentage']
            existing.ai_summary = ai_advice
            existing.generated_at = datetime.utcnow()
            db.session.commit()
            return existing
        else:
            report = FinancialReport(
                user_id=user_id,
                month=month,
                year=year,
                total_income=summary['total_income'],
                total_expenses=summary['total_expenses'],
                total_savings=summary['net_balance'],
                savings_percentage=summary['savings_percentage'],
                ai_summary=ai_advice,
                generated_at=datetime.utcnow()
            )
            db.session.add(report)
            db.session.commit()
            return report

    @staticmethod
    def get_user_reports(user_id: int) -> List[FinancialReport]:
        """Fetch all compiled historical reports for a specific user."""
        return FinancialReport.query.filter_by(user_id=user_id).order_by(
            FinancialReport.year.desc(),
            FinancialReport.month.desc()
        ).all()

    @staticmethod
    def export_transactions_csv(user_id: int) -> str:
        """
        Generate RFC-4180 compliant CSV export containing all user transactions.
        """
        user = db.session.get(User, user_id)
        currency = user.currency if user else '₹'

        incomes = FinanceService.get_user_incomes(user_id)
        expenses = FinanceService.get_user_expenses(user_id)

        rows = []
        for inc in incomes:
            rows.append({
                'Type': 'INCOME',
                'Date': inc.date.strftime('%Y-%m-%d'),
                'Category_or_Source': inc.source,
                'Amount': inc.amount,
                'Currency': currency,
                'Description': inc.description or '',
                'Payment_Method': 'N/A'
            })

        for exp in expenses:
            rows.append({
                'Type': 'EXPENSE',
                'Date': exp.date.strftime('%Y-%m-%d'),
                'Category_or_Source': exp.category,
                'Amount': exp.amount,
                'Currency': currency,
                'Description': exp.description or '',
                'Payment_Method': exp.payment_method
            })

        # Sort all records by date descending
        rows.sort(key=lambda x: x['Date'], reverse=True)

        output = io.StringIO()
        fieldnames = ['Type', 'Date', 'Category_or_Source', 'Amount', 'Currency', 'Description', 'Payment_Method']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

        return output.getvalue()
