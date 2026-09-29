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
        self.assertNotIn('password_hash', data['user'])

if __name__ == '__main__':
    unittest.main()
