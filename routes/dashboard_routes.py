

from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from functools import wraps
from database.db import get_db
from werkzeug.security import generate_password_hash

dashboard_bp = Blueprint("dashboard", __name__)

def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "role" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))
            if session["role"] != role:
                flash(f"Access denied. This portal is for {role}s only. You are logged in as a {session['role']}.", "danger")
                # Redirect to appropriate dashboard based on user's actual role
                if session["role"] == "admin":
                    return redirect(url_for("dashboard.admin_dashboard"))
                elif session["role"] == "doctor":
                    return redirect(url_for("dashboard.doctor_dashboard"))
                elif session["role"] == "patient":
                    return redirect(url_for("dashboard.patient_dashboard"))
                else:
                    return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

def roles_required(*roles):
    """
    Decorator that allows multiple roles to access a route.
    Usage: @roles_required("patient", "doctor")
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "role" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))
            if session["role"] not in roles:
                flash(f"Access denied. You are logged in as a {session['role']}.", "danger")
                # Redirect to appropriate dashboard based on user's actual role
                if session["role"] == "admin":
                    return redirect(url_for("dashboard.admin_dashboard"))
                elif session["role"] == "doctor":
                    return redirect(url_for("dashboard.doctor_dashboard"))
                elif session["role"] == "patient":
                    return redirect(url_for("dashboard.patient_dashboard"))
                else:
                    return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# -------- PATIENT REPORT EDIT/DELETE --------
@dashboard_bp.route("/patient/reports/<int:report_id>/edit", methods=["GET", "POST"])
@roles_required("patient", "doctor")
def edit_patient_report(report_id):
    user_id = session.get("user_id")
    user_role = session.get("role")
    conn = get_db()
    cur = conn.cursor()
    
    # Patients can only edit their own reports, doctors can edit any report
    if user_role == "patient":
        cur.execute("SELECT * FROM patient_reports WHERE id = ? AND user_id = ?", (report_id, user_id))
    else:  # doctor
        cur.execute("SELECT * FROM patient_reports WHERE id = ?", (report_id,))
    
    report = cur.fetchone()
    if not report:
        conn.close()
        flash("Report not found or access denied.", "danger")
        # Redirect based on user role
        if user_role == "doctor":
            return redirect(url_for("dashboard.doctor_dashboard"))
        return redirect(url_for("dashboard.patient_dashboard"))

    if request.method == "POST":
        try:
            age = float(request.form.get("age") or 0)
        except Exception:
            age = None
        gender = (request.form.get("gender") or None)
        try:
            hypertension = int(request.form.get("hypertension") or 0)
        except Exception:
            hypertension = 0
        ever_married = (request.form.get("ever_married") or None)
        work_type = (request.form.get("work_type") or None)
        residence = (request.form.get("Residence_type") or None)
        try:
            glucose = float(request.form.get("avg_glucose_level") or 0)
        except Exception:
            glucose = None
        try:
            bmi = float(request.form.get("bmi") or 0)
        except Exception:
            bmi = None
        smoking_status = request.form.get("smoking_status") or "unknown"
        try:
            stroke = int(request.form.get("stroke") or 0)
        except Exception:
            stroke = 0

        allowed_genders = {None, '', 'Male', 'Female', 'Other'}
        allowed_ever = {None, '', 'No', 'Yes'}
        allowed_work = {None, '', 'Children', 'Govt_job', 'Never_worked', 'Private', 'Self-employed'}
        allowed_res = {None, '', 'Rural', 'Urban'}
        if gender not in allowed_genders:
            flash('Invalid gender value.', 'danger')
            return redirect(url_for('dashboard.edit_patient_report', report_id=report_id))
        if ever_married not in allowed_ever:
            flash('Invalid ever_married value.', 'danger')
            return redirect(url_for('dashboard.edit_patient_report', report_id=report_id))
        if work_type not in allowed_work:
            flash('Invalid work_type value.', 'danger')
            return redirect(url_for('dashboard.edit_patient_report', report_id=report_id))
        if residence not in allowed_res:
            flash('Invalid Residence_type value.', 'danger')
            return redirect(url_for('dashboard.edit_patient_report', report_id=report_id))
        if age is not None and (age < 0 or age > 120):
            flash('Please enter a valid age.', 'danger')
            return redirect(url_for('dashboard.edit_patient_report', report_id=report_id))
        if glucose is not None and glucose < 0:
            flash('Please enter a valid glucose value.', 'danger')
            return redirect(url_for('dashboard.edit_patient_report', report_id=report_id))
        if bmi is not None and (bmi <= 0 or bmi > 80):
            flash('Please enter a valid BMI value.', 'danger')
            return redirect(url_for('dashboard.edit_patient_report', report_id=report_id))
        if stroke not in (0, 1):
            flash('Invalid stroke value.', 'danger')
            return redirect(url_for('dashboard.edit_patient_report', report_id=report_id))

        # Patients can only update their own reports, doctors can update any
        if user_role == "patient":
            cur.execute(
                """UPDATE patient_reports SET age=?, gender=?, hypertension=?, ever_married=?, work_type=?, Residence_type=?, avg_glucose_level=?, bmi=?, smoking_status=?, stroke=? WHERE id=? AND user_id=?""",
                (age, gender, hypertension, ever_married, work_type, residence, glucose, bmi, smoking_status, stroke, report_id, user_id)
            )
        else:  # doctor
            cur.execute(
                """UPDATE patient_reports SET age=?, gender=?, hypertension=?, ever_married=?, work_type=?, Residence_type=?, avg_glucose_level=?, bmi=?, smoking_status=?, stroke=? WHERE id=?""",
                (age, gender, hypertension, ever_married, work_type, residence, glucose, bmi, smoking_status, stroke, report_id)
            )
        conn.commit()
        conn.close()
        flash("Report updated.", "success")
        # Redirect based on user role
        if user_role == "doctor":
            return redirect(url_for("dashboard.doctor_dashboard"))
        return redirect(url_for("dashboard.patient_dashboard"))

    conn.close()
    # Set cancel URL based on user role
    cancel_url = url_for('dashboard.doctor_dashboard') if user_role == "doctor" else url_for('dashboard.patient_dashboard')
    return render_template("patient_form.html", action="Edit", patient=report, form_action=url_for('dashboard.edit_patient_report', report_id=report_id), cancel_url=cancel_url, show_id=False)


@dashboard_bp.route("/patient/reports/<int:report_id>/delete", methods=["POST"])
@roles_required("patient", "doctor")
def delete_patient_report(report_id):
    user_id = session.get("user_id")
    user_role = session.get("role")
    conn = get_db()
    cur = conn.cursor()
    
    # Patients can only delete their own reports, doctors can delete any report
    if user_role == "patient":
        cur.execute("DELETE FROM patient_reports WHERE id = ? AND user_id = ?", (report_id, user_id))
    else:  # doctor
        cur.execute("DELETE FROM patient_reports WHERE id = ?", (report_id,))
    
    conn.commit()
    conn.close()
    flash("Report deleted.", "info")
    
    # Redirect based on user role
    if user_role == "doctor":
        return redirect(url_for("dashboard.doctor_dashboard"))
    return redirect(url_for("dashboard.patient_dashboard"))

# (Removed duplicate Blueprint and role_required definitions)

# -------- ADMIN DASHBOARD --------
@dashboard_bp.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    conn = get_db()
    cur = conn.cursor()
    # Fetch table info to determine whether created_at column exists (safe for older DBs)
    cur.execute("PRAGMA table_info(users);")
    cols = [r[1] for r in cur.fetchall()]

    if 'created_at' in cols:
        cur.execute("SELECT id, username, full_name, role, email, hospital_id, patient_id, license_number, approved, created_at FROM users ORDER BY created_at DESC")
    else:
        # Fallback for older DBs without created_at
        cur.execute("SELECT id, username, full_name, role, email, hospital_id, patient_id, license_number, approved FROM users ORDER BY id DESC")

    users = cur.fetchall()
    conn.close()
    return render_template("admin_user_management.html", users=users)

@dashboard_bp.route("/admin/users/add", methods=["POST"])
@role_required("admin")
def add_user():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "").strip().lower()
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()

    if not username or not password or not role or not full_name:
        flash("All basic fields are required.", "danger")
        return redirect(url_for("dashboard.admin_dashboard"))

    if role not in ("admin", "doctor", "patient"):
        flash("Invalid role.", "danger")
        return redirect(url_for("dashboard.admin_dashboard"))

    password_hash = generate_password_hash(password)
    conn = get_db()
    cur = conn.cursor()

    # Check username exists
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        conn.close()
        flash("Username already exists.", "danger")
        return redirect(url_for("dashboard.admin_dashboard"))

    try:
        if role == "doctor":
            hospital_id = request.form.get("hospital_id", "").strip()
            license_number = request.form.get("license_number", "").strip()
            if not hospital_id or not license_number:
                conn.close()
                flash("Hospital ID and License Number required for doctors.", "danger")
                return redirect(url_for("dashboard.admin_dashboard"))
            
            cur.execute(
                """INSERT INTO users (username, password_hash, role, full_name, email, hospital_id, license_number, approved)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, password_hash, role, full_name, email, hospital_id, license_number, 1)
            )
        elif role == "patient":
            patient_id = request.form.get("patient_id", "").strip()
            if not patient_id:
                conn.close()
                flash("Patient ID required for patients.", "danger")
                return redirect(url_for("dashboard.admin_dashboard"))
            
            cur.execute(
                """INSERT INTO users (username, password_hash, role, full_name, email, patient_id, approved)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (username, password_hash, role, full_name, email, patient_id, 1)
            )
        else:  # admin
            cur.execute(
                """INSERT INTO users (username, password_hash, role, full_name, email, approved)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (username, password_hash, role, full_name, email, 1)
            )

        conn.commit()
        flash(f"User '{username}' added successfully as {role.capitalize()}.", "success")
    except Exception as e:
        print("Error adding user:", e)
        flash("Failed to add user.", "danger")
    finally:
        conn.close()

    return redirect(url_for("dashboard.admin_dashboard"))


@dashboard_bp.route("/admin/users/<int:user_id>/approve", methods=["POST"])
@role_required("admin")
def approve_user(user_id):
    conn = get_db()
    cur = conn.cursor()

    # Admin may provide patient_id or hospital_id/license_number when approving
    patient_id = request.form.get("patient_id")
    hospital_id = request.form.get("hospital_id")
    license_number = request.form.get("license_number")

    # Build update
    updates = []
    params = []
    updates.append("approved = 1")
    if patient_id:
        updates.append("patient_id = ?")
        params.append(patient_id.strip())
    if hospital_id:
        updates.append("hospital_id = ?")
        params.append(hospital_id.strip())
    if license_number:
        updates.append("license_number = ?")
        params.append(license_number.strip())

    params.append(user_id)
    sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    try:
        cur.execute(sql, tuple(params))
        conn.commit()
        flash("User approved successfully.", "success")
    except Exception as e:
        print("Approve user error:", e)
        flash("Failed to approve user.", "danger")
    finally:
        conn.close()

    return redirect(url_for("dashboard.admin_dashboard"))

@dashboard_bp.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@role_required("admin")
def delete_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    
    # Prevent deleting the current admin user
    if user_id == session.get("user_id"):
        flash("Cannot delete your own account.", "danger")
    else:
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        flash("User deleted successfully.", "success")
    
    conn.close()
    return redirect(url_for("dashboard.admin_dashboard"))

# -------- DOCTOR DASHBOARD --------
@dashboard_bp.route("/doctor/dashboard", methods=["GET", "POST"])
@role_required("doctor")
def doctor_dashboard():
    # Get search query from form or URL parameter
    search_query = request.args.get("search", "").strip()
    
    conn = get_db()
    cur = conn.cursor()
    
    # Fetch patient reports added by patients (linked via users)
    cur.execute("""
        SELECT pr.id, pr.user_id, pr.age, pr.gender, pr.hypertension, pr.ever_married, 
               pr.work_type, pr.Residence_type, pr.avg_glucose_level, pr.bmi, 
               pr.smoking_status, pr.stroke, pr.created_at, u.username, u.full_name
        FROM patient_reports pr
        JOIN users u ON pr.user_id = u.id
        ORDER BY pr.created_at DESC
        LIMIT 50
    """)
    patient_reports = cur.fetchall()
    
    # Search patients by ID if search query provided
    if search_query:
        try:
            search_id = int(search_query)
            cur.execute("SELECT * FROM patients WHERE id = ?;", (search_id,))
            search_results = cur.fetchall()
        except ValueError:
            search_results = []
    else:
        search_results = None
    
    # Show all patients from Kaggle dataset (with limit if no search)
    if search_results is None:
        cur.execute("SELECT * FROM patients ORDER BY id DESC LIMIT 200;")
        all_patients = cur.fetchall()
    else:
        all_patients = search_results if search_results else []
    
    # Count stroke patients for statistics
    cur.execute("SELECT COUNT(*) FROM patients WHERE stroke=1")
    stroke_count = cur.fetchone()[0]
    
    conn.close()
    return render_template("doctor_dashboard.html", 
                         patients=all_patients, 
                         stroke_count=stroke_count,
                         patient_reports=patient_reports,
                         search_query=search_query,
                         is_search=search_results is not None)


# Doctor: view a single patient and any linked user accounts/reports
@dashboard_bp.route("/doctor/patient/<int:pid>")
@role_required("doctor")
def doctor_view_patient(pid):
    conn = get_db()
    cur = conn.cursor()
    # Fetch patient row from patients table
    cur.execute("SELECT * FROM patients WHERE id = ?", (pid,))
    patient = cur.fetchone()
    if not patient:
        conn.close()
        flash("Patient not found.", "danger")
        return redirect(url_for("dashboard.doctor_dashboard"))

    # Find user accounts linked to this patient (users.patient_id)
    cur.execute("SELECT id, username, full_name, email FROM users WHERE patient_id = ?", (pid,))
    users = cur.fetchall()

    # Fetch reports associated with those users (if any)
    reports = []
    if users:
        user_ids = [str(u['id']) for u in users]
        placeholders = ",".join(["?"] * len(user_ids))
        sql = f"SELECT pr.*, u.username FROM patient_reports pr LEFT JOIN users u ON pr.user_id = u.id WHERE pr.user_id IN ({placeholders}) ORDER BY pr.created_at DESC"
        cur.execute(sql, tuple(user_ids))
        reports = cur.fetchall()

    conn.close()
    return render_template("doctor_view_patient.html", patient=patient, users=users, reports=reports)


# Doctor: smoking relational graph of stroke patients
@dashboard_bp.route("/doctor/smoking-graph")
@role_required("doctor")
def doctor_smoking_graph():
    conn = get_db()
    cur = conn.cursor()

    # Fetch all patients with stroke=1
    cur.execute("SELECT id, gender, age, smoking_status, avg_glucose_level, bmi FROM patients WHERE stroke=1 ORDER BY smoking_status")
    stroke_patients = cur.fetchall()
    conn.close()

    # Group by smoking status
    smoking_groups = {}
    for p in stroke_patients:
        status = p['smoking_status'] or 'unknown'
        if status not in smoking_groups:
            smoking_groups[status] = []
        smoking_groups[status].append(p)

    # Build Cytoscape nodes and edges
    nodes = []
    edges = []

    # Central node for "Stroke Patients"
    center_id = "center"
    nodes.append({"data": {"id": center_id, "label": "Stroke Patients"}, "classes": "center"})

    # Create smoking status nodes and connect them
    for status, patients in smoking_groups.items():
        status_node_id = f"smoking_{status}"
        count = len(patients)
        nodes.append({
            "data": {"id": status_node_id, "label": f"{status.capitalize()}\n({count})", "count": count},
            "classes": "smoking-status"
        })
        edges.append({"data": {"source": center_id, "target": status_node_id}})

        # Create patient nodes under each smoking status
        for p in patients[:10]:  # Limit to 10 per status for clarity
            patient_node_id = f"patient_{p['id']}"
            nodes.append({
                "data": {
                    "id": patient_node_id,
                    "label": f"ID {p['id']}",
                    "age": p['age'],
                    "gender": p['gender'],
                    "glucose": p['avg_glucose_level'],
                    "bmi": p['bmi']
                },
                "classes": "patient"
            })
            edges.append({"data": {"source": status_node_id, "target": patient_node_id}})

    # Prepare statistics
    stats = {
        "total_stroke": len(stroke_patients),
        "by_smoking": {status: len(patients) for status, patients in smoking_groups.items()}
    }

    return render_template("doctor_smoking_graph.html", nodes=nodes, edges=edges, stats=stats)

# -------- PATIENT DASHBOARD --------
@dashboard_bp.route("/patient/dashboard", methods=["GET", "POST"])
@role_required("patient")
def patient_dashboard():
    conn = get_db()
    cur = conn.cursor()

    # Ensure patient_reports table exists (create if missing)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patient_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            age REAL,
            gender TEXT,
            hypertension INTEGER,
            ever_married TEXT,
            work_type TEXT,
            Residence_type TEXT,
            avg_glucose_level REAL,
            bmi REAL,
            smoking_status TEXT,
            stroke INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()

    # Perform safe ALTER TABLE to add any missing columns (for existing DBs)
    cur.execute("PRAGMA table_info(patient_reports);")
    existing = {r[1] for r in cur.fetchall()}
    extras = [
        ("gender", "TEXT"),
        ("ever_married", "TEXT"),
        ("work_type", "TEXT"),
        ("Residence_type", "TEXT"),
        ("stroke", "INTEGER DEFAULT 0")
    ]
    for col, col_type in extras:
        if col not in existing:
            try:
                cur.execute(f"ALTER TABLE patient_reports ADD COLUMN {col} {col_type}")
            except Exception:
                pass
    conn.commit()

    user_id = session.get("user_id")

    if request.method == "POST":
        # Collect form data
        try:
            age = float(request.form.get("age") or 0)
        except Exception:
            age = None
        gender = (request.form.get("gender") or None)
        try:
            hypertension = int(request.form.get("hypertension") or 0)
        except Exception:
            hypertension = 0
        ever_married = (request.form.get("ever_married") or None)
        work_type = (request.form.get("work_type") or None)
        residence = (request.form.get("Residence_type") or None)
        try:
            glucose = float(request.form.get("avg_glucose_level") or 0)
        except Exception:
            glucose = None
        try:
            bmi = float(request.form.get("bmi") or 0)
        except Exception:
            bmi = None
        smoking_status = request.form.get("smoking_status") or "unknown"
        try:
            stroke = int(request.form.get("stroke") or 0)
        except Exception:
            stroke = 0

        # Basic server-side validation for provided fields
        allowed_genders = {None, '', 'Male', 'Female', 'Other'}
        allowed_ever = {None, '', 'No', 'Yes'}
        allowed_work = {None, '', 'Children', 'Govt_job', 'Never_worked', 'Private', 'Self-employed'}
        allowed_res = {None, '', 'Rural', 'Urban'}
        if gender not in allowed_genders:
            flash('Invalid gender value.', 'danger')
            return redirect(url_for('dashboard.patient_dashboard'))
        if ever_married not in allowed_ever:
            flash('Invalid ever_married value.', 'danger')
            return redirect(url_for('dashboard.patient_dashboard'))
        if work_type not in allowed_work:
            flash('Invalid work_type value.', 'danger')
            return redirect(url_for('dashboard.patient_dashboard'))
        if residence not in allowed_res:
            flash('Invalid Residence_type value.', 'danger')
            return redirect(url_for('dashboard.patient_dashboard'))
        if age is not None and (age < 0 or age > 120):
            flash('Please enter a valid age.', 'danger')
            return redirect(url_for('dashboard.patient_dashboard'))
        if glucose is not None and glucose < 0:
            flash('Please enter a valid glucose value.', 'danger')
            return redirect(url_for('dashboard.patient_dashboard'))
        if bmi is not None and (bmi <= 0 or bmi > 80):
            flash('Please enter a valid BMI value.', 'danger')
            return redirect(url_for('dashboard.patient_dashboard'))
        if stroke not in (0, 1):
            flash('Invalid stroke value.', 'danger')
            return redirect(url_for('dashboard.patient_dashboard'))

        cur.execute(
            """INSERT INTO patient_reports (user_id, age, gender, hypertension, ever_married, work_type, Residence_type, avg_glucose_level, bmi, smoking_status, stroke)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, age, gender, hypertension, ever_married, work_type, residence, glucose, bmi, smoking_status, stroke)
        )
        conn.commit()
        flash("Report saved.", "success")

    # Fetch recent reports for this user
    cur.execute("SELECT id, age, gender, hypertension, ever_married, work_type, Residence_type, avg_glucose_level, bmi, smoking_status, stroke, created_at FROM patient_reports WHERE user_id = ? ORDER BY created_at DESC LIMIT 50", (user_id,))
    rows = cur.fetchall()

    # Build data for chart: reverse to chronological
    rows_chrono = list(reversed(rows))
    labels = [r['created_at'] for r in rows_chrono]
    def safe_float(val):
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0
    ages = [safe_float(r['age']) for r in rows_chrono]
    glucoses = [safe_float(r['avg_glucose_level']) for r in rows_chrono]
    bmis = [safe_float(r['bmi']) for r in rows_chrono]

    # Compute a simple risk score for visualization (0-100)
    scores = []
    for r in rows_chrono:
        try:
            age_v = safe_float(r['age'] if r['age'] is not None else 0)
            hyp = int(r['hypertension']) if r['hypertension'] is not None else 0
            glu = safe_float(r['avg_glucose_level'] if r['avg_glucose_level'] is not None else 0)
            bmi_v = safe_float(r['bmi'] if r['bmi'] is not None else 0)
        except (KeyError, TypeError, ValueError):
            age_v = 0
            hyp = 0
            glu = 0
            bmi_v = 0
        # Simple heuristic: age, hypertension, glucose, bmi
        score = 0
        score += min(age_v / 100.0, 1.0) * 0.4
        score += (1.0 if hyp == 1 else 0.0) * 0.25
        score += min(glu / 200.0, 1.0) * 0.2
        score += min(bmi_v / 40.0, 1.0) * 0.15
        scores.append(round(score * 100, 1))

    conn.close()
    return render_template("patient_dashboard.html", reports=rows_chrono, labels=labels, ages=ages, glucoses=glucoses, bmis=bmis, scores=scores)
