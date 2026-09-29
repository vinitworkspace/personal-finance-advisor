from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance without binding to specific app yet (Application Factory Pattern)
db = SQLAlchemy()

# Import models to ensure they register with SQLAlchemy metadata
from models.user import User
from models.income import Income
from models.expense import Expense
from models.budget import Budget
from models.report import FinancialReport

__all__ = ['db', 'User', 'Income', 'Expense', 'Budget', 'FinancialReport']
