from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from functools import wraps
from database.db import get_db

patients_bp = Blueprint("patients", __name__)



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


@patients_bp.route("/")
def home_redirect():
    # Show home page if not logged in; redirect to dashboard if logged in
    if "user_id" in session:
        if session.get("role") == "admin":
            return redirect(url_for("dashboard.admin_dashboard"))
        elif session.get("role") == "doctor":
            return redirect(url_for("dashboard.doctor_dashboard"))
        else:
            return redirect(url_for("dashboard.patient_dashboard"))
    return render_template("home.html")


@patients_bp.route("/about")
def about():
    return render_template("about.html")


@patients_bp.route("/contact")
def contact():
    return render_template("contact.html")


@patients_bp.route("/patients")
@staff_required
def list_patients():
    conn = get_db()
    cur = conn.cursor()
    # Show all patients from Kaggle dataset (no limit for doctors)
    cur.execute("SELECT * FROM patients ORDER BY id DESC;")
    data = cur.fetchall()
    
    # Get total count
    cur.execute("SELECT COUNT(*) FROM patients")
    total_count = cur.fetchone()[0]
    
    conn.close()
    return render_template("patients.html", patients=data, total_count=total_count)


@patients_bp.route("/patients/add", methods=["GET", "POST"])
@staff_required
def add_patient():
    if request.method == "POST":
        try:
            pid = int(request.form["id"])
            age = float(request.form["age"])
            hypertension = int(request.form["hypertension"])
            glucose = float(request.form["avg_glucose_level"])
            bmi = float(request.form["bmi"])
            stroke = int(request.form["stroke"])
        except:
            flash("Invalid numeric values", "danger")
            return redirect(url_for("patients.add_patient"))

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pid,
                request.form["gender"],
                age,
                hypertension,
                request.form["ever_married"],
                request.form["work_type"],
                request.form["Residence_type"],
                glucose,
                bmi,
                request.form["smoking_status"],
                stroke
            ))
            conn.commit()
            flash("Patient added.", "success")
        except:
            flash("Patient ID already exists.", "danger")

        conn.close()
        return redirect(url_for("patients.list_patients"))

    return render_template("patient_form.html", action="Add")


@patients_bp.route("/patients/<int:pid>/edit", methods=["GET", "POST"])
@staff_required
def edit_patient(pid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (pid,))
    patient = cur.fetchone()

    if not patient:
        flash("Patient not found", "danger")
        return redirect(url_for("patients.list_patients"))

    if request.method == "POST":
        try:
            age = float(request.form["age"])
            hypertension = int(request.form["hypertension"])
            glucose = float(request.form["avg_glucose_level"])
            bmi = float(request.form["bmi"])
            stroke = int(request.form["stroke"])
        except:
            flash("Invalid numeric values.", "danger")
            return redirect(url_for("patients.edit_patient", pid=pid))

        cur.execute("""
            UPDATE patients SET
                gender=?, age=?, hypertension=?, ever_married=?,
                work_type=?, Residence_type=?, avg_glucose_level=?,
                bmi=?, smoking_status=?, stroke=?
            WHERE id=?
        """, (
            request.form["gender"], age, hypertension,
            request.form["ever_married"], request.form["work_type"],
            request.form["Residence_type"], glucose, bmi,
            request.form["smoking_status"], stroke, pid
        ))
        conn.commit()
        conn.close()
        flash("Patient updated.", "success")
        return redirect(url_for("patients.list_patients"))

    conn.close()
    return render_template("patient_form.html", action="Edit", patient=patient)


@patients_bp.route("/patients/<int:pid>/delete", methods=["POST"])
@staff_required
def delete_patient(pid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    flash("Patient deleted.", "info")
    return redirect(url_for("patients.list_patients"))
