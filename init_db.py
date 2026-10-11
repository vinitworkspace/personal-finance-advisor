"""
Database initialization and verification script for VinZie Budget Tracker.
Creates SQLite tables and seeds initial test data for demonstration.
"""
from datetime import date
from sqlalchemy import inspect, text
from models import db, User, Income, Expense, Budget, FinancialReport

def ensure_schema_migrations():
    """Ensure newly added subscription columns exist in SQLite database gracefully."""
    try:
        inspector = inspect(db.engine)
        if 'users' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('users')]
            with db.engine.begin() as conn:
                if 'subscription_status' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN subscription_status VARCHAR(20) DEFAULT 'trial' NOT NULL"))
                if 'trial_ends_at' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN trial_ends_at DATETIME"))
                if 'subscription_expires_at' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN subscription_expires_at DATETIME"))
                if 'subscription_plan' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN subscription_plan VARCHAR(50) DEFAULT 'VinZie Free Trial (1 Month)' NOT NULL"))
                if 'phone_number' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)"))
                if 'pin_hash' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN pin_hash VARCHAR(255)"))
                if 'biometric_enabled' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN biometric_enabled BOOLEAN DEFAULT 0 NOT NULL"))
                if 'auth_provider' not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(30) DEFAULT 'email' NOT NULL"))
    except Exception as err:
        print(f"[Schema Migration Warning] {err}")

def seed_demo_data():
    """Create all tables and seed sample data if demo user does not exist."""
    db.create_all()
    ensure_schema_migrations()

    demo_user = User.query.filter_by(email="demo@finance.test").first()
    if not demo_user:
        demo_user = User(
            name="Demo Student",
            email="demo@finance.test",
            phone_number="9876543210",
            biometric_enabled=True,
            currency="₹",
            subscription_status="trial",
            subscription_plan="VinZie Free Trial (1 Month)"
        )
        demo_user.set_password("Password123!")
        demo_user.set_pin("1234")
        db.session.add(demo_user)
        db.session.commit()
    else:
        if not demo_user.pin_hash:
            demo_user.set_pin("1234")
            demo_user.biometric_enabled = True
            if not demo_user.phone_number:
                demo_user.phone_number = "9876543210"
            db.session.commit()

        # Seed sample income
        sample_income = Income(
            user_id=demo_user.id,
            amount=50000.0,
            source="Salary",
            date=date.today(),
            description="Monthly Primary Salary"
        )
        db.session.add(sample_income)

        # Seed sample expenses
        sample_expenses = [
            Expense(user_id=demo_user.id, amount=15000.0, category="Rent", date=date.today(), description="Monthly Apartment Rent"),
            Expense(user_id=demo_user.id, amount=7000.0, category="Food", date=date.today(), description="Groceries & Dining"),
            Expense(user_id=demo_user.id, amount=3000.0, category="Utilities", date=date.today(), description="Electricity & High-speed Internet"),
            Expense(user_id=demo_user.id, amount=4000.0, category="Transport", date=date.today(), description="Metro pass and Fuel"),
            Expense(user_id=demo_user.id, amount=3500.0, category="Entertainment", date=date.today(), description="Movies and streaming")
        ]
        db.session.add_all(sample_expenses)

        # Seed sample budget
        sample_budget = Budget(
            user_id=demo_user.id,
            category="Food",
            amount=8000.0,
            month=date.today().month,
            year=date.today().year
        )
        db.session.add(sample_budget)
        db.session.commit()
        return True
    return False

def initialize_database():
    from app import create_app
    app = create_app('development')
    
    with app.app_context():
        # Drop temporary test table if present
        try:
            db.session.execute(text("DROP TABLE IF EXISTS test"))
            db.session.commit()
        except Exception:
            pass

        print("-" * 65)
        print(" [1/3] Initializing SQLite database tables...")
        db.create_all()
        
        inspector = inspect(db.engine)
        table_names = [t for t in inspector.get_table_names() if t != 'test']
        print(f"       Tables successfully detected ({len(table_names)}): {', '.join(table_names)}")
        
        print("\n [2/3] Checking schema structure:")
        for table in table_names:
            cols = [col['name'] for col in inspector.get_columns(table)]
            print(f"       * {table.ljust(18)} : {', '.join(cols)}")

        print("\n [3/3] Seeding demo student/viva user account...")
        seeded = seed_demo_data()
        if seeded:
            print("       [OK] Created demo user: demo@finance.test (Password: Password123!)")
            print("       [OK] Seeded baseline transactions (Scenario 1: Salaried Professional)")
        else:
            print("       [OK] Demo user account already exists. Ready.")

        print("-" * 65)
        print(" [SUCCESS] Phase 1 Database & Model Layer is fully operational!")
        print("-" * 65)

if __name__ == '__main__':
    initialize_database()
