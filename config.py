import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project base directory
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# Ensure local database directory exists
DB_DIR = BASE_DIR / 'database'
DB_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_DB_FILE = (DB_DIR / 'finance.db').resolve()

class Config:
    """Base application configuration with robust cross-platform path resolution."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_insecure_fallback_key_2026')
    
    # SQLite Database URI configuration
    # Resolves relative sqlite:/// URIs against project root to prevent Flask-SQLAlchemy instance-folder traps
    raw_db_url = os.getenv('DATABASE_URL', '')
    if raw_db_url.startswith('sqlite:///') and not raw_db_url.startswith('sqlite:////'):
        rel_path = raw_db_url.replace('sqlite:///', '')
        if not (Path(rel_path).is_absolute() or ':' in rel_path):
            resolved_path = (BASE_DIR / rel_path).resolve()
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{resolved_path.as_posix()}"
        else:
            SQLALCHEMY_DATABASE_URI = raw_db_url
    elif raw_db_url:
        SQLALCHEMY_DATABASE_URI = raw_db_url
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security settings for session cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours in seconds

    # Google Gemini AI settings
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '').strip()
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

    # Default application currency symbol
    DEFAULT_CURRENCY = '₹'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration with in-memory database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test_secret_key'

# Configuration mapping dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
