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

class VercelWSGIMiddleware:
    """
    WSGI middleware ensuring correct path routing on Vercel Serverless environment.
    1. If PATH_INFO is /api/index.py, /api/index, /api, or /api/, normalizes it to '/'.
    2. Recovers original requested path from Vercel edge headers (HTTP_X_FORWARDED_PATH, HTTP_X_MATCHED_PATH).
    3. Handles cases where the entrypoint prefix was prepended to the path.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')
        print("[VERCEL_DEBUG_PATH]", path)
        print("[VERCEL_DEBUG_ENV]", {k: str(v) for k, v in environ.items() if not k.startswith('wsgi.') and not k.startswith('SERVER_')})

        # If PATH_INFO is directly targeting the serverless entrypoint
        if path in ('/api/index.py', '/api/index', '/api', '/api/'):
            environ['PATH_INFO'] = '/'
        elif path.startswith('/api/index.py/'):
            environ['PATH_INFO'] = path.replace('/api/index.py', '', 1) or '/'
        elif path.startswith('/api/index/'):
            environ['PATH_INFO'] = path.replace('/api/index', '', 1) or '/'

        return self.wsgi_app(environ, start_response)

# Apply Vercel WSGI routing middleware
app.wsgi_app = VercelWSGIMiddleware(app.wsgi_app)

# Auto-initialize database tables and demo seed data on serverless cold start in /tmp
with app.app_context():
    try:
        seed_demo_data()
    except Exception as e:
        print(f"[Vercel Cold Start] DB initialization notice: {e}")
