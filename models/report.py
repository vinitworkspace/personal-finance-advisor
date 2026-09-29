from datetime import datetime
from models import db

class FinancialReport(db.Model):
    """Archived monthly financial snapshot containing aggregates and AI-generated insights."""
    __tablename__ = 'financial_reports'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    total_income = db.Column(db.Float, default=0.0, nullable=False)
    total_expenses = db.Column(db.Float, default=0.0, nullable=False)
    total_savings = db.Column(db.Float, default=0.0, nullable=False)
    savings_percentage = db.Column(db.Float, default=0.0, nullable=False)
    ai_summary = db.Column(db.Text, nullable=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'month', 'year', name='uq_user_report_month_year'),
    )

    def to_dict(self) -> dict:
        """Serialize report summary for dashboard or archive display."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'month': self.month,
            'year': self.year,
            'total_income': round(float(self.total_income), 2),
            'total_expenses': round(float(self.total_expenses), 2),
            'total_savings': round(float(self.total_savings), 2),
            'savings_percentage': round(float(self.savings_percentage), 2),
            'ai_summary': self.ai_summary or '',
            'generated_at': self.generated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self) -> str:
        return f"<FinancialReport id={self.id} user_id={self.user_id} period='{self.month}/{self.year}' savings={self.total_savings}>"
