from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from functools import wraps
from bson.objectid import ObjectId
from database.mongo import add_patient, get_patient, update_patient, delete_patient, list_patients

mongo_patients_bp = Blueprint("mongo_patients", __name__)

# Only allow admin/doctor to access global patient CRUD
def staff_required(f):
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
