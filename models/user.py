from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    """User account model with secure password hashing, subscription tracking, and relationship cascades."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(10), default='₹', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Monthly Subscription & Free Month Trial System (₹100/month after 30-day free trial)
    subscription_status = db.Column(db.String(20), default='trial', nullable=False) # 'trial', 'active', 'expired'
    trial_ends_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30), nullable=True)
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    subscription_plan = db.Column(db.String(50), default='VinZie Free Trial (1 Month)', nullable=False)

    # Relationships: Deleting a user automatically cascades and deletes their financial records
    incomes = db.relationship('Income', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    expenses = db.relationship('Expense', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    budgets = db.relationship('Budget', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    reports = db.relationship('FinancialReport', backref='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password: str) -> None:
        """Hash and store user password using PBKDF2-SHA256."""
        if not password or len(password.strip()) < 6:
            raise ValueError("Password must be at least 6 characters long.")
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify candidate password against stored cryptographic hash."""
        if not password or not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def is_subscription_active(self) -> bool:
        """Check if user has an active 30-day free trial or paid active subscription."""
        now = datetime.utcnow()
        if self.subscription_status == 'active':
            return bool(self.subscription_expires_at and self.subscription_expires_at >= now)
        if self.subscription_status == 'trial':
            trial_limit = self.trial_ends_at or (self.created_at + timedelta(days=30))
            return bool(trial_limit >= now)
        return False

    def days_remaining(self) -> int:
        """Calculate calendar days remaining in current trial or subscription period."""
        now = datetime.utcnow()
        if self.subscription_status == 'active' and self.subscription_expires_at:
            delta = self.subscription_expires_at - now
            return max(0, delta.days + (1 if delta.seconds > 0 else 0))
        
        trial_limit = self.trial_ends_at or (self.created_at + timedelta(days=30))
        delta = trial_limit - now
        return max(0, delta.days + (1 if delta.seconds > 0 else 0))

    def get_subscription_info(self) -> dict:
        """Return structured subscription state for templates, navigation badges, and paywalls."""
        is_active = self.is_subscription_active()
        days_left = self.days_remaining()
        
        if is_active:
            if self.subscription_status == 'active':
                return {
                    'status': 'active',
                    'is_active': True,
                    'plan_name': self.subscription_plan or 'VinZie Pro (Monthly - ₹100)',
                    'days_remaining': days_left,
                    'badge_text': '💎 Pro Member',
                    'badge_class': 'badge-pro',
                    'notice': f'Pro subscription active — {days_left} days remaining'
                }
            else:
                return {
                    'status': 'trial',
                    'is_active': True,
                    'plan_name': 'VinZie Free Trial (1 Month)',
                    'days_remaining': days_left,
                    'badge_text': f'✨ Trial: {days_left}d left',
                    'badge_class': 'badge-trial',
                    'notice': f'Enjoy your 30-day free trial — {days_left} days remaining'
                }
        else:
            return {
                'status': 'expired',
                'is_active': False,
                'plan_name': 'Trial Expired',
                'days_remaining': 0,
                'badge_text': '⚠️ Trial Expired (Upgrade for ₹100/mo)',
                'badge_class': 'badge-expired',
                'notice': 'Your 30-day free trial has expired. Subscribe for ₹100/month to keep accessing AI features.'
            }

    def activate_subscription(self, duration_days: int = 30, plan_name: str = 'VinZie Pro (Monthly - ₹100)') -> datetime:
        """Activate or extend user subscription by given days (default 30 days for ₹100/month)."""
        now = datetime.utcnow()
        # If already active and unexpired, extend from previous expiration
        if self.subscription_status == 'active' and self.subscription_expires_at and self.subscription_expires_at > now:
            self.subscription_expires_at = self.subscription_expires_at + timedelta(days=duration_days)
        else:
            self.subscription_expires_at = now + timedelta(days=duration_days)
        
        self.subscription_status = 'active'
        self.subscription_plan = plan_name
        return self.subscription_expires_at

    def to_dict(self) -> dict:
        """Serialize user object safely without exposing password hashes."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'currency': self.currency,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'subscription': self.get_subscription_info()
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}'>"
