"""
Environment Configuration

Configuration management using environment variables and .env file support.
Implements secure configuration practices with python-dotenv integration.

Security Features:
- Sensitive data in environment variables (not hardcoded)
- Secret key generation
- Configurable security settings
- Development vs Production modes

Author: Just Ahsan
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University
"""

import os
import secrets
from pathlib import Path
from typing import Optional

# Try to load python-dotenv (optional dependency)
try:
    from dotenv import load_dotenv
    # Load .env file if it exists
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"✓ Loaded environment variables from {env_path}")
    else:
        print("ℹ No .env file found, using system environment variables")
except ImportError:
    print("ℹ python-dotenv not installed. Install with: pip install python-dotenv")


class Config:
    """
    Base configuration class with environment variable support.
    
    Environment variables can be set in:
    1. .env file (recommended for development)
    2. System environment variables (recommended for production)
    3. Default values (fallback)
    """
    
    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'Stroke Pass')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    TESTING = os.getenv('TESTING', 'False').lower() in ('true', '1', 'yes')
    
    # Secret Key (MUST be changed in production!)
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        # Generate random secret key if not provided
        SECRET_KEY = secrets.token_hex(32)
        print(f"⚠ WARNING: Using generated SECRET_KEY. Set SECRET_KEY in .env file for production!")
    
    # Database Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_PATH = os.getenv('DATABASE_PATH', os.path.join(BASE_DIR, "instance", "stroke.db"))
    CSV_FILE = os.getenv('CSV_FILE', os.path.join(BASE_DIR, "healthcare-dataset-stroke-data.csv"))
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'stroke_db')
    
    # Security Settings
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_HTTPONLY = True  # Always True for security
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', 3600))  # 1 hour
    
    # CSRF Protection
    WTF_CSRF_ENABLED = os.getenv('WTF_CSRF_ENABLED', 'True').lower() in ('true', '1', 'yes')
    WTF_CSRF_TIME_LIMIT = int(os.getenv('WTF_CSRF_TIME_LIMIT', 3600))  # 1 hour
    
    # Rate Limiting (requires Flask-Limiter)
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() in ('true', '1', 'yes')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    
    # Password Hashing
    PASSWORD_HASH_METHOD = os.getenv('PASSWORD_HASH_METHOD', 'scrypt')
    
    # File Upload Settings
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'csv', 'txt', 'pdf', 'png', 'jpg', 'jpeg'}
    
    @classmethod
    def get_config_summary(cls) -> str:
        """
        Get a summary of current configuration (for debugging).
        
        Returns:
            str: Configuration summary (sensitive data masked)
        """
        summary = f"""
Configuration Summary
=====================
App Name: {cls.APP_NAME}
Debug Mode: {cls.DEBUG}
Testing Mode: {cls.TESTING}
Database: {cls.DATABASE_PATH}
MongoDB: {cls.MONGO_URI} / {cls.MONGO_DB_NAME}
Secret Key: {'*' * 20} (masked)
CSRF Enabled: {cls.WTF_CSRF_ENABLED}
Rate Limiting: {cls.RATELIMIT_ENABLED}
Log Level: {cls.LOG_LEVEL}
Session Lifetime: {cls.PERMANENT_SESSION_LIFETIME}s
"""
        return summary
    
    @classmethod
    def validate_config(cls) -> tuple[bool, list[str]]:
        """
        Validate configuration and return any warnings.
        
        Returns:
            tuple[bool, list[str]]: (is_valid, list of warning messages)
        """
        warnings = []
        
        # Check if SECRET_KEY is the default
        if len(cls.SECRET_KEY) < 32:
            warnings.append("SECRET_KEY is too short (minimum 32 characters)")
        
        # Check if database path is accessible
        db_dir = os.path.dirname(cls.DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            warnings.append(f"Database directory does not exist: {db_dir}")
        
        # Check if DEBUG is enabled in production-like settings
        if cls.DEBUG and cls.SESSION_COOKIE_SECURE:
            warnings.append("DEBUG mode enabled with secure cookies (possible production environment)")
        
        # Check if CSRF is disabled
        if not cls.WTF_CSRF_ENABLED:
            warnings.append("CSRF protection is disabled (security risk)")
        
        # Check MongoDB connection
        if 'localhost' not in cls.MONGO_URI and not cls.MONGO_URI.startswith('mongodb+srv'):
            warnings.append(f"MongoDB URI may be invalid: {cls.MONGO_URI}")
        
        is_valid = len(warnings) == 0
        return is_valid, warnings


class DevelopmentConfig(Config):
    """Development configuration with debug enabled."""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration with security hardened."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True
    RATELIMIT_ENABLED = True


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing
    DATABASE_PATH = ':memory:'  # Use in-memory database


def get_config(environment: Optional[str] = None) -> Config:
    """
    Get configuration based on environment.
    
    Args:
        environment (Optional[str]): Environment name ('development', 'production', 'testing')
                                     If None, reads from FLASK_ENV environment variable
    
    Returns:
        Config: Configuration instance
    """
    if environment is None:
        environment = os.getenv('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(environment.lower(), DevelopmentConfig)
    return config_class()


# Example .env file template
ENV_TEMPLATE = """
# Stroke Pass Application - Environment Configuration
# Copy this to .env and customize for your environment

# Application Settings
APP_NAME=Stroke Pass
DEBUG=True
FLASK_ENV=development

# Security (CHANGE THIS!)
SECRET_KEY=your-secret-key-here-generate-with-secrets-token-hex-32

# Database
DATABASE_PATH=./instance/stroke.db
CSV_FILE=./healthcare-dataset-stroke-data.csv

# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=stroke_db

# Session Security
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=3600

# CSRF Protection
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600

# Rate Limiting
RATELIMIT_ENABLED=True
RATELIMIT_DEFAULT=100 per hour

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs

# Password Hashing
PASSWORD_HASH_METHOD=scrypt
"""


if __name__ == '__main__':
    # Test configuration
    config = get_config()
    print(config.get_config_summary())
    
    is_valid, warnings = config.validate_config()
    if warnings:
        print("\n⚠ Configuration Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    else:
        print("\n✓ Configuration is valid")
    
    # Generate .env template
    if not os.path.exists('.env'):
        with open('.env.example', 'w') as f:
            f.write(ENV_TEMPLATE)
        print("\n✓ Created .env.example template")
