import sqlite3
import pandas as pd
import os
from config import DATABASE_PATH, CSV_FILE

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def download_kaggle_dataset():
    """Download stroke detection dataset from Kaggle using Kaggle API"""
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        
        # Initialize Kaggle API
        api = KaggleApi()
        api.authenticate()
        
        # Download dataset
        dataset_name = "fedesoriano/stroke-prediction-dataset"
        download_dir = os.path.dirname(CSV_FILE)
        os.makedirs(download_dir, exist_ok=True)
        
        print(f"Downloading Kaggle dataset: {dataset_name}")
        api.dataset_download_files(dataset_name, path=download_dir, unzip=True)
        
        # Find and rename the CSV file
        for file in os.listdir(download_dir):
            if file.endswith('.csv') and 'stroke' in file.lower():
                src = os.path.join(download_dir, file)
                if src != CSV_FILE:
                    os.rename(src, CSV_FILE)
                print(f"Dataset saved to {CSV_FILE}")
                return True
        
        print("No stroke CSV found in downloaded files.")
        return False
    except Exception as e:
        print(f"Failed to download from Kaggle: {e}")
        return False


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # USERS - Enhanced with profile info
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'patient',
            full_name TEXT,
            email TEXT,
            hospital_id TEXT,
            patient_id TEXT,
            license_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # PATIENTS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            gender TEXT,
            age REAL,
            hypertension INTEGER,
            heart_disease INTEGER,
            ever_married TEXT,
            work_type TEXT,
            Residence_type TEXT,
            avg_glucose_level REAL,
            bmi REAL,
            smoking_status TEXT,
            stroke INTEGER
        );
    """)

    conn.commit()
    # Ensure additional profile columns exist (safe migrations)
    cur.execute("PRAGMA table_info(users);")
    existing = [r[1] for r in cur.fetchall()]

    extra_columns = [
        ("first_name", "TEXT"),
        ("last_name", "TEXT"),
        ("department", "TEXT"),
        ("address", "TEXT"),
        ("mobile", "TEXT"),
        ("symptoms", "TEXT"),
        ("assigned_doctor_id", "INTEGER"),
        ("approved", "INTEGER DEFAULT 0"),
        ("created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]

    for col_name, col_type in extra_columns:
        if col_name not in existing:
            alter_sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"
            try:
                cur.execute(alter_sql)
            except Exception:
                # If ALTER TABLE fails for any reason, continue; table may be in unexpected state
                pass

    conn.commit()
    conn.close()


def import_csv_if_needed():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM patients;")
    count = cur.fetchone()[0]

    if count == 0:
        # Try local CSV first
        if os.path.exists(CSV_FILE):
            print(f"Loading data from {CSV_FILE}")
            df = pd.read_csv(CSV_FILE)
        else:
            # If no local CSV, try to download from Kaggle
            print("CSV not found locally. Attempting to download from Kaggle...")
            if download_kaggle_dataset():
                df = pd.read_csv(CSV_FILE)
            else:
                print("Could not load dataset. Please ensure CSV exists or set up Kaggle API credentials.")
                conn.close()
                return
        
        # Import the data
        try:
            df.to_sql("patients", conn, if_exists="append", index=False)
            print(f"✓ Imported {len(df)} patients into database.")
        except Exception as e:
            print(f"Error importing data: {e}")
    
    conn.close()

