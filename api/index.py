"""
Vercel Serverless Function Entrypoint for VinZie Budget Tracker.
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

from urllib.parse import parse_qs, urlencode

# Create production Flask WSGI application instance
app = create_app('production')

class VercelWSGIMiddleware:
    """
    WSGI middleware ensuring correct path routing on Vercel Serverless environment.
    1. Recovers true requested path passed via __vercel_route__ query param from vercel.json.
    2. Strips internal routing query param and reconstructs original query string.
    3. Safely normalizes direct hits to /api/index, /api/index.py, /api to root '/'.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        query_string = environ.get('QUERY_STRING', '')

        # Check if true route was passed via rewrite query parameter
        if '__vercel_route__' in query_string:
            params = parse_qs(query_string, keep_blank_values=True)
            route_val = params.pop('__vercel_route__', [None])[0]
            if route_val:
                clean_path = '/' + route_val.lstrip('/')
                environ['PATH_INFO'] = clean_path
                # Rebuild original query string without the routing parameter
                flat_params = [(k, v) for k, vs in params.items() for v in vs]
                environ['QUERY_STRING'] = urlencode(flat_params)
        else:
            path = environ.get('PATH_INFO', '')
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
