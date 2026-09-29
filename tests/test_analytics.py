import unittest
from datetime import date
from app import create_app
from models import db, User
from services.finance_service import FinanceService
from services.analytics_service import AnalyticsService

class TestAnalyticsService(unittest.TestCase):
    """Unit tests for spending velocity, category distributions, trends, and pattern detection."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name="Analytics Tester", email="analytics@finance.test")
        self.user.set_password("Password123!")
        db.session.add(self.user)
        db.session.commit()

        # Seed sample data for testing
        # October 2026: 31 days.
        FinanceService.create_income(self.user.id, 60000.0, "Salary", date(2026, 10, 1))
        FinanceService.create_expense(self.user.id, 15000.0, "Rent", date(2026, 10, 2))
        FinanceService.create_expense(self.user.id, 9000.0, "Food", date(2026, 10, 5))
        FinanceService.create_expense(self.user.id, 6000.0, "Entertainment", date(2026, 10, 8))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_daily_spending_velocity(self):
        """Test daily burn rate and end-of-month projected spend calculations."""
        velocity = AnalyticsService.get_daily_spending_velocity(self.user.id, month=10, year=2026)
        
        self.assertEqual(velocity['total_expenses'], 30000.0)
        self.assertEqual(velocity['days_in_month'], 31)
        self.assertGreater(velocity['average_daily_spend'], 0.0)
        self.assertGreater(velocity['projected_spend'], 0.0)

    def test_category_distribution(self):
        """Test category share percentages and Chart.js payload structures."""
        dist = AnalyticsService.get_category_distribution(self.user.id, month=10, year=2026)
        
        self.assertEqual(dist['total_expenses'], 30000.0)
        self.assertIn("Rent", dist['labels'])
        self.assertIn("Food", dist['labels'])
        self.assertIn("Entertainment", dist['labels'])

        # Rent: 15,000 / 30,000 = 50.0%
        rent_item = next(item for item in dist['items'] if item['category'] == 'Rent')
        self.assertEqual(rent_item['amount'], 15000.0)
        self.assertEqual(rent_item['percentage'], 50.0)

    def test_monthly_trends_series(self):
        """Test 6-month historical trajectory returns chronological datasets."""
        trends = AnalyticsService.get_monthly_trends(self.user.id, months_count=6)
        
        self.assertEqual(len(trends['labels']), 6)
        self.assertEqual(len(trends['income']), 6)
        self.assertEqual(len(trends['expenses']), 6)
        self.assertEqual(len(trends['savings']), 6)

    def test_spending_pattern_insights(self):
        """Test rule-based insight generation detecting healthy savings and discretionary spend."""
        insights = AnalyticsService.get_spending_insights(self.user.id, month=10, year=2026)
        
        self.assertTrue(len(insights) > 0)
        # Income = 60,000, Expenses = 30,000 -> Savings = 50.0% -> Healthy Savings Rate
        has_healthy_savings = any(i['title'] == 'Healthy Savings Rate' for i in insights)
        self.assertTrue(has_healthy_savings)

    def test_api_charts_endpoint(self):
        """Test /api/analytics/charts JSON endpoint returns 200 with chart structures."""
        client = self.app.test_client()
        client.post('/login', data={'email': 'analytics@finance.test', 'password': 'Password123!'})

        response = client.get('/api/analytics/charts?month=10&year=2026')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('category_chart', data)
        self.assertIn('trend_chart', data)
        self.assertIn('velocity', data)

if __name__ == '__main__':
    unittest.main()
