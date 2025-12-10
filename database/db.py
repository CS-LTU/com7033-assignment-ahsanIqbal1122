"""
SQLite Database Management Module

Handles SQLite database operations for the Stroke Intelligence System.
Manages user authentication, patient reports, and Kaggle dataset integration.

Author: Just Ahsan
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University

Database Schema:
1. users: Authentication and user profiles (doctors, patients, admins)
2. patients: Kaggle stroke prediction dataset (training data)
3. patient_reports: User-submitted patient medical reports

Key Features:
- Automatic database initialization
- Kaggle dataset integration with automatic download
- Safe schema migrations with ALTER TABLE
- Row factory for dict-like access to query results

Dependencies:
- sqlite3: Python built-in SQLite database
- pandas: CSV data import
- kaggle: Kaggle API for dataset download
"""

# Standard library imports
import sqlite3  # SQLite database operations
import pandas as pd  # CSV data manipulation and import
import os  # File system operations

# Local imports
from config import DATABASE_PATH, CSV_FILE  # Database and dataset paths


def get_db():
    """
    Create and return a SQLite database connection.
    
    Returns:
        sqlite3.Connection: Database connection with row_factory set to sqlite3.Row
        
    Features:
        - Row factory enables dict-like access: row['column_name']
        - Thread-safe: Each request gets its own connection
        - Automatic connection management
        
    Example:
        >>> conn = get_db()
        >>> cur = conn.cursor()
        >>> cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        >>> user = cur.fetchone()
        >>> print(user['username'])
    """
    # Connect to SQLite database file
    conn = sqlite3.connect(DATABASE_PATH)
    
    # Enable dict-like access to rows: row['column_name'] instead of row[0]
    conn.row_factory = sqlite3.Row
    
    return conn


def download_kaggle_dataset():
    """
    Download stroke detection dataset from Kaggle using Kaggle API.
    
    Dataset: fedesoriano/stroke-prediction-dataset
    Contains 5,110+ patient records with stroke risk factors
    
    Returns:
        bool: True if download successful, False otherwise
        
    Prerequisites:
        1. Install kaggle package: pip install kaggle
        2. Kaggle API credentials: ~/.kaggle/kaggle.json
           - Create at: https://www.kaggle.com/settings
           - Format: {"username":"your_username","key":"your_api_key"}
        3. Accept dataset terms: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
        
    Features:
        - Automatic authentication with Kaggle API
        - Downloads and unzips dataset automatically
        - Renames CSV file to match application configuration
        - Creates download directory if it doesn't exist
        
    Error Handling:
        - Catches authentication failures
        - Catches network errors
        - Catches file system errors
    """
    try:
        # Import Kaggle API (third-party integration)
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        # Initialize Kaggle API client
        # Requires ~/.kaggle/kaggle.json with API credentials
        api = KaggleApi()
        api.authenticate()  # Authenticate using kaggle.json
        
        # Configure dataset download
        dataset_name = "fedesoriano/stroke-prediction-dataset"  # Kaggle dataset identifier
        download_dir = os.path.dirname(CSV_FILE)  # Extract directory from CSV_FILE path
        os.makedirs(download_dir, exist_ok=True)  # Create directory if it doesn't exist
        
        # Download dataset from Kaggle
        print(f"Downloading Kaggle dataset: {dataset_name}")
        api.dataset_download_files(dataset_name, path=download_dir, unzip=True)
        
        # Find and rename the CSV file to match application configuration
        for file in os.listdir(download_dir):
            # Look for CSV files containing 'stroke' in filename
            if file.endswith('.csv') and 'stroke' in file.lower():
                src = os.path.join(download_dir, file)
                # Rename to standard filename from config.py
                if src != CSV_FILE:
                    os.rename(src, CSV_FILE)
                print(f"Dataset saved to {CSV_FILE}")
                return True
        
        # No matching CSV file found in downloaded files
        print("No stroke CSV found in downloaded files.")
        return False
        
    except Exception as e:
        # Catch all errors: authentication, network, file system
        print(f"Failed to download from Kaggle: {e}")
        return False


def init_db():
    """
    Initialize SQLite database with required tables and schema migrations.
    
    Creates tables:
        1. users: User authentication and profile data
        2. patients: Kaggle stroke prediction dataset (training data)
        
    Features:
        - Idempotent: Safe to call multiple times (CREATE IF NOT EXISTS)
        - Safe schema migrations: Adds missing columns without data loss
        - PRAGMA table_info: Detects existing columns before ALTER TABLE
        
    Schema Migrations:
        Automatically adds new profile columns to users table:
        - first_name, last_name: User full name split
        - department: Doctor's department
        - address: Patient residential address
        - mobile: Contact number
        - symptoms: Patient symptoms
        - assigned_doctor_id: Doctor assigned to patient
        - approved: Admin approval status (0=pending, 1=approved)
        
    Called by:
        - app.py on application startup
        - setup scripts for database initialization
    """
    # Get database connection
    conn = get_db()
    cur = conn.cursor()

    # ============================================================
    # USERS TABLE - Authentication and Profile Data
    # ============================================================
    # Stores user accounts for doctors, patients, and admins
    # Security: password_hash stores bcrypt hash, never plain text
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,       -- Unique user ID
            username TEXT UNIQUE NOT NULL,               -- Login username (unique)
            password_hash TEXT NOT NULL,                 -- Bcrypt password hash
            role TEXT NOT NULL DEFAULT 'patient',        -- User role: admin/doctor/patient
            full_name TEXT,                              -- Full name for display
            email TEXT,                                  -- Email address
            hospital_id TEXT,                            -- Hospital/clinic identifier
            patient_id TEXT,                             -- Patient medical record number
            license_number TEXT,                         -- Doctor license number
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Account creation time
        );
    """)

    # ============================================================
    # PATIENTS TABLE - Kaggle Training Dataset
    # ============================================================
    # Contains 5,110+ patient records from Kaggle stroke prediction dataset
    # Used for stroke risk analysis and machine learning model training
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,                      -- Patient record ID
            gender TEXT,                                 -- Male/Female/Other
            age REAL,                                    -- Age in years
            hypertension INTEGER,                        -- 0=No, 1=Yes (Has hypertension)
            heart_disease INTEGER,                       -- 0=No, 1=Yes (Has heart disease)
            ever_married TEXT,                           -- Yes/No (Marital status)
            work_type TEXT,                              -- Private/Self-employed/Govt/etc
            Residence_type TEXT,                         -- Rural/Urban
            avg_glucose_level REAL,                      -- Average glucose level (mg/dL)
            bmi REAL,                                    -- Body Mass Index
            smoking_status TEXT,                         -- Never/Formerly/Smokes/Unknown
            stroke INTEGER                               -- 0=No stroke, 1=Had stroke (target variable)
        );
    """)

    conn.commit()
    
    # ============================================================
    # SAFE SCHEMA MIGRATIONS - Add Missing Columns
    # ============================================================
    # Use PRAGMA table_info to detect existing columns before ALTER TABLE
    # This prevents "duplicate column name" errors
    cur.execute("PRAGMA table_info(users);")
    existing = [r[1] for r in cur.fetchall()]  # Extract column names

    # List of additional profile columns to add
    # Format: (column_name, column_type)
    extra_columns = [
        ("first_name", "TEXT"),                          # User first name
        ("last_name", "TEXT"),                           # User last name
        ("department", "TEXT"),                          # Doctor's department
        ("address", "TEXT"),                             # Patient address
        ("mobile", "TEXT"),                              # Contact phone number
        ("symptoms", "TEXT"),                            # Patient symptoms
        ("assigned_doctor_id", "INTEGER"),               # Foreign key to doctor user ID
        ("approved", "INTEGER DEFAULT 0"),               # Admin approval flag (0=pending, 1=approved)
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")  # Record creation time
    ]

    # Add missing columns one by one
    for col_name, col_type in extra_columns:
        if col_name not in existing:
            # Construct ALTER TABLE statement
            alter_sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"
            try:
                cur.execute(alter_sql)
            except Exception:
                # Ignore errors: column may already exist or table in unexpected state
                # This ensures migrations don't break application startup
                pass

    # Commit all changes and close connection
    conn.commit()
    conn.close()


def import_csv_if_needed():
    """
    Import Kaggle stroke prediction dataset into SQLite database if patients table is empty.
    
    Workflow:
        1. Check if patients table already has data (count > 0)
        2. If empty, try to load CSV from local file system
        3. If local CSV not found, attempt Kaggle API download
        4. Import CSV data into patients table using pandas
        
    Data Source:
        - Dataset: Kaggle Stroke Prediction Dataset (5,110+ records)
        - Author: fedesoriano
        - URL: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
        
    Features:
        - Idempotent: Only imports if table is empty (prevents duplicates)
        - Automatic Kaggle download fallback
        - Pandas DataFrame for efficient CSV import
        - Error handling for file and import errors
        
    Called by:
        - app.py on application startup
        - Ensures training data is available for stroke prediction
    """
    # Get database connection
    conn = get_db()
    cur = conn.cursor()

    # Check if patients table already has data
    cur.execute("SELECT COUNT(*) FROM patients;")
    count = cur.fetchone()[0]

    # Only import if table is empty (prevents duplicate imports)
    if count == 0:
        # ============================================================
        # STEP 1: Try to load CSV from local file system
        # ============================================================
        if os.path.exists(CSV_FILE):
            print(f"Loading data from {CSV_FILE}")
            df = pd.read_csv(CSV_FILE)  # Read CSV into pandas DataFrame
        else:
            # ============================================================
            # STEP 2: CSV not found locally - try Kaggle API download
            # ============================================================
            print("CSV not found locally. Attempting to download from Kaggle...")
            if download_kaggle_dataset():
                # Download successful - read the CSV
                df = pd.read_csv(CSV_FILE)
            else:
                # Download failed - cannot proceed without dataset
                print("Could not load dataset. Please ensure CSV exists or set up Kaggle API credentials.")
                conn.close()
                return
        
        # ============================================================
        # STEP 3: Import DataFrame into SQLite database
        # ============================================================
        try:
            # Use pandas to_sql for efficient bulk insert
            # if_exists="append": Add rows to existing table
            # index=False: Don't import DataFrame index as column
            df.to_sql("patients", conn, if_exists="append", index=False)
            print(f"✓ Imported {len(df)} patients into database.")
        except Exception as e:
            print(f"Error importing data: {e}")
    
    # Close database connection
    conn.close()

