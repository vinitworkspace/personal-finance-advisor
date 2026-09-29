import unittest
from datetime import date
from app import create_app
from models import db, User
from services.finance_service import FinanceService
from services.gemini_service import GeminiService

class TestGeminiAndFallbackAI(unittest.TestCase):
    """Unit tests for AI expense categorization, advice generation, and resilient fallback mode."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(name="AI Tester", email="ai@finance.test", currency="₹")
        self.user.set_password("Password123!")
        db.session.add(self.user)
        db.session.commit()

        # Seed data for financial advice tests
        FinanceService.create_income(self.user.id, 50000.0, "Salary", date(2026, 10, 1))
        FinanceService.create_expense(self.user.id, 15000.0, "Rent", date(2026, 10, 2))
        FinanceService.create_expense(self.user.id, 7000.0, "Food", date(2026, 10, 5))
        FinanceService.create_expense(self.user.id, 4000.0, "Entertainment", date(2026, 10, 8))

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_auto_categorization_food(self):
        """Test categorization of food-related descriptions."""
        res1 = GeminiService.categorize_expense("Had lunch at Dominos pizza with colleagues")
        self.assertEqual(res1['category'], "Food")

        res2 = GeminiService.categorize_expense("Starbucks iced coffee and snacks")
        self.assertEqual(res2['category'], "Food")

    def test_auto_categorization_transport(self):
        """Test categorization of transport and commute expenses."""
        res1 = GeminiService.categorize_expense("Uber cab to downtown conference")
        self.assertEqual(res1['category'], "Transport")

        res2 = GeminiService.categorize_expense("Metro smart card recharge")
        self.assertEqual(res2['category'], "Transport")

    def test_auto_categorization_utilities(self):
        """Test categorization of household utilities."""
        res1 = GeminiService.categorize_expense("Monthly high-speed wifi internet broadband")
        self.assertEqual(res1['category'], "Utilities")

        res2 = GeminiService.categorize_expense("Electricity power bill payment")
        self.assertEqual(res2['category'], "Utilities")

    def test_auto_categorization_education_and_entertainment(self):
        """Test education courses and entertainment streaming."""
        res_edu = GeminiService.categorize_expense("Enrolled in Python Data Science course on Udemy")
        self.assertEqual(res_edu['category'], "Education")

        res_ent = GeminiService.categorize_expense("Netflix and Spotify monthly subscription")
        self.assertEqual(res_ent['category'], "Entertainment")

    def test_financial_advice_generation(self):
        """Test generation of personalized financial recommendations."""
        ctx = {
            'currency': '₹',
            'total_income': 50000.0,
            'total_expenses': 26000.0,
            'net_balance': 24000.0,
            'savings_percentage': 48.0,
            'category_breakdown': {'Rent': 15000.0, 'Food': 7000.0, 'Entertainment': 4000.0},
            'average_daily_spend': 866.67,
            'alerts': []
        }
        advice = GeminiService.generate_financial_advice(ctx)
        self.assertIsInstance(advice, str)
        self.assertIn("Monthly Spending Analysis", advice)
        self.assertIn("Actionable Cost-Cutting", advice)
        self.assertIn("Emergency Fund", advice)

    def test_chat_advisor_highest_spending(self):
        """Test chat advisor answers 'Where am I spending the most?'."""
        ctx = {
            'currency': '₹',
            'total_income': 50000.0,
            'total_expenses': 26000.0,
            'net_balance': 24000.0,
            'savings_percentage': 48.0,
            'category_breakdown': {'Rent': 15000.0, 'Food': 7000.0, 'Entertainment': 4000.0},
            'average_daily_spend': 866.67
        }
        reply = GeminiService.chat_with_advisor("Where am I spending the most?", ctx)
        self.assertIn("Rent", reply)
        self.assertIn("15,000", reply)

    def test_api_categorize_endpoint(self):
        """Test /api/ai/categorize POST endpoint returns valid category JSON."""
        client = self.app.test_client()
        client.post('/login', data={'email': 'ai@finance.test', 'password': 'Password123!'})

        res = client.post('/api/ai/categorize', json={'description': 'Swiggy dinner order'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['category'], 'Food')

    def test_api_chat_endpoint(self):
        """Test /api/ai/chat POST endpoint returns conversational JSON."""
        client = self.app.test_client()
        client.post('/login', data={'email': 'ai@finance.test', 'password': 'Password123!'})

        res = client.post('/api/ai/chat', json={'message': 'How much did I save this month?'})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn("savings", data['reply'].lower())

if __name__ == '__main__':
    unittest.main()
