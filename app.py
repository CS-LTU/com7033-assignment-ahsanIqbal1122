from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import SECRET_KEY, DATABASE_PATH
from database.db import init_db, import_csv_if_needed
from routes.auth_routes import auth_bp
from routes.patient_routes import patients_bp
from routes.dashboard_routes import dashboard_bp
from routes.mongo_patient_routes import mongo_patients_bp
from version import VERSION, RELEASE_DATE
import os


app = Flask(__name__)
app.secret_key = SECRET_KEY

# Enable CSRF protection for all forms
csrf = CSRFProtect(app)

# Add version info to app context
app.config['VERSION'] = VERSION
app.config['RELEASE_DATE'] = RELEASE_DATE

# Ensure instance directory exists for the SQLite database
instance_dir = os.path.dirname(DATABASE_PATH)
if instance_dir and not os.path.exists(instance_dir):
    os.makedirs(instance_dir, exist_ok=True)

# Initialize SQLite + Load CSV
init_db()
import_csv_if_needed()

# Register routes
app.register_blueprint(auth_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(mongo_patients_bp)


if __name__ == "__main__":
    app.run(debug=True)
