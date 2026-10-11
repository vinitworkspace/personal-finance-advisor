import unittest
from app import create_app
from models import db, User

class TestAuth(unittest.TestCase):
    """Unit tests for user registration, authentication, sessions, and route guards."""

    def setUp(self):
        """Configure test application and empty database for each test case."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        """Tear down and drop in-memory database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_registration_success(self):
        """Test successful registration via HTML form."""
        response = self.client.post('/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'currency': '₹',
            'password': 'SecurePassword123',
            'confirm_password': 'SecurePassword123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.currency, '₹')
        self.assertTrue(user.check_password('SecurePassword123'))

    def test_registration_duplicate_email(self):
        """Test that registering an already registered email is prevented."""
        # Create initial user
        u = User(name="First User", email="duplicate@example.com")
        u.set_password("Password123")
        db.session.add(u)
        db.session.commit()

        # Attempt to register duplicate
        response = self.client.post('/register', data={
            'name': 'Second User',
            'email': 'duplicate@example.com',
            'currency': '₹',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)

        self.assertIn(b"already exists", response.data)
        self.assertEqual(User.query.filter_by(email='duplicate@example.com').count(), 1)

    def test_registration_password_mismatch(self):
        """Test that mismatched passwords fail registration."""
        response = self.client.post('/register', data={
            'name': 'Mismatch User',
            'email': 'mismatch@example.com',
            'currency': '₹',
            'password': 'Password123',
            'confirm_password': 'Password456'
        }, follow_redirects=True)

        self.assertIn(b"Passwords do not match", response.data)
        self.assertIsNone(User.query.filter_by(email='mismatch@example.com').first())

    def test_registration_short_password(self):
        """Test that passwords shorter than 6 characters are rejected."""
        response = self.client.post('/register', data={
            'name': 'Short Pass',
            'email': 'short@example.com',
            'currency': '₹',
            'password': '123',
            'confirm_password': '123'
        }, follow_redirects=True)

        self.assertIn(b"at least 6 characters", response.data)
        self.assertIsNone(User.query.filter_by(email='short@example.com').first())

    def test_login_success(self):
        """Test authentication with correct credentials."""
        user = User(name="Login Test", email="login@example.com")
        user.set_password("CorrectPassword123")
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data={
            'email': 'login@example.com',
            'password': 'CorrectPassword123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome back, Login Test", response.data)

        # Check session contains user_id
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('user_id'), user.id)

    def test_login_invalid_password(self):
        """Test authentication rejection with incorrect password."""
        user = User(name="Login Test", email="login@example.com")
        user.set_password("CorrectPassword123")
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login', data={
            'email': 'login@example.com',
            'password': 'WrongPassword999'
        }, follow_redirects=True)

        self.assertIn(b"Invalid email or password", response.data)
        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('user_id'))

    def test_logout(self):
        """Test session termination upon logout."""
        user = User(name="Logout Test", email="logout@example.com")
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

        # Login first
        self.client.post('/login', data={'email': 'logout@example.com', 'password': 'Password123'})
        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get('user_id'), user.id)

        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"signed out safely", response.data)
        with self.client.session_transaction() as sess:
            self.assertIsNone(sess.get('user_id'))

    def test_unauthenticated_route_protection(self):
        """Test that unauthenticated requests to protected pages redirect to /login."""
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_unauthenticated_api_protection(self):
        """Test that unauthenticated requests to /api/ endpoints return 401 JSON."""
        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, 401)
        json_data = response.get_json()
        self.assertIn('Unauthorized', json_data.get('error', ''))

    def test_authenticated_api_me(self):
        """Test that authenticated users can query their profile JSON."""
        user = User(name="API User", email="api@example.com", currency="₹")
        user.set_password("Password123")
        db.session.add(user)
        db.session.commit()

        # Log in
        self.client.post('/login', data={'email': 'api@example.com', 'password': 'Password123'})

        response = self.client.get('/api/auth/me')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['name'], 'API User')
        self.assertEqual(data['user']['email'], 'api@example.com')
    def test_api_entrypoint_redirects(self):
        """Test that direct visits to serverless function entrypoints redirect cleanly."""
        for path in ['/api', '/api/', '/api/index', '/api/index.py']:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302, f"Failed for path {path}")

    def test_favicon_route(self):
        """Test that /favicon.ico returns 200 with SVG content."""
        response = self.client.get('/favicon.ico')
        self.assertEqual(response.status_code, 200)
        self.assertIn('image/svg+xml', response.content_type)

    def test_forgot_password_flow(self):
        """Test password reset request and reset verification."""
        user = User(name="Reset User", email="reset@example.com")
        user.set_password("OldPassword123")
        db.session.add(user)
        db.session.commit()

        # 1. Request OTP
        req_res = self.client.post('/forgot-password/request-otp', json={'email': 'reset@example.com'})
        self.assertEqual(req_res.status_code, 200)
        req_data = req_res.get_json()
        self.assertTrue(req_data['success'])
        otp = req_data['otp']

        # 2. Reset password using OTP
        reset_res = self.client.post('/forgot-password/reset', json={
            'email': 'reset@example.com',
            'otp': otp,
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        })
        self.assertEqual(reset_res.status_code, 200)

        # 3. Verify user can now log in with new password
        db.session.refresh(user)
        self.assertTrue(user.check_password('NewPassword123!'))

    def test_google_oauth_login(self):
        """Test Google OAuth authentication and account auto-creation."""
        res = self.client.post('/auth/oauth/google', json={
            'email': 'oauth.test@gmail.com',
            'name': 'OAuth Google User'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])

        user = User.query.filter_by(email='oauth.test@gmail.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'OAuth Google User')
        self.assertEqual(user.auth_provider, 'google')

    def test_phone_otp_login(self):
        """Test sending and verifying phone OTP."""
        # 1. Send OTP
        send_res = self.client.post('/auth/phone/send-otp', json={'phone_number': '9876543210'})
        self.assertEqual(send_res.status_code, 200)
        send_data = send_res.get_json()
        self.assertTrue(send_data['success'])
        otp = send_data['otp']

        # 2. Verify OTP
        verify_res = self.client.post('/auth/phone/verify-otp', json={'phone_number': '9876543210', 'otp': otp})
        self.assertEqual(verify_res.status_code, 200)
        verify_data = verify_res.get_json()
        self.assertTrue(verify_data['success'])

        user = User.query.filter_by(phone_number='9876543210').first()
        self.assertIsNotNone(user)

    def test_pin_and_biometric_login(self):
        """Test PIN code setting and biometric verification."""
        user = User(name="Pin User", email="pin@example.com")
        user.set_password("Password123")
        user.set_pin("4321")
        user.biometric_enabled = True
        db.session.add(user)
        db.session.commit()

        # Test PIN login
        pin_res = self.client.post('/auth/pin-login', json={'identifier': 'pin@example.com', 'pin': '4321'})
        self.assertEqual(pin_res.status_code, 200)

        # Test Biometric verification
        bio_res = self.client.post('/api/auth/biometric/verify', json={'identifier': 'pin@example.com'})
        self.assertEqual(bio_res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
