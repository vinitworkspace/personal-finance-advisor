from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    """User account model with secure password hashing and relationship cascades."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    currency = db.Column(db.String(10), default='₹', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

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

    def to_dict(self) -> dict:
        """Serialize user object safely without exposing password hashes."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'currency': self.currency,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}'>"
