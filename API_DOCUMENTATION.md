# API Documentation - Stroke Pass Application

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Endpoints Reference](#endpoints-reference)
- [Request/Response Examples](#requestresponse-examples)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Security Considerations](#security-considerations)

## Overview

The Stroke Pass application provides a RESTful-style web interface for managing stroke patient data with role-based access control. The API follows RESTful conventions with HTML form submissions and server-side rendering.

### Base URL
```
http://localhost:5000
```

### Authentication Method
- Session-based authentication with HTTP-only cookies
- CSRF protection on all state-changing operations

### Supported Formats
- HTML (server-rendered templates)
- Form data (application/x-www-form-urlencoded)

---

## Authentication

### Session Management

Authentication is managed through server-side sessions with encrypted cookies.

**Session Cookie Attributes:**
- `HttpOnly`: Yes (prevents JavaScript access)
- `Secure`: Yes (HTTPS only in production)
- `SameSite`: Lax (CSRF protection)
- `Lifetime`: 3600 seconds (1 hour default)

**Session Data:**
```python
{
    'user_id': int,      # User's unique identifier
    'username': str,     # User's username
    'role': str          # 'admin', 'doctor', or 'patient'
}
```

---

## Endpoints Reference

### 1. Authentication Endpoints

#### `POST /login`
Authenticate user and create session.

**Access:** Public  
**CSRF:** Required  
**Rate Limit:** 5 per minute

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | User's username |
| `password` | string | Yes | User's password |
| `csrf_token` | string | Yes | CSRF protection token |

**Success Response:**
- **Code:** 302 (Redirect)
- **Location:** Role-based dashboard
  - Admin → `/admin_dashboard`
  - Doctor → `/doctor_dashboard`
  - Patient → `/patient_dashboard`

**Error Responses:**
- **Code:** 401 (Unauthorized)
  - Invalid credentials
  - Account not approved
- **Code:** 400 (Bad Request)
  - Missing required fields
  - Invalid CSRF token

---

#### `POST /register_patient`
Register a new patient account.

**Access:** Public  
**CSRF:** Required  
**Rate Limit:** 3 per hour

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Unique username (min 3 chars) |
| `password` | string | Yes | Password (min 6 chars) |
| `email` | string | Yes | Valid email address |
| `first_name` | string | Yes | Patient's first name |
| `last_name` | string | Yes | Patient's last name |
| `address` | string | No | Home address |
| `mobile` | string | No | Phone number |
| `assignedDoctorId` | int | No | Assigned doctor's user ID |
| `csrf_token` | string | Yes | CSRF token |

**Success Response:**
- **Code:** 302 (Redirect)
- **Location:** `/login`
- **Message:** "Registration successful. Wait for approval."

**Error Responses:**
- **Code:** 400 (Bad Request)
  - Username already exists
  - Password too short
  - Invalid email format

---

#### `POST /register_doctor`
Register a new doctor account.

**Access:** Public  
**CSRF:** Required  
**Rate Limit:** 3 per hour

**Form Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Unique username |
| `password` | string | Yes | Password |
| `email` | string | Yes | Email address |
| `first_name` | string | Yes | Doctor's first name |
| `last_name` | string | Yes | Doctor's last name |
| `department` | string | No | Medical department |
| `license_number` | string | Yes | Medical license number |
| `address` | string | No | Office address |
| `mobile` | string | No | Contact number |
| `csrf_token` | string | Yes | CSRF token |

---

#### `GET /logout`
Terminate user session.

**Access:** Authenticated users  
**CSRF:** Not required (GET request)

**Success Response:**
- **Code:** 302 (Redirect)
- **Location:** `/login`
- **Action:** Session cleared

---

### 2. Admin Endpoints

#### `GET /admin_dashboard`
View admin dashboard with pending approvals.

**Access:** Admin only  
**Authorization:** `role == 'admin'`

**Response Data:**
```python
{
    'pending_doctors': List[User],   # Doctors awaiting approval
    'pending_patients': List[User],  # Patients awaiting approval
    'all_users': List[User]          # All registered users
}
```

---

#### `POST /approve_doctor/<int:user_id>`
Approve a pending doctor account.

**Access:** Admin only  
**CSRF:** Required  
**Parameters:**
- `user_id` (path): User ID to approve

**Success Response:**
- **Code:** 302 (Redirect)
- **Location:** `/admin_dashboard`

---

#### `POST /approve_patient/<int:user_id>`
Approve a pending patient account.

**Access:** Admin only  
**CSRF:** Required  
**Parameters:**
- `user_id` (path): User ID to approve

---

### 3. Doctor Endpoints

#### `GET /doctor_dashboard`
View doctor dashboard with patient summary.

**Access:** Doctor only  
**Authorization:** `role == 'doctor'`

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search` | string | No | Search patients by name/ID |

**Response Data:**
```python
{
    'total_patients': int,
    'high_risk_count': int,
    'recent_reports': List[PatientReport],
    'search_results': List[PatientReport]  # If search provided
}
```

---

#### `GET /patient/<int:patient_id>`
View detailed patient report.

**Access:** Doctor only  
**Authorization:** `role == 'doctor'`  
**Parameters:**
- `patient_id` (path): Patient report ID

**Response Data:**
```python
{
    'id': int,
    'user_id': int,
    'age': float,
    'gender': str,
    'hypertension': int,
    'heart_disease': int,
    'ever_married': str,
    'work_type': str,
    'residence_type': str,
    'avg_glucose_level': float,
    'bmi': float,
    'smoking_status': str,
    'stroke': int,
    'risk_score': float,  # Calculated
    'risk_level': str     # Low/Medium/High
}
```

---

### 4. Patient Endpoints

#### `GET /patient_dashboard`
View patient's own dashboard and reports.

**Access:** Patient only  
**Authorization:** `role == 'patient'`

**Response Data:**
```python
{
    'user': User,
    'reports': List[PatientReport],
    'report_count': int,
    'latest_report': PatientReport
}
```

---

#### `POST /patient/add_report`
Create a new patient report.

**Access:** Patient only  
**CSRF:** Required  
**Authorization:** User can only create reports for themselves

**Form Parameters:**
| Parameter | Type | Required | Range/Values |
|-----------|------|----------|--------------|
| `age` | float | Yes | 0-150 |
| `gender` | string | Yes | Male, Female, Other |
| `hypertension` | int | Yes | 0 or 1 |
| `heart_disease` | int | Yes | 0 or 1 |
| `ever_married` | string | Yes | Yes, No |
| `work_type` | string | Yes | Private, Self-employed, Govt_job, children, Never_worked |
| `residence_type` | string | Yes | Urban, Rural |
| `avg_glucose_level` | float | Yes | 0-500 |
| `bmi` | float | Yes | 0-100 |
| `smoking_status` | string | Yes | formerly smoked, never smoked, smokes, Unknown |
| `stroke` | int | Yes | 0 or 1 |
| `csrf_token` | string | Yes | CSRF token |

**Success Response:**
- **Code:** 302 (Redirect)
- **Location:** `/patient_dashboard`

**Validation:**
- All numeric fields validated for range
- Enum fields validated against allowed values
- Foreign key constraint on `user_id`

---

#### `POST /patient/edit_report/<int:report_id>`
Update existing patient report.

**Access:** Patient only  
**CSRF:** Required  
**Authorization:** User can only edit their own reports  
**Parameters:**
- `report_id` (path): Report ID to update

**Form Parameters:** Same as `add_report`

---

#### `POST /patient/delete_report/<int:report_id>`
Delete a patient report.

**Access:** Patient only  
**CSRF:** Required  
**Authorization:** User can only delete their own reports  
**Parameters:**
- `report_id` (path): Report ID to delete

**Success Response:**
- **Code:** 302 (Redirect)
- **Location:** `/patient_dashboard`

---

### 5. MongoDB Patient Endpoints

#### `POST /mongo/add_patient`
Add patient record to MongoDB.

**Access:** Authenticated users  
**CSRF:** Required

**Form Parameters:** Same as SQLite patient report

**Response:**
- Stores flexible schema in MongoDB
- Returns ObjectId as string

---

## Request/Response Examples

### Example 1: User Login

**Request:**
```http
POST /login HTTP/1.1
Host: localhost:5000
Content-Type: application/x-www-form-urlencoded

username=john_doe&password=SecurePass123&csrf_token=abc123xyz
```

**Success Response:**
```http
HTTP/1.1 302 Found
Location: /patient_dashboard
Set-Cookie: session=...; HttpOnly; SameSite=Lax
```

**Error Response:**
```http
HTTP/1.1 401 Unauthorized
Content-Type: text/html

<div class="alert alert-danger">Invalid username or password</div>
```

---

### Example 2: Create Patient Report

**Request:**
```http
POST /patient/add_report HTTP/1.1
Host: localhost:5000
Content-Type: application/x-www-form-urlencoded
Cookie: session=...

age=55&gender=Male&hypertension=1&heart_disease=0&ever_married=Yes&work_type=Private&residence_type=Urban&avg_glucose_level=180.5&bmi=28.3&smoking_status=formerly+smoked&stroke=0&csrf_token=xyz789
```

**Success Response:**
```http
HTTP/1.1 302 Found
Location: /patient_dashboard
```

---

### Example 3: Doctor Search Patients

**Request:**
```http
GET /doctor_dashboard?search=john HTTP/1.1
Host: localhost:5000
Cookie: session=...
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/html

<table class="table">
  <tr>
    <td>123</td>
    <td>john_doe</td>
    <td>55</td>
    <td>Male</td>
    <td class="text-danger">High Risk (75.2)</td>
  </tr>
</table>
```

---

## Error Handling

### Error Response Format

All errors return appropriate HTTP status codes with user-friendly messages in HTML format.

**Common Status Codes:**
| Code | Meaning | Description |
|------|---------|-------------|
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

**Error Message Structure:**
```html
<div class="alert alert-{type}">
    {error_message}
</div>
```

---

## Rate Limiting

Rate limiting protects against abuse and brute-force attacks.

### Rate Limit Configuration

| Endpoint | Limit | Window | Reason |
|----------|-------|--------|--------|
| `/login` | 5 requests | per minute | Prevent brute force |
| `/register_*` | 3 requests | per hour | Prevent spam accounts |
| `/patient/add_report` | 10 requests | per hour | Prevent data spam |
| Default | 100 requests | per hour | General protection |

### Rate Limit Headers

```http
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1638360000
```

### Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60

<div class="alert alert-warning">
    Too many requests. Please try again in 60 seconds.
</div>
```

---

## Security Considerations

### 1. CSRF Protection

All state-changing operations (POST, PUT, DELETE) require CSRF tokens.

**Implementation:**
```html
<form method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <!-- form fields -->
</form>
```

**Validation:**
- Token validated on every POST request
- Token expires after 1 hour
- Missing/invalid token returns 400 Bad Request

---

### 2. SQL Injection Prevention

All database queries use parameterized statements.

**Example:**
```python
# ✅ Safe (parameterized)
cur.execute("SELECT * FROM users WHERE username = ?", (username,))

# ❌ Unsafe (never used)
# cur.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

---

### 3. Password Security

**Hashing Algorithm:** Scrypt  
**Iterations:** 32,768  
**Salt:** Automatic (unique per password)

**Storage:**
```python
# Password never stored as plain text
password_hash = generate_password_hash(password, method='scrypt')
```

---

### 4. Session Security

**Configuration:**
- `HttpOnly`: Prevents JavaScript access
- `Secure`: HTTPS only in production
- `SameSite=Lax`: CSRF protection
- Automatic expiration after 1 hour

---

### 5. Authorization Checks

Every protected endpoint verifies:
1. User is authenticated (session exists)
2. User has required role (admin/doctor/patient)
3. User owns the data being accessed (ownership verification)

**Example:**
```python
@login_required
def patient_dashboard():
    if session['role'] != 'patient':
        return redirect('/login')
    # Show only user's own data
    reports = get_reports_for_user(session['user_id'])
```

---

### 6. Input Validation

All inputs validated on server-side:
- Type checking (int, float, string)
- Range validation (age 0-150, BMI 0-100)
- Enum validation (gender, work_type, etc.)
- Length limits (username, password)

**Validation Layers:**
1. HTML5 form validation (client-side)
2. Type conversion (server-side)
3. Range checking (server-side)
4. Database constraints (database-side)

---

## API Design Rationale

### Why Session-Based Authentication?

1. **Simplicity:** No token management for HTML applications
2. **Security:** HTTP-only cookies prevent XSS attacks
3. **Compatibility:** Works with server-side rendering
4. **CSRF Protection:** Built-in with Flask-WTF

### Why Server-Side Rendering?

1. **Performance:** Faster initial page load
2. **SEO:** Better search engine optimization
3. **Accessibility:** Works without JavaScript
4. **Security:** Reduced attack surface

### Why Dual Database Architecture?

1. **SQLite:** 
   - ACID transactions for user authentication
   - Relational integrity for reports
   - Simple deployment (no external database)

2. **MongoDB:**
   - Flexible schema for varying patient data
   - Horizontal scalability
   - JSON-like documents for complex structures

---

## Future API Enhancements

Planned improvements for future versions:

1. **RESTful JSON API:**
   - `/api/v1/patients` (GET, POST, PUT, DELETE)
   - JSON request/response format
   - JWT authentication

2. **WebSocket Support:**
   - Real-time notifications
   - Live dashboard updates

3. **GraphQL API:**
   - Flexible data querying
   - Reduced over-fetching

4. **API Versioning:**
   - `/api/v1/`, `/api/v2/`
   - Backward compatibility

5. **OAuth2 Integration:**
   - Google/GitHub login
   - Third-party app authorization

---

**Last Updated:** December 9, 2025  
**API Version:** 1.0.0  
**Author:** Ahsan Iqbal
