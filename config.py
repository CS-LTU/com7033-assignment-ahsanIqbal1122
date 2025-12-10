"""
Configuration File - Basic Settings

This file contains basic configuration settings for the Flask application.
For advanced configuration with environment variables, see config_env.py

Author: Ahsan Iqbal
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University

Security Note:
- SECRET_KEY should be changed to a random string in production
- Use environment variables for sensitive configuration (see config_env.py)
- Never commit actual secret keys to version control
"""

import os

# Base directory - absolute path to the project root
# Used as a reference point for all other paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Secret key for Flask session encryption
# WARNING: Change this to a secure random string in production
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY = "change_this_to_something_random"

# SQLite database path
# Database file stored in instance/ directory
# Contains users table and patient_reports table
DATABASE_PATH = os.path.join(BASE_DIR, "instance", "stroke.db")

# Kaggle dataset CSV file path
# Contains 5,110 stroke patient records for demonstration
# Source: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
CSV_FILE = os.path.join(BASE_DIR, "healthcare-dataset-stroke-data.csv")
