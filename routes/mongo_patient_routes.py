"""
MongoDB Patient Routes Module

Handles CRUD operations for patient records stored in MongoDB (NoSQL database).

Author: Just Ahsan
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University

Features:
    - List all MongoDB patient records
    - Add new patient to MongoDB
    - Edit existing MongoDB patient
    - Delete MongoDB patient
    - Flexible NoSQL schema (no fixed columns required)

Database Architecture:
    - SQLite: Structured data (users, Kaggle dataset, patient reports)
    - MongoDB: Flexible patient records with varying schemas
    
Security:
    - @staff_required decorator: Restricts access to admin and doctor roles
    - Session-based authentication
    - ObjectId validation for MongoDB document IDs
    - Input validation for numeric fields

MongoDB Operations:
    - Collection: patients
    - Uses BSON ObjectId for document identification
    - Supports flexible schema without migrations

Note:
    This module demonstrates NoSQL database integration.
    For SQLite patient data (Kaggle dataset), see patient_routes.py.
"""

# Flask imports
from flask import Blueprint, render_template, redirect, url_for, flash, request, session

# Standard library imports
from functools import wraps  # Preserves function metadata in decorators

# Third-party imports
from bson.objectid import ObjectId  # MongoDB document ID type

# Local imports
from database.mongo import add_patient, get_patient, update_patient, delete_patient, list_patients

# Initialize Flask Blueprint for MongoDB patient routes
mongo_patients_bp = Blueprint("mongo_patients", __name__)


# ============================================================
# ACCESS CONTROL DECORATOR
# ============================================================

def staff_required(f):
    """
    Decorator to restrict access to admin and doctor roles only.
    
    Prevents patients from accessing MongoDB CRUD operations.
    Only staff members (admin, doctor) can manage NoSQL patient records.
    
    Args:
        f: Flask route function to wrap
        
    Returns:
        Decorated function with role-based access control
        
    Behavior:
        - Not logged in: Redirect to login page
        - Patient role: Redirect to patient dashboard with error message
        - Admin/Doctor: Allow access to route
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Login required", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") not in ("admin", "doctor"):
            flash("Access denied.", "danger")
            return redirect(url_for("dashboard.patient_dashboard"))
        return f(*args, **kwargs)
    return wrapper

@mongo_patients_bp.route("/mongo/patients")
@staff_required
def mongo_list_patients():
    patients = list_patients()
    return render_template("mongo_patients.html", patients=patients, total_count=len(patients))

@mongo_patients_bp.route("/mongo/patients/add", methods=["GET", "POST"])
@staff_required
def mongo_add_patient():
    if request.method == "POST":
        # Input validation
        try:
            age = float(request.form["age"])
            hypertension = int(request.form["hypertension"])
            glucose = float(request.form["avg_glucose_level"])
            bmi = float(request.form["bmi"])
            stroke = int(request.form["stroke"])
        except Exception:
            flash("Invalid numeric values", "danger")
            return redirect(url_for("mongo_patients.mongo_add_patient"))
        patient_data = {
            "gender": request.form["gender"],
            "age": age,
            "hypertension": hypertension,
            "heart_disease": int(request.form.get("heart_disease", 0)),
            "ever_married": request.form["ever_married"],
            "work_type": request.form["work_type"],
            "Residence_type": request.form["Residence_type"],
            "avg_glucose_level": glucose,
            "bmi": bmi,
            "smoking_status": request.form["smoking_status"],
            "stroke": stroke
        }
        add_patient(patient_data)
        flash("Patient added to MongoDB.", "success")
        return redirect(url_for("mongo_patients.mongo_list_patients"))
    return render_template("mongo_patient_form.html", action="Add")

@mongo_patients_bp.route("/mongo/patients/<string:pid>/edit", methods=["GET", "POST"])
@staff_required
def mongo_edit_patient(pid):
    patient = get_patient(ObjectId(pid))
    if not patient:
        flash("Patient not found in MongoDB", "danger")
        return redirect(url_for("mongo_patients.mongo_list_patients"))
    if request.method == "POST":
        try:
            age = float(request.form["age"])
            hypertension = int(request.form["hypertension"])
            glucose = float(request.form["avg_glucose_level"])
            bmi = float(request.form["bmi"])
            stroke = int(request.form["stroke"])
        except Exception:
            flash("Invalid numeric values.", "danger")
            return redirect(url_for("mongo_patients.mongo_edit_patient", pid=pid))
        update_data = {
            "gender": request.form["gender"],
            "age": age,
            "hypertension": hypertension,
            "heart_disease": int(request.form.get("heart_disease", 0)),
            "ever_married": request.form["ever_married"],
            "work_type": request.form["work_type"],
            "Residence_type": request.form["Residence_type"],
            "avg_glucose_level": glucose,
            "bmi": bmi,
            "smoking_status": request.form["smoking_status"],
            "stroke": stroke
        }
        update_patient(ObjectId(pid), update_data)
        flash("Patient updated in MongoDB.", "success")
        return redirect(url_for("mongo_patients.mongo_list_patients"))
    return render_template("mongo_patient_form.html", action="Edit", patient=patient)

@mongo_patients_bp.route("/mongo/patients/<string:pid>/delete", methods=["POST"])
@staff_required
def mongo_delete_patient(pid):
    delete_patient(ObjectId(pid))
    flash("Patient deleted from MongoDB.", "info")
    return redirect(url_for("mongo_patients.mongo_list_patients"))
