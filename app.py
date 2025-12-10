"""
Stroke Pass - Main Application Entry Point

This is the main Flask application file that initializes and configures the web application.
It sets up CSRF protection, database connections, and registers all route blueprints.

Author: Just Ahsan
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University

Security Features:
- CSRF protection on all forms (Flask-WTF)
- Session-based authentication
- Secure secret key configuration
- SQLite and MongoDB dual-database architecture
"""

# Flask framework imports
from flask import Flask
from flask_wtf.csrf import CSRFProtect  # CSRF protection for forms

# Configuration imports
from config import SECRET_KEY, DATABASE_PATH

# Database initialization functions
from database.db import init_db, import_csv_if_needed

# Route blueprints for modular routing
from routes.auth_routes import auth_bp  # Authentication routes (login, register, logout)
from routes.patient_routes import patients_bp  # Patient CRUD routes (SQLite)
from routes.dashboard_routes import dashboard_bp  # Dashboard routes (admin, doctor, patient)
from routes.mongo_patient_routes import mongo_patients_bp  # MongoDB patient routes

# Version tracking
from version import VERSION, RELEASE_DATE

# Standard library imports
import os


# Initialize Flask application
app = Flask(__name__)

# Configure secret key for session encryption
# WARNING: In production, use environment variable instead of hardcoded value
app.secret_key = SECRET_KEY

# Enable CSRF protection for all forms
# This prevents Cross-Site Request Forgery attacks by requiring a token on POST requests
csrf = CSRFProtect(app)

# Add version information to application context
# Makes VERSION and RELEASE_DATE available in all templates
app.config['VERSION'] = VERSION
app.config['RELEASE_DATE'] = RELEASE_DATE

# Ensure instance directory exists for the SQLite database
# The instance folder stores the SQLite database file
instance_dir = os.path.dirname(DATABASE_PATH)
if instance_dir and not os.path.exists(instance_dir):
    os.makedirs(instance_dir, exist_ok=True)

# Initialize SQLite database with tables
# Creates users and patient_reports tables if they don't exist
init_db()

# Import Kaggle dataset CSV into SQLite if not already imported
# Loads 5,110 stroke patient records for testing and demonstration
import_csv_if_needed()

# Register route blueprints
# Blueprints organize routes into modular components
app.register_blueprint(auth_bp)  # /login, /register_patient, /register_doctor, /logout
app.register_blueprint(patients_bp)  # /patients, /patient/add, /patient/edit, /patient/delete
app.register_blueprint(dashboard_bp)  # /admin_dashboard, /doctor_dashboard, /patient_dashboard
app.register_blueprint(mongo_patients_bp)  # /mongo/patients, /mongo/add, /mongo/edit, /mongo/delete


# Application entry point
if __name__ == "__main__":
    # Run Flask development server
    # WARNING: Debug mode should be False in production
    app.run(debug=True)
