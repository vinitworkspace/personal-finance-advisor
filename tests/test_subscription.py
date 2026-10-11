import unittest
from datetime import datetime, timedelta
from app import create_app
from models import db, User

class TestSubscription(unittest.TestCase):
    """Unit tests for ₹100/month subscription model, 30-day free trial, and feature paywalls."""

    def setUp(self):
        """Configure test application and empty database for each test case."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create a test user
        self.user = User(
            name="Subscriber Student",
            email="sub@finance.test",
            currency="₹"
        )
        self.user.set_password("Password123!")
        db.session.add(self.user)
        db.session.commit()

        # Log in
        self.client.post('/login', data={'email': 'sub@finance.test', 'password': 'Password123!'})

    def tearDown(self):
        """Tear down and drop in-memory database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_new_user_starts_with_30_day_free_trial(self):
        """Verify that newly registered accounts receive an active 30-day free trial."""
        self.assertEqual(self.user.subscription_status, 'trial')
        self.assertTrue(self.user.is_subscription_active())
        self.assertGreaterEqual(self.user.days_remaining(), 29)
        self.assertLessEqual(self.user.days_remaining(), 31)

        info = self.user.get_subscription_info()
        self.assertEqual(info['status'], 'trial')
        self.assertTrue(info['is_active'])
        self.assertIn('Trial', info['badge_text'])

    def test_trial_user_can_access_ai_advisor(self):
        """Verify that free trial users can access the AI Financial Advisor."""
        response = self.client.get('/advisor')
        self.assertEqual(response.status_code, 200)

    def test_expired_trial_blocks_ai_advisor(self):
        """Verify that users whose 30-day trial has elapsed are redirected to subscription."""
        # Simulate trial expired 2 days ago
        self.user.subscription_status = 'expired'
        self.user.trial_ends_at = datetime.utcnow() - timedelta(days=2)
        db.session.commit()

        self.assertFalse(self.user.is_subscription_active())
        self.assertEqual(self.user.days_remaining(), 0)

        # GET /advisor should redirect to /subscription
        response = self.client.get('/advisor')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/subscription', response.headers.get('Location', ''))

        # POST /api/ai/chat should return 402 Payment Required JSON
        api_res = self.client.post('/api/ai/chat', json={'message': 'How to save money?'})
        self.assertEqual(api_res.status_code, 402)
        json_data = api_res.get_json()
        self.assertFalse(json_data['success'])
        self.assertEqual(json_data['code'], 'SUBSCRIPTION_EXPIRED')

    def test_payment_checkout_activates_pro(self):
        """Verify that paying ₹100 activates FinanceAI Pro for 30 calendar days."""
        # Expire user first
        self.user.subscription_status = 'expired'
        self.user.trial_ends_at = datetime.utcnow() - timedelta(days=5)
        db.session.commit()

        # Submit ₹100 payment
        response = self.client.post('/subscription/checkout', json={
            'amount': 100,
            'payment_method': 'upi'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'active')

        # Verify DB state
        db.session.refresh(self.user)
        self.assertEqual(self.user.subscription_status, 'active')
        self.assertTrue(self.user.is_subscription_active())
        self.assertGreaterEqual(self.user.days_remaining(), 29)

        # Now /advisor should be fully accessible again
        adv_res = self.client.get('/advisor')
        self.assertEqual(adv_res.status_code, 200)

    def test_multiple_payments_extend_duration(self):
        """Verify that renewing before expiry extends subscription by an additional 30 days."""
        # First payment: 30 days
        self.user.activate_subscription(duration_days=30)
        first_expiry = self.user.subscription_expires_at
        db.session.commit()

        # Second payment of ₹100: should add 30 more days
        self.client.post('/subscription/checkout', json={'amount': 100, 'payment_method': 'card'})
        db.session.refresh(self.user)

        expected_expiry = first_expiry + timedelta(days=30)
        # Difference should be within a couple seconds
        diff = abs((self.user.subscription_expires_at - expected_expiry).total_seconds())
        self.assertLess(diff, 5)
        self.assertGreaterEqual(self.user.days_remaining(), 59)

if __name__ == '__main__':
    unittest.main()
