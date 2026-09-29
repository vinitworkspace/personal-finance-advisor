import unittest
from datetime import date
from app import create_app
from models import db, User
from services.finance_service import FinanceService
from services.budget_service import BudgetService

class TestBudgetService(unittest.TestCase):
    """Unit tests for budget management, threshold alerts, and overrun computations."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name="Budget Tester", email="budget@finance.test")
        self.user.set_password("Password123!")
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_set_and_update_budget(self):
        """Test setting a budget and updating the existing entry without creating duplicates."""
        b1 = BudgetService.set_or_update_budget(self.user.id, "Food", 5000.0, month=10, year=2026)
        self.assertEqual(b1.amount, 5000.0)

        # Update budget for same category and period
        b2 = BudgetService.set_or_update_budget(self.user.id, "Food", 6500.0, month=10, year=2026)
        self.assertEqual(b1.id, b2.id)
        self.assertEqual(b2.amount, 6500.0)

        budgets = BudgetService.get_user_budgets(self.user.id, month=10, year=2026)
        self.assertEqual(len(budgets), 1)

    def test_budget_threshold_safe(self):
        """Test budget utilization below 75% is categorized as safe with no alerts."""
        BudgetService.set_or_update_budget(self.user.id, "Transport", 4000.0, month=10, year=2026)
        # Spend 2,000 (50% used)
        FinanceService.create_expense(self.user.id, 2000.0, "Transport", date(2026, 10, 5))

        status = BudgetService.get_budget_status(self.user.id, month=10, year=2026)
        self.assertEqual(len(status['items']), 1)
        item = status['items'][0]
        self.assertEqual(item['status'], 'safe')
        self.assertEqual(item['percent_used'], 50.0)
        self.assertEqual(item['remaining'], 2000.0)
        self.assertEqual(len(status['alerts']), 0)

    def test_budget_threshold_warning(self):
        """Test budget utilization between 75% and 99.9% triggers a warning alert."""
        BudgetService.set_or_update_budget(self.user.id, "Entertainment", 5000.0, month=10, year=2026)
        # Spend 4,000 (80% used)
        FinanceService.create_expense(self.user.id, 4000.0, "Entertainment", date(2026, 10, 10))

        status = BudgetService.get_budget_status(self.user.id, month=10, year=2026)
        item = status['items'][0]
        self.assertEqual(item['status'], 'warning')
        self.assertEqual(item['percent_used'], 80.0)
        self.assertEqual(item['remaining'], 1000.0)

        # Confirm warning alert was generated
        self.assertEqual(len(status['alerts']), 1)
        self.assertEqual(status['alerts'][0]['severity'], 'warning')
        self.assertIn("nearing limit", status['alerts'][0]['message'])

    def test_budget_threshold_danger_overrun(self):
        """Test budget overrun (>= 100%) triggers danger alert with excess calculated."""
        BudgetService.set_or_update_budget(self.user.id, "Food", 5000.0, month=10, year=2026)
        # Spend 5,750 (115% used -> Over by 750)
        FinanceService.create_expense(self.user.id, 5750.0, "Food", date(2026, 10, 15))

        status = BudgetService.get_budget_status(self.user.id, month=10, year=2026)
        item = status['items'][0]
        self.assertEqual(item['status'], 'danger')
        self.assertEqual(item['percent_used'], 115.0)

        # Confirm danger alert was generated with exact overrun amount
        self.assertEqual(len(status['alerts']), 1)
        self.assertEqual(status['alerts'][0]['severity'], 'danger')
        self.assertEqual(status['alerts'][0]['overrun'], 750.0)
        self.assertIn("exceeded by", status['alerts'][0]['message'])

if __name__ == '__main__':
    unittest.main()
