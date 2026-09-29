from datetime import datetime, date
from models import db

class Income(db.Model):
    """Income entry representing cash inflows for a user."""
    __tablename__ = 'incomes'

    SOURCES = ['Salary', 'Freelance', 'Allowance', 'Business', 'Investment', 'Other']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    source = db.Column(db.String(50), nullable=False, default='Other')
    date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self) -> dict:
        """Serialize income instance to JSON-serializable dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': round(float(self.amount), 2),
            'source': self.source,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'description': self.description or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self) -> str:
        return f"<Income id={self.id} user_id={self.user_id} amount={self.amount} source='{self.source}'>"
