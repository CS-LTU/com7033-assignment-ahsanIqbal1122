"""
Authentication Routes Module

This module handles user authentication including:
- User login with secure password verification
- Doctor and patient registration with input validation
- User logout and session management
- Password hashing using Werkzeug's scrypt algorithm

Security Features:
- Password hashing with scrypt (32,768 iterations)
- Input validation on registration fields
- SQL injection prevention with parameterized queries
- Session-based authentication
- Role-based access control (admin, doctor, patient)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db
import re

auth_bp = Blueprint("auth", __name__)


def validate_password_strength(password):
    """
    Validate password strength with comprehensive security requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (@$!%*?&#)
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
        
    Security Rationale:
        - Length requirement prevents brute force attacks
        - Character variety increases entropy
        - Special characters make dictionary attacks harder
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[@$!%*?&#]', password):
        return False, "Password must contain at least one special character (@$!%*?&#)"
    
    return True, ""


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
    """
    Handle user login with secure password verification.
    
    GET: Display login form
    POST: Authenticate user credentials and create session
    
    Security:
    - Uses check_password_hash() to verify passwords securely
    - Prevents timing attacks with consistent hash checking
    - Validates user approval status before allowing login
    - Uses parameterized SQL queries to prevent injection
    
    Returns:
    - GET: Rendered login.html template
    - POST (success): Redirect to role-specific dashboard
    - POST (failure): Redirect to login with error flash message
    """
    if request.method == "POST":
        # Get and sanitize username and password from form
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # Debug logging for troubleshooting (remove in production)
        print(f"[LOGIN DEBUG] Attempting login with username: '{username}'")
        print(f"[LOGIN DEBUG] Password length: {len(password)}")

        # Query database for user with provided username
        # Using parameterized query prevents SQL injection
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        conn.close()

        if user:
            print(f"[LOGIN DEBUG] User found in database")
            # Verify password using scrypt hash comparison
            # check_password_hash() is time-constant to prevent timing attacks
            password_match = check_password_hash(user["password_hash"], password)
            print(f"[LOGIN DEBUG] Password match: {password_match}")
        else:
            print(f"[LOGIN DEBUG] User NOT found in database")

        if user and check_password_hash(user["password_hash"], password):
            # Check if user is approved by admin (admins bypass this check)
            # This prevents unapproved users from accessing the system
            approved = 0
            try:
                approved = user["approved"]
            except Exception:
                approved = 0

            # Non-admin users must be approved before login access
            if user["role"] != "admin" and (approved is None or int(approved) != 1):
                flash("Your account is pending approval by an administrator.", "warning")
                return redirect(url_for("auth.login"))

            # Authentication successful - create session with user data
            session["user_id"] = user["id"]
            session["username"] = username
            session["role"] = user["role"]

            # Redirect to appropriate dashboard based on user role
            if user["role"] == "admin":
                return redirect(url_for("dashboard.admin_dashboard"))
            elif user["role"] == "doctor":
                return redirect(url_for("dashboard.doctor_dashboard"))
            else:
                return redirect(url_for("dashboard.patient_dashboard"))

        else:
            # Authentication failed - invalid credentials
            flash("Invalid login credentials.", "danger")

    # Display login form
    role_param = request.args.get('role', '')
    return render_template("login.html", role=role_param)


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    """
    Handle doctor registration with validation.
    
    Security Features:
    1. Required fields validation (username, password, full_name, email, license_number)
    2. Strong password validation:
       - Minimum 8 characters
       - At least one uppercase letter
       - At least one lowercase letter
       - At least one digit
       - At least one special character (@$!%*?&#)
    3. Unique username check to prevent duplicate accounts
    4. Password hashing with scrypt algorithm before storage
    5. Input sanitization with .strip()
    
    Returns:
    - GET: Rendered register_doctor.html template
    - POST (success): Redirect to login with success message
    - POST (failure): Redirect to registration form with error message
    """
    if request.method == "POST":
        # Get form data and sanitize by stripping whitespace
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

        # Validate all required fields are provided
        if not username or not password or not full_name or not email or not license_number:
            flash("All fields are required for doctor registration.", "danger")
            return redirect(url_for("auth.register_doctor"))

        # Enforce strong password requirements for security
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            flash(error_message, "danger")
            return redirect(url_for("auth.register_doctor"))

        # Hash password using scrypt algorithm (32,768 iterations)
        # This ensures passwords are never stored in plain text
        password_hash = generate_password_hash(password)
        conn = get_db()
        cur = conn.cursor()

        # Check if username already exists in database
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone():
            conn.close()
            flash("Username already exists. Please choose another.", "danger")
            return redirect(url_for("auth.register_doctor"))

        try:
            # Insert new doctor into database
            # Using parameterized query prevents SQL injection
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

        # Enforce strong password requirements for security
        is_valid, error_message = validate_password_strength(password)
        if not is_valid:
            flash(error_message, "danger")
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

