# API Documentation

## Authentication Endpoints

### POST /login
Login with username and password.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:** Redirects to dashboard based on role (admin/doctor/patient)

### POST /logout
Logout current user and clear session.

**Response:** Redirects to login page

### POST /register/doctor
Register a new doctor account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string (min 8 chars, uppercase, lowercase, digit, special char)",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "license_number": "string",
  "department": "string",
  "address": "string",
  "mobile": "string"
}
```

**Response:** Redirects to login with success message

### POST /register/patient
Register a new patient account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string (min 8 chars, uppercase, lowercase, digit, special char)",
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "address": "string",
  "mobile": "string",
  "assignedDoctorId": "integer (optional)"
}
```

**Response:** Redirects to login with success message

## Patient Management Endpoints

### GET /patients
List all patients (requires doctor/admin role).

**Response:** HTML page with patient list

### POST /patients
Add a new patient record.

**Request Body:**
```json
{
  "full_name": "string",
  "age": "integer",
  "gender": "0 (Female) | 1 (Male)",
  "hypertension": "0 | 1",
  "heart_disease": "0 | 1",
  "ever_married": "No | Yes",
  "work_type": "string",
  "residence_type": "Rural | Urban",
  "avg_glucose_level": "float",
  "bmi": "float",
  "smoking_status": "string"
}
```

**Response:** Redirects to patients list

### GET /patients/<id>
View specific patient details.

**Response:** HTML page with patient information

### POST /patients/<id>/edit
Update patient information.

**Request Body:** Same as POST /patients

**Response:** Redirects to patient detail page

### POST /patients/<id>/delete
Delete a patient record.

**Response:** Redirects to patients list

## Dashboard Endpoints

### GET /admin/dashboard
Admin dashboard with system overview and user management.

**Requirements:** Admin role

**Response:** HTML page with admin controls

### GET /doctor/dashboard
Doctor dashboard with assigned patients and statistics.

**Requirements:** Doctor role

**Response:** HTML page with patient data

### GET /patient/dashboard
Patient dashboard with personal health records.

**Requirements:** Patient role

**Response:** HTML page with personal data

## Admin Endpoints

### POST /admin/approve-user/<user_id>
Approve a pending user registration.

**Requirements:** Admin role

**Response:** Redirects to admin dashboard

### POST /admin/reject-user/<user_id>
Reject a pending user registration.

**Requirements:** Admin role

**Response:** Redirects to admin dashboard

## MongoDB Endpoints (Alternative Database)

### GET /mongo/patients
List patients from MongoDB.

### POST /mongo/patients
Add patient to MongoDB.

### GET /mongo/patients/<id>
View patient from MongoDB.

### POST /mongo/patients/<id>/edit
Update patient in MongoDB.

### POST /mongo/patients/<id>/delete
Delete patient from MongoDB.

## Security Features

- CSRF protection on all forms
- Password hashing with scrypt (32,768 iterations)
- Strong password requirements (8+ chars, mixed case, digits, special chars)
- Role-based access control
- Session management
- SQL injection prevention with parameterized queries

## Error Responses

- **401 Unauthorized:** User not logged in
- **403 Forbidden:** Insufficient permissions
- **404 Not Found:** Resource doesn't exist
- **500 Internal Server Error:** Server-side error

## Password Requirements

All passwords must contain:
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)
- At least one special character (@$!%*?&#)

---

**Author:** Just Ahsan  
**Course:** COM7033 - Secure Programming  
**Institution:** Leeds Trinity University
