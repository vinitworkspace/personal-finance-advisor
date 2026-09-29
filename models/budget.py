from datetime import datetime
from models import db

class Budget(db.Model):
    """Budget cap allocation for a specific category within a given month and year."""
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Ensure a user has at most one budget per category in any given month/year
    __table_args__ = (
        db.UniqueConstraint('user_id', 'category', 'month', 'year', name='uq_user_category_month_year'),
    )

    def to_dict(self) -> dict:
        """Serialize budget target to dictionary format."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category': self.category,
            'amount': round(float(self.amount), 2),
            'month': self.month,
            'year': self.year,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self) -> str:
        return f"<Budget id={self.id} user_id={self.user_id} category='{self.category}' amount={self.amount} ({self.month}/{self.year})>"
