from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET"])
def register():
    """Show registration choice page. Separate patient and doctor registration handled on their own routes."""
    # If user already logged in, send them to their dashboard
    if session.get("role"):
        role = session.get("role")
        if role == "admin":
            return redirect(url_for("dashboard.admin_dashboard"))
        elif role == "doctor":
            return redirect(url_for("dashboard.doctor_dashboard"))
        else:
            return redirect(url_for("dashboard.patient_dashboard"))

    # Optional query param to jump directly to a role-specific registration page
    role_q = (request.args.get("role") or "").strip().lower()
    if role_q == "doctor":
        return redirect(url_for("auth.register_doctor"))
    if role_q == "patient":
        return redirect(url_for("auth.register_patient"))

    return render_template("register_choice.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Debug logging
        print(f"[LOGIN DEBUG] Attempting login with username: '{username}'")
        print(f"[LOGIN DEBUG] Password length: {len(password)}")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user:
            print(f"[LOGIN DEBUG] User found in database")
            password_match = check_password_hash(user["password_hash"], password)
            print(f"[LOGIN DEBUG] Password match: {password_match}")
        else:
            print(f"[LOGIN DEBUG] User NOT found in database")

        if user and check_password_hash(user["password_hash"], password):
            # Block login until approved by admin (admins are allowed)
            approved = 0
            try:
                approved = user["approved"]
            except Exception:
                approved = 0

            if user["role"] != "admin" and (approved is None or int(approved) != 1):
                flash("Your account is pending approval by an administrator.", "warning")
                return redirect(url_for("auth.login"))

            session["user_id"] = user["id"]
            session["username"] = username
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))
            elif user["role"] == "doctor":
                return redirect(url_for("dashboard.doctor_dashboard"))
            else:
                return redirect(url_for("dashboard.patient_dashboard"))

        else:
            flash("Invalid login credentials.", "danger")

    # Pass role parameter to login template if it's admin trying to login
    role_param = request.args.get('role', '')
    return render_template("login.html", role=role_param)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = "doctor"
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        full_name = (first_name + " " + last_name).strip() if (first_name or last_name) else request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        license_number = request.form.get("license_number", "").strip()
        department = request.form.get("department", "").strip()
        address = request.form.get("address", "").strip()
        mobile = request.form.get("mobile", "").strip()

        # Basic validation
        if not username or not password or not full_name or not email or not license_number:
            flash("All fields are required for doctor registration.", "danger")
            return redirect(url_for("auth.register_doctor"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("auth.register_doctor"))

        password_hash = generate_password_hash(password)
        conn = get_db()
        cur = conn.cursor()

        # Check if username already exists
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            conn.close()
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for("auth.register_doctor"))

        try:
            cur.execute(
                """INSERT INTO users (username, password_hash, role, full_name, email, license_number, department, address, mobile, approved) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, password_hash, role, full_name, email, license_number, department, address, mobile, 0)
            )
            conn.commit()
            flash("Doctor registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            print("Doctor registration error:", e)
            flash("Registration failed. Please try again.", "danger")
        finally:
            conn.close()

    return render_template("register_doctor.html")


@auth_bp.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = "patient"
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        full_name = (first_name + " " + last_name).strip() if (first_name or last_name) else request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        # patient_id will be assigned by admin upon approval
        address = request.form.get("address", "").strip()
        mobile = request.form.get("mobile", "").strip()
        assigned_doctor_id = request.form.get("assignedDoctorId") or request.form.get("assigned_doctor_id")
        if assigned_doctor_id:
            try:
                assigned_doctor_id = int(assigned_doctor_id)
            except Exception:
                assigned_doctor_id = None

        # Basic validation
        if not username or not password or not full_name or not email:
            flash("All fields are required for patient registration.", "danger")
            return redirect(url_for("auth.register_patient"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("auth.register_patient"))

        password_hash = generate_password_hash(password)
        conn = get_db()
        cur = conn.cursor()

        # Check if username already exists
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            conn.close()
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for("auth.register_patient"))

        try:
            cur.execute(
                """INSERT INTO users (username, password_hash, role, full_name, email, address, mobile, assigned_doctor_id, approved) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (username, password_hash, role, full_name, email, address, mobile, assigned_doctor_id, 0)
            )
            conn.commit()
            flash("Patient registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception as e:
            print("Patient registration error:", e)
            flash("Registration failed. Please try again.", "danger")
        finally:
            conn.close()

    # GET: provide doctor list for assignment
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, full_name, hospital_id FROM users WHERE role = 'doctor' ORDER BY full_name ASC")
    doctors = cur.fetchall()
    conn.close()
    return render_template("register_patient.html", doctors=doctors)

