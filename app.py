import os
from flask import Flask, jsonify, render_template, request
from config import config_by_name
from models import db
from routes.auth import auth_bp, get_current_user
from routes.dashboard import dashboard_bp
from routes.income import income_bp
from routes.expenses import expenses_bp
from routes.budget import budget_bp
from routes.analytics import analytics_bp
from routes.ai import ai_bp
from routes.reports import reports_bp

def create_app(config_name: str = None) -> Flask:
    """Application factory for Personal Finance Advisor Bot."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Ensure database parent directory exists (skipped if read-only or in serverless)
    try:
        if not os.getenv('VERCEL'):
            os.makedirs(os.path.join(app.root_path, 'database'), exist_ok=True)
    except OSError:
        pass

    # Initialize database extensions
    db.init_app(app)

    # Register application blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(reports_bp)

    # Context processor: make authenticated user accessible in all Jinja templates
    @app.context_processor
    def inject_global_template_context():
        return {
            'current_user': get_current_user()
        }

    # Health check endpoint for system monitoring
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Personal Finance Advisor Bot',
            'database': 'SQLite connected'
        }), 200

    # Error handlers preventing stack trace leakage
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found', 'status': 404}), 404
        return render_template('base.html', error_message="Page Not Found"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error occurred', 'status': 500}), 500
        return render_template('base.html', error_message="An unexpected server error occurred"), 500

    return app

if __name__ == '__main__':
    app = create_app('development')
    print("=" * 60)
    print(" Personal Finance Advisor Bot is running!")
    print(" Local URL: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
