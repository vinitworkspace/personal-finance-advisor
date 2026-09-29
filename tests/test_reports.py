import unittest
from datetime import date
from app import create_app
from models import db, User, FinancialReport, Income, Expense
from services.finance_service import FinanceService
from services.report_service import ReportService

class TestReportService(unittest.TestCase):
    """Unit tests for monthly report compilation, snapshot caching, and CSV export."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name="Report Tester", email="reporter@finance.test", currency="₹")
        self.user.set_password("Password123!")
        db.session.add(self.user)
        db.session.commit()

        # Seed data for October 2026
        FinanceService.create_income(self.user.id, 50000.0, "Salary", date(2026, 10, 1))
        FinanceService.create_expense(self.user.id, 15000.0, "Rent", date(2026, 10, 2))
        FinanceService.create_expense(self.user.id, 5000.0, "Food", date(2026, 10, 5))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_compile_monthly_report(self):
        """Test compiling and saving a monthly financial snapshot in SQLite."""
        report = ReportService.compile_monthly_report(self.user.id, month=10, year=2026)
        
        self.assertIsNotNone(report.id)
        self.assertEqual(report.total_income, 50000.0)
        self.assertEqual(report.total_expenses, 20000.0)
        self.assertEqual(report.total_savings, 30000.0)
        self.assertEqual(report.savings_percentage, 60.0)
        self.assertTrue(len(report.ai_summary) > 20)

        # Confirm persisted in DB
        db_report = FinancialReport.query.filter_by(user_id=self.user.id, month=10, year=2026).first()
        self.assertIsNotNone(db_report)
        self.assertEqual(db_report.id, report.id)

    def test_regenerate_report_no_duplicates(self):
        """Test that re-compiling a report updates the existing record instead of creating duplicates."""
        r1 = ReportService.compile_monthly_report(self.user.id, month=10, year=2026)
        count_before = FinancialReport.query.filter_by(user_id=self.user.id).count()

        # Add another expense and regenerate
        FinanceService.create_expense(self.user.id, 2000.0, "Utilities", date(2026, 10, 10))
        r2 = ReportService.compile_monthly_report(self.user.id, month=10, year=2026, regenerate=True)

        count_after = FinancialReport.query.filter_by(user_id=self.user.id).count()
        self.assertEqual(count_before, count_after)
        self.assertEqual(r1.id, r2.id)
        self.assertEqual(r2.total_expenses, 22000.0)

    def test_export_transactions_csv(self):
        """Test CSV ledger export format and content."""
        csv_text = ReportService.export_transactions_csv(self.user.id)
        self.assertIn("Type,Date,Category_or_Source,Amount,Currency,Description,Payment_Method", csv_text)
        self.assertIn("INCOME", csv_text)
        self.assertIn("EXPENSE", csv_text)
        self.assertIn("50000.0", csv_text)
        self.assertIn("Rent", csv_text)

    def test_routes_reports_view_and_export(self):
        """Test /reports, /reports/generate, and /reports/export/csv endpoints."""
        client = self.app.test_client()
        client.post('/login', data={'email': 'reporter@finance.test', 'password': 'Password123!'})

        # Test reports view
        res = client.get('/reports?month=10&year=2026')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Executive Financial Statement", res.data)

        # Test CSV export endpoint
        res_csv = client.get('/reports/export/csv')
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv.mimetype, 'text/csv')
        self.assertIn('attachment;', res_csv.headers.get('Content-Disposition', ''))

    def test_settings_currency_and_reset(self):
        """Test updating currency and demo reset via settings endpoints."""
        client = self.app.test_client()
        client.post('/login', data={'email': 'reporter@finance.test', 'password': 'Password123!'})

        # Update currency to USD $
        client.post('/settings/currency', data={'currency': '$'}, follow_redirects=True)
        user = db.session.get(User, self.user.id)
        self.assertEqual(user.currency, '$')

        # Trigger demo reset
        client.post('/settings/reset-demo', follow_redirects=True)
        incomes = Income.query.filter_by(user_id=self.user.id).all()
        expenses = Expense.query.filter_by(user_id=self.user.id).all()
        self.assertEqual(len(incomes), 1)
        self.assertEqual(len(expenses), 5)

if __name__ == '__main__':
    unittest.main()
