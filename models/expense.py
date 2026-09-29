from datetime import datetime, date
from models import db

class Expense(db.Model):
    """Expense entry representing cash outflows for a user."""
    __tablename__ = 'expenses'

    CATEGORIES = [
        'Food',
        'Rent',
        'Transport',
        'Utilities',
        'Entertainment',
        'Shopping',
        'Healthcare',
        'Education',
        'EMI',
        'Other'
    ]

    PAYMENT_METHODS = ['UPI/Card', 'Cash', 'NetBanking', 'Cheque', 'Other']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True, default='Other')
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    description = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), default='UPI/Card', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Serialize expense instance to JSON-serializable dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': round(float(self.amount), 2),
            'category': self.category,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'description': self.description or '',
            'payment_method': self.payment_method,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self) -> str:
        return f"<Expense id={self.id} user_id={self.user_id} amount={self.amount} category='{self.category}'>"
