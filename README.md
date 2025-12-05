# Stroke Intelligence System (SIS)

A comprehensive web-based healthcare management system for stroke patient data analysis and management, built with Flask and powered by real-world Kaggle stroke prediction dataset.

## 📋 Overview

The Stroke Intelligence System is a secure, role-based web application designed to manage stroke patient records, facilitate healthcare provider workflows, and provide data-driven insights. The system integrates 5,110+ real patient records from the Kaggle Stroke Prediction Dataset and provides specialized dashboards for administrators, doctors, and patients.

## ✨ Features

### 🔐 Role-Based Authentication
- **Admin Dashboard**: User approval workflow, system-wide management, user administration
- **Doctor Dashboard**: Complete patient record access, smoking analysis visualization, patient detail views
- **Patient Dashboard**: Personal health report management, view medical history, track health metrics

### 📊 Data Management
- **5,110+ Patient Records**: Real-world stroke prediction data from Kaggle
- **12 Clinical Attributes**: Age, gender, hypertension, heart disease, glucose levels, BMI, smoking status, stroke history, and more
- **CRUD Operations**: Create, read, update, and delete patient health reports
- **CSV Import/Export**: Automatic dataset loading on first run

### 📈 Visualizations
- **Smoking Analysis Graph**: Interactive Cytoscape.js network visualization showing relationships between smoking status and stroke occurrence
- **Statistical Insights**: Real-time patient statistics and health metrics
- **Responsive Charts**: Chart.js powered data visualizations

### 🛡️ Security Features
- Werkzeug password hashing (scrypt algorithm)
- Session-based authentication
- Role-based access control (RBAC)
- Admin approval workflow for new registrations
- Secure credential validation

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git (for repository cloning)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/CS-LTU/com7033-assignment-ahsanIqbal1122.git
   cd com7033-assignment-ahsanIqbal1122
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   The database will be automatically initialized on first run with the Kaggle dataset.

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   Open your browser and navigate to: `http://127.0.0.1:5000`

## 👥 Test Accounts

The system comes with pre-configured test accounts for immediate testing:

| Role    | Username  | Password   | Access Level                          |
|---------|-----------|------------|---------------------------------------|
| Admin   | admin     | admin123   | Full system access, user approvals    |
| Doctor  | doctor1   | doctor123  | Patient records, analysis tools       |
| Patient | patient1  | patient123 | Personal health reports               |

## 🎯 How to Use

### For Administrators
1. **Login**: Use admin credentials (admin/admin123)
2. **Approve Users**: Navigate to Admin Dashboard → Pending Approvals
3. **Manage Users**: View all registered users, approve/reject registrations
4. **System Overview**: Monitor total patients, doctors, and pending approvals

### For Doctors
1. **Login**: Use doctor credentials (doctor1/doctor123)
2. **View Patients**: Access complete patient database (5,110+ records)
3. **Patient Details**: Click "View" to see individual patient demographics and health metrics
4. **Smoking Analysis**: Navigate to "Smoking Graph" to visualize smoking-stroke relationships
5. **Search & Filter**: Use table search to find specific patients by name, age, or health conditions

### For Patients
1. **Login**: Use patient credentials (patient1/patient123)
2. **Submit Health Reports**: Fill out the health report form with current metrics
3. **View History**: See all previous health reports in chronological order
4. **Edit Reports**: Update existing health records
5. **Track Progress**: Monitor health metric changes over time

### Registration Flow
1. **New User Registration**:
   - Navigate to `/register`
   - Choose role: Doctor or Patient
   - Fill in required information:
     - **Doctors**: License number, department, specialization
     - **Patients**: Medical history, assigned doctor
   - Submit for admin approval
   - Wait for email confirmation (pending feature)
   - Login after approval

## 📁 Project Structure

```
stroke_pass_app/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
│
├── database/
│   ├── __init__.py
│   └── db.py                   # Database initialization & CSV import
│
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py          # Login, registration, logout
│   ├── dashboard_routes.py     # Role-based dashboards
│   └── patient_routes.py       # Patient CRUD operations
│
├── templates/
│   ├── base.html               # Base template with navbar
│   ├── login.html              # Login page
│   ├── register.html           # Registration choice page
│   ├── register_doctor.html    # Doctor registration form
│   ├── register_patient.html   # Patient registration form
│   ├── admin_dashboard.html    # Admin control panel
│   ├── doctor_dashboard.html   # Doctor patient list
│   ├── doctor_view_patient.html# Patient detail view
│   ├── doctor_smoking_graph.html# Smoking analysis visualization
│   ├── patient_dashboard.html  # Patient health reports
│   ├── patient_form.html       # Health report form
│   └── patients.html           # Patient management (admin)
│
└── instance/
    ├── stroke.db               # SQLite database
    └── healthcare-dataset-stroke-data.csv  # Kaggle dataset
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,              -- admin, doctor, patient
    full_name TEXT,
    email TEXT,
    license_number TEXT,             -- doctors only
    department TEXT,                 -- doctors only
    address TEXT,
    mobile TEXT,
    assigned_doctor_id INTEGER,      -- patients only
    approved INTEGER DEFAULT 0,      -- approval status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Patients Table (Kaggle Dataset)
```sql
CREATE TABLE patients (
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
)
```

## 📊 Dataset Information

**Source**: [Kaggle Stroke Prediction Dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)

**Records**: 5,110 patient entries

**Attributes**:
- `id`: Unique patient identifier
- `gender`: Male, Female, or Other
- `age`: Patient age in years
- `hypertension`: 0 (no) or 1 (yes)
- `heart_disease`: 0 (no) or 1 (yes)
- `ever_married`: Yes or No
- `work_type`: Private, Self-employed, Govt_job, children, Never_worked
- `Residence_type`: Urban or Rural
- `avg_glucose_level`: Average glucose level in blood
- `bmi`: Body mass index
- `smoking_status`: formerly smoked, never smoked, smokes, Unknown
- `stroke`: 0 (no stroke) or 1 (stroke occurred)

**Statistics**:
- Total Patients: 5,110
- Stroke Cases: 249 (4.87%)
- Age Range: 0.08 to 82 years
- Gender Distribution: ~59% Female, ~41% Male

## 🛠️ Technologies Used

### Backend
- **Flask 3.1.0**: Python web framework
- **SQLite3**: Embedded relational database
- **Werkzeug**: Password hashing and security utilities
- **Pandas**: CSV data processing and analysis

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **Jinja2**: Template engine
- **Chart.js**: Data visualization library
- **Cytoscape.js**: Network graph visualization
- **FontAwesome**: Icon library

### Development Tools
- **Python 3.14**: Programming language
- **Git**: Version control
- **VS Code**: Development environment

## 🔧 Configuration

Edit `config.py` to customize application settings:

```python
SECRET_KEY = "your-secret-key-here"
DATABASE_PATH = "instance/stroke.db"
CSV_FILE_PATH = "instance/healthcare-dataset-stroke-data.csv"
```

## 📝 API Routes

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout
- `GET /register` - Registration choice page
- `GET/POST /register/doctor` - Doctor registration
- `GET/POST /register/patient` - Patient registration

### Dashboards
- `GET /admin/dashboard` - Admin control panel
- `GET /doctor/dashboard` - Doctor patient list
- `GET /doctor/patient/<id>` - Patient detail view
- `GET /doctor/smoking-graph` - Smoking analysis visualization
- `GET /patient/dashboard` - Patient health reports

### Patient Management
- `GET /patients` - List all patients (admin/doctor)
- `POST /patients/add` - Add new patient report
- `POST /patients/edit/<id>` - Edit patient report
- `POST /patients/delete/<id>` - Delete patient report

## 🐛 Troubleshooting

### Login Issues
- Ensure you're using the correct credentials (username is case-sensitive)
- Check that your account is approved by an administrator
- Clear browser cookies and try again
- Check terminal logs for debug information

### Database Issues
- Delete `instance/stroke.db` and restart the app to recreate the database
- Ensure the CSV file is present in the `instance/` folder
- Check file permissions on the instance directory

### Import Errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher
- Check for conflicting package versions

## 🚧 Future Enhancements

- [ ] Email notifications for account approval
- [ ] Advanced filtering and search in doctor dashboard
- [ ] Machine learning stroke risk prediction
- [ ] PDF export for patient reports
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Real-time notifications
- [ ] Audit logging for all operations
- [ ] Data visualization dashboard for admins
- [ ] Patient appointment scheduling

## 📄 License

This project is developed as part of COM7033 assignment for educational purposes.

## 👨‍💻 Author

**Ahsan Iqbal**  
Student ID: 1122  
Course: COM7033  
Institution: Leeds Trinity University

## 🙏 Acknowledgments

- Kaggle for the Stroke Prediction Dataset
- Flask documentation and community
- Bootstrap team for the UI framework
- Leeds Trinity University for project guidance

## 📧 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact: [Your Email]
- Repository: https://github.com/CS-LTU/com7033-assignment-ahsanIqbal1122

---

**Last Updated**: December 5, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
