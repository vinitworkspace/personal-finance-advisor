import unittest
from datetime import date
from app import create_app
from models import db, User, Income, Expense
from services.finance_service import FinanceService

class TestFinanceService(unittest.TestCase):
    """Unit tests for income, expense management, financial math, and tenant isolation."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create two test users to verify multi-tenant isolation
        self.user1 = User(name="User One", email="user1@finance.test")
        self.user1.set_password("Password123!")
        self.user2 = User(name="User Two", email="user2@finance.test")
        self.user2.set_password("Password123!")
        db.session.add_all([self.user1, self.user2])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_and_read_income(self):
        """Test recording an income entry and retrieving it."""
        inc = FinanceService.create_income(
            user_id=self.user1.id,
            amount=50000.0,
            source="Salary",
            date_val=date(2026, 10, 1),
            description="October Salary"
        )
        self.assertIsNotNone(inc.id)
        self.assertEqual(inc.amount, 50000.0)

        incomes = FinanceService.get_user_incomes(self.user1.id, month=10, year=2026)
        self.assertEqual(len(incomes), 1)
        self.assertEqual(incomes[0].source, "Salary")

    def test_income_validation(self):
        """Test that invalid or non-positive amounts raise ValueError."""
        with self.assertRaises(ValueError):
            FinanceService.create_income(self.user1.id, amount=-500.0, source="Salary", date_val=date.today())
        with self.assertRaises(ValueError):
            FinanceService.create_income(self.user1.id, amount="not_a_number", source="Salary", date_val=date.today())

    def test_create_and_read_expense(self):
        """Test logging an expense transaction."""
        exp = FinanceService.create_expense(
            user_id=self.user1.id,
            amount=12000.0,
            category="Rent",
            date_val=date(2026, 10, 2),
            description="Flat rent",
            payment_method="NetBanking"
        )
        self.assertIsNotNone(exp.id)
        self.assertEqual(exp.amount, 12000.0)

        expenses = FinanceService.get_user_expenses(self.user1.id, month=10, year=2026)
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].category, "Rent")

    def test_financial_calculations_math(self):
        """
        Verify financial formulas:
          • Net Balance = Total Income - Total Expenses
          • Savings % = (Savings / Income) * 100
        """
        # User 1: 50,000 Income, 35,000 Expenses (15,000 Rent, 10,000 Food, 10,000 Shopping)
        FinanceService.create_income(self.user1.id, 50000.0, "Salary", date(2026, 10, 1))
        FinanceService.create_expense(self.user1.id, 15000.0, "Rent", date(2026, 10, 2))
        FinanceService.create_expense(self.user1.id, 10000.0, "Food", date(2026, 10, 5))
        FinanceService.create_expense(self.user1.id, 10000.0, "Shopping", date(2026, 10, 10))

        summary = FinanceService.calculate_monthly_summary(self.user1.id, month=10, year=2026)
        self.assertEqual(summary['total_income'], 50000.0)
        self.assertEqual(summary['total_expenses'], 35000.0)
        self.assertEqual(summary['net_balance'], 15000.0)
        # Savings Rate: 15,000 / 50,000 * 100 = 30.0%
        self.assertEqual(summary['savings_percentage'], 30.0)
        self.assertEqual(summary['highest_category'], "Rent")

    def test_zero_income_safe_division(self):
        """Test that having 0 income does not trigger a ZeroDivisionError in savings calculation."""
        FinanceService.create_expense(self.user1.id, 2500.0, "Food", date(2026, 10, 5))
        summary = FinanceService.calculate_monthly_summary(self.user1.id, month=10, year=2026)

        self.assertEqual(summary['total_income'], 0.0)
        self.assertEqual(summary['total_expenses'], 2500.0)
        self.assertEqual(summary['net_balance'], -2500.0)
        self.assertEqual(summary['savings_percentage'], 0.0)

    def test_strict_tenant_isolation(self):
        """Test that User 1 cannot access, update, or delete User 2's records."""
        # Create record for User 2
        inc2 = FinanceService.create_income(self.user2.id, 30000.0, "Freelance", date(2026, 10, 1))

        # User 1 queries income: should see 0
        user1_incomes = FinanceService.get_user_incomes(self.user1.id, month=10, year=2026)
        self.assertEqual(len(user1_incomes), 0)

        # User 1 attempts to update User 2's income -> should raise LookupError
        with self.assertRaises(LookupError):
            FinanceService.update_income(inc2.id, self.user1.id, 99999.0, "Salary", date.today())

        # User 1 attempts to delete User 2's income -> should raise LookupError
        with self.assertRaises(LookupError):
            FinanceService.delete_income(inc2.id, self.user1.id)

        # Confirm User 2's record remains untouched
        intact = db.session.get(Income, inc2.id)
        self.assertIsNotNone(intact)
        self.assertEqual(intact.amount, 30000.0)

if __name__ == '__main__':
    unittest.main()
