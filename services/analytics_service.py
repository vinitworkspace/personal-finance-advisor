import calendar
from datetime import date
from typing import List, Dict, Any, Optional
from services.finance_service import FinanceService

class AnalyticsService:
    """Service providing financial metrics, spending velocity, trends, and pattern detection."""

    CATEGORY_COLORS = {
        'Food': '#fb923c',          # Amber/Orange
        'Rent': '#c084fc',          # Purple
        'Transport': '#60a5fa',     # Blue
        'Utilities': '#2dd4bf',     # Teal
        'Entertainment': '#f472b6', # Pink
        'Shopping': '#fb7185',      # Rose
        'Healthcare': '#38bdf8',    # Cyan
        'Education': '#a78bfa',     # Indigo
        'EMI': '#f59e0b',           # Gold
        'Other': '#94a3b8'          # Slate
    }

    @staticmethod
    def get_daily_spending_velocity(user_id: int, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Calculate daily burn rate and projected end-of-month total spending.
        
        Formulas:
          • Average Daily Spend = Total Expenses / Days Elapsed
          • Projected Month-End Spend = Average Daily Spend * Days in Month
        """
        today = date.today()
        target_month = month or today.month
        target_year = year or today.year

        _, days_in_month = calendar.monthrange(target_year, target_month)

        if target_year == today.year and target_month == today.month:
            days_elapsed = max(today.day, 1)
        elif date(target_year, target_month, 1) < today:
            days_elapsed = days_in_month
        else:
            days_elapsed = 1

        summary = FinanceService.calculate_monthly_summary(user_id, target_month, target_year)
        total_expenses = summary['total_expenses']

        avg_daily_spend = round(total_expenses / days_elapsed, 2) if days_elapsed > 0 else 0.0
        projected_spend = round(avg_daily_spend * days_in_month, 2)

        return {
            'month': target_month,
            'year': target_year,
            'days_in_month': days_in_month,
            'days_elapsed': days_elapsed,
            'total_expenses': total_expenses,
            'average_daily_spend': avg_daily_spend,
            'projected_spend': projected_spend
        }

    @staticmethod
    def get_category_distribution(user_id: int, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Calculate category percentage shares and provide Chart.js payload.
        """
        summary = FinanceService.calculate_monthly_summary(user_id, month, year)
        total_expenses = summary['total_expenses']
        raw_breakdown = summary['category_breakdown']

        labels: List[str] = []
        data: List[float] = []
        colors: List[str] = []
        percentage_items: List[Dict[str, Any]] = []

        for category, amt in raw_breakdown.items():
            pct = round((amt / total_expenses) * 100, 1) if total_expenses > 0 else 0.0
            color = AnalyticsService.CATEGORY_COLORS.get(category, '#94a3b8')

            labels.append(category)
            data.append(round(amt, 2))
            colors.append(color)

            percentage_items.append({
                'category': category,
                'amount': round(amt, 2),
                'percentage': pct,
                'color': color
            })

        return {
            'labels': labels,
            'data': data,
            'colors': colors,
            'category_list': percentage_items,
            'items': percentage_items,
            'total_expenses': total_expenses
        }

    @staticmethod
    def get_monthly_trends(user_id: int, months_count: int = 6) -> Dict[str, Any]:
        """
        Generate 6-month historical trajectory of income vs expenses for trend charts.
        """
        today = date.today()
        month_labels: List[str] = []
        income_series: List[float] = []
        expense_series: List[float] = []
        savings_series: List[float] = []

        # Generate (year, month) tuples stepping backwards
        periods = []
        cur_year, cur_month = today.year, today.month
        for _ in range(months_count):
            periods.append((cur_year, cur_month))
            cur_month -= 1
            if cur_month < 1:
                cur_month = 12
                cur_year -= 1

        periods.reverse()  # Chronological order

        for yr, mo in periods:
            month_name = calendar.month_abbr[mo]
            label = f"{month_name} '{str(yr)[2:]}"
            summary = FinanceService.calculate_monthly_summary(user_id, month=mo, year=yr)

            month_labels.append(label)
            income_series.append(summary['total_income'])
            expense_series.append(summary['total_expenses'])
            savings_series.append(summary['net_balance'])

        return {
            'labels': month_labels,
            'income': income_series,
            'expenses': expense_series,
            'savings': savings_series
        }

    @staticmethod
    def get_spending_insights(user_id: int, month: Optional[int] = None, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Rule-based pattern detection generating actionable financial observations.
        """
        summary = FinanceService.calculate_monthly_summary(user_id, month, year)
        velocity = AnalyticsService.get_daily_spending_velocity(user_id, month, year)
        insights = []

        total_income = summary['total_income']
        total_expenses = summary['total_expenses']
        net_balance = summary['net_balance']
        savings_pct = summary['savings_percentage']
        categories = summary['category_breakdown']

        # Rule 1: High Living Expenses Deficit
        if total_income > 0 and total_expenses > total_income:
            deficit = total_expenses - total_income
            insights.append({
                'type': 'danger',
                'title': 'Deficit Spending Warning',
                'message': f"Monthly spending exceeds income by ₹{deficit:,.2f}. Consider trimming non-essential expenditures."
            })

        # Rule 2: Savings Health
        if total_income > 0:
            if savings_pct >= 20.0:
                insights.append({
                    'type': 'success',
                    'title': 'Healthy Savings Rate',
                    'message': f"You are saving {savings_pct}% of your income, surpassing the benchmark 20% savings rule!"
                })
            elif savings_pct > 0.0:
                insights.append({
                    'type': 'warning',
                    'title': 'Modest Savings Buffer',
                    'message': f"Your savings rate is {savings_pct}%. Aim to increase your savings buffer toward 20%."
                })

        # Rule 3: Heavy Entertainment / Shopping Share
        entertainment_spend = categories.get('Entertainment', 0.0)
        shopping_spend = categories.get('Shopping', 0.0)
        discretionary = entertainment_spend + shopping_spend

        if total_income > 0 and discretionary > 0:
            disc_pct = (discretionary / total_income) * 100
            if disc_pct >= 15.0:
                insights.append({
                    'type': 'warning',
                    'title': 'Elevated Discretionary Outlay',
                    'message': f"Entertainment and Shopping consume {disc_pct:.1f}% of your monthly income (₹{discretionary:,.2f})."
                })

        # Rule 4: Burn Rate Velocity Projection
        if total_income > 0 and velocity['projected_spend'] > total_income:
            insights.append({
                'type': 'info',
                'title': 'Burn Rate Projection',
                'message': f"At current average velocity (₹{velocity['average_daily_spend']:,.2f}/day), projected month-end outflow is ₹{velocity['projected_spend']:,.2f}."
            })

        if not insights:
            insights.append({
                'type': 'info',
                'title': 'Financial Equilibrium',
                'message': "No anomalous spending detected. Continue logging daily expenses to refine your pattern analysis."
            })

        return insights
