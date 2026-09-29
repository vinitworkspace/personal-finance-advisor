import unittest
from datetime import date
from app import create_app
from models import db, User, Income, Expense, Budget, FinancialReport

class TestModels(unittest.TestCase):
    """Unit tests for Phase 1 database models, security hashing, and relationships."""

    def setUp(self):
        """Set up in-memory testing database before each test."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Clean up database after each test."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_password_hashing(self):
        """Test that passwords are never stored in plaintext and verification functions correctly."""
        user = User(name="Alice Johnson", email="alice@test.com")
        user.set_password("SecurePass123!")
        
        self.assertNotEqual(user.password_hash, "SecurePass123!")
        self.assertTrue(user.check_password("SecurePass123!"))
        self.assertFalse(user.check_password("WrongPassword"))

    def test_user_cascade_deletion(self):
        """Test that deleting a user cascades to all related financial entries (Tenant isolation)."""
        user = User(name="Bob Smith", email="bob@test.com")
        user.set_password("BobSecure123")
        db.session.add(user)
        db.session.commit()

        income = Income(user_id=user.id, amount=25000.0, source="Freelance", date=date.today())
        expense = Expense(user_id=user.id, amount=5000.0, category="Food", date=date.today())
        budget = Budget(user_id=user.id, category="Food", amount=6000.0, month=10, year=2026)
        
        db.session.add_all([income, expense, budget])
        db.session.commit()

        self.assertEqual(Income.query.filter_by(user_id=user.id).count(), 1)
        self.assertEqual(Expense.query.filter_by(user_id=user.id).count(), 1)
        self.assertEqual(Budget.query.filter_by(user_id=user.id).count(), 1)

        # Delete User
        db.session.delete(user)
        db.session.commit()

        # Verify cascading deletion cleaned up all associated rows
        self.assertEqual(Income.query.filter_by(user_id=user.id).count(), 0)
        self.assertEqual(Expense.query.filter_by(user_id=user.id).count(), 0)
        self.assertEqual(Budget.query.filter_by(user_id=user.id).count(), 0)

    def test_budget_uniqueness_constraint(self):
        """Test that duplicate budgets for the same category in the same month are rejected."""
        user = User(name="Charlie Davis", email="charlie@test.com")
        user.set_password("Charlie123!")
        db.session.add(user)
        db.session.commit()

        b1 = Budget(user_id=user.id, category="Food", amount=5000.0, month=5, year=2026)
        db.session.add(b1)
        db.session.commit()

        b2 = Budget(user_id=user.id, category="Food", amount=7000.0, month=5, year=2026)
        db.session.add(b2)
        with self.assertRaises(Exception):
            db.session.commit()
        db.session.rollback()

    def test_financial_report_serialization(self):
        """Test serialization of FinancialReport model."""
        user = User(name="Diana Prince", email="diana@test.com")
        user.set_password("Diana123!")
        db.session.add(user)
        db.session.commit()

        report = FinancialReport(
            user_id=user.id,
            month=10,
            year=2026,
            total_income=50000.0,
            total_expenses=32000.0,
            total_savings=18000.0,
            savings_percentage=36.0,
            ai_summary="Great savings rate of 36%."
        )
        db.session.add(report)
        db.session.commit()

        report_dict = report.to_dict()
        self.assertEqual(report_dict['total_income'], 50000.0)
        self.assertEqual(report_dict['savings_percentage'], 36.0)
        self.assertIn("Great savings", report_dict['ai_summary'])

if __name__ == '__main__':
    unittest.main()
