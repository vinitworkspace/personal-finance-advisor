"""
Vercel Serverless Function Entrypoint for Personal Finance Advisor Bot.
Handles WSGI request routing and auto-initializes the database in /tmp on cold start.
"""
import os
import sys
from pathlib import Path

# Add project root directory to Python module search path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Mark environment as Vercel
os.environ['VERCEL'] = '1'

from app import create_app
from init_db import seed_demo_data

# Create production Flask WSGI application instance
app = create_app('production')

# Auto-initialize database tables and demo seed data on serverless cold start in /tmp
with app.app_context():
    try:
        seed_demo_data()
    except Exception as e:
        print(f"[Vercel Cold Start] DB initialization notice: {e}")
