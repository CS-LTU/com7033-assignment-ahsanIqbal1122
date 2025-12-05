# Git Setup and Commit Instructions

## Prerequisites
You need to install Git for Windows first:
1. Download from: https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart your terminal/PowerShell

## Step-by-Step Commit Guide

### 1. Initialize Git Repository
```bash
cd C:\Users\User\Desktop\stroke_pass_app
git init
```

### 2. Configure Git (if first time)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Add Remote Repository
```bash
git remote add origin https://github.com/CS-LTU/com7033-assignment-ahsanIqbal1122.git
```

### 4. Stage All Files
```bash
git add .
```

### 5. Commit with Descriptive Message
```bash
git commit -m "Initial commit: Complete Stroke Intelligence System (SIS) implementation

Features:
- Role-based authentication (Admin, Doctor, Patient) with Werkzeug password hashing
- Integrated 5,110+ patient records from Kaggle Stroke Prediction Dataset
- Admin dashboard with user approval workflow and system management
- Doctor dashboard with full patient record access and smoking analysis visualization
- Patient dashboard for personal health report management
- Interactive Cytoscape.js network graph for smoking-stroke relationship analysis
- CRUD operations for patient health reports with secure session management
- SQLite database with automatic CSV import on first run
- Responsive Bootstrap 5 UI with Chart.js visualizations
- Comprehensive README with installation guide, usage instructions, and API documentation
- Test accounts pre-configured for immediate system testing

Technical Stack:
- Backend: Flask 3.1.0, SQLite3, Pandas, Werkzeug security
- Frontend: Bootstrap 5, Jinja2, Chart.js, Cytoscape.js
- Security: Session-based auth, role-based access control, password hashing
- Dataset: Real-world Kaggle stroke prediction data (12 clinical attributes)

Database Schema:
- Users table with role-based access (admin/doctor/patient)
- Patients table with 12 Kaggle dataset attributes
- Automated approval workflow for new registrations

Routes Implemented:
- Authentication: /login, /logout, /register (doctor/patient flows)
- Dashboards: /admin/dashboard, /doctor/dashboard, /patient/dashboard
- Patient Management: /patients (list/add/edit/delete)
- Visualizations: /doctor/smoking-graph, /doctor/patient/<id>

Documentation:
- Comprehensive README.md with setup instructions
- Test credentials provided for all user roles
- API route documentation included
- Troubleshooting guide for common issues
- Project structure overview with file descriptions

Status: Production-ready with debug logging enabled for troubleshooting"
```

### 6. Check Branch Name
```bash
git branch
```

If you're on `master` but the remote uses `main`, rename it:
```bash
git branch -M main
```

### 7. Push to GitHub
```bash
git push -u origin main
```

If the repository already exists and you need to force push (be careful!):
```bash
git push -u origin main --force
```

### 8. Verify on GitHub
Open your browser and go to:
https://github.com/CS-LTU/com7033-assignment-ahsanIqbal1122

You should see all your files committed with the detailed description.

---

## Quick Reference: Future Commits

After making changes, use these commands:

```bash
# Check what changed
git status

# Stage all changes
git add .

# Commit with message
git commit -m "Description of your changes"

# Push to GitHub
git push origin main
```

## Common Issues

### Authentication Required
If GitHub asks for credentials, you may need to:
1. Generate a Personal Access Token (PAT) at: https://github.com/settings/tokens
2. Use the PAT as your password when pushing

### Permission Denied
Make sure you have write access to the repository.

### Merge Conflicts
If files exist on GitHub already:
```bash
git pull origin main --rebase
git push origin main
```

---

**Note**: The `.gitignore` file has been created to exclude:
- Database files (stroke.db)
- Python cache files (__pycache__)
- Virtual environment folders
- IDE configuration files
- Log files
- Debug/test scripts (optional)

The Kaggle CSV dataset file is included in the repository for easy setup.
