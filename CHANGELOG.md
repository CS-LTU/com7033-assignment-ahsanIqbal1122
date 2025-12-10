# Changelog

All notable changes to the Stroke Intelligence System (SIS) will be documented in this file.

## [1.0.0] - 2025-12-05

### Initial Release - Complete Implementation

#### Added
- **Authentication System**
  - Role-based login and logout functionality
  - Secure password hashing using Werkzeug scrypt algorithm
  - Session-based authentication and authorization
  - Registration flows for doctors and patients
  - Admin approval workflow for new user accounts

- **Role-Based Dashboards**
  - Admin Dashboard: User management, approval workflow, system statistics
  - Doctor Dashboard: Patient list, patient detail views, analysis tools
  - Patient Dashboard: Personal health report management and history

- **Patient Management**
  - CRUD operations for patient health reports
  - View detailed patient demographics and health metrics
  - Search and filter patient records
  - Assign patients to doctors

- **Data Management**
  - Integration of Kaggle Stroke Prediction Dataset (5,110 records)
  - Automatic CSV import on first application run
  - 12 clinical attributes per patient record
  - SQLite3 database with relational schema

- **Visualizations**
  - Interactive Cytoscape.js network graph for smoking analysis
  - Chart.js data visualizations
  - Smoking status and stroke outcome relationships
  - Statistical insights and metrics

- **User Interface**
  - Responsive Bootstrap 5 design
  - Mobile-friendly layouts
  - Interactive forms with validation
  - Flash messages for user feedback
  - Jinja2 template engine

- **Database Features**
  - Automatic database initialization
  - CSV dataset import functionality
  - Proper schema with user and patient tables
  - Fallback Kaggle API dataset download
  - Database transactions and error handling

- **Security Features**
  - Password hashing with scrypt (32768 iterations)
  - Session management with secure cookies
  - User approval system before login access
  - Role-based access control (RBAC)
  - Input validation and sanitization

- **Documentation**
  - Comprehensive README with setup instructions
  - API route documentation
  - Database schema documentation
  - Troubleshooting guide
  - Usage instructions for all user roles
  - Git setup and commit instructions

- **Development Tools**
  - Debug logging in authentication routes
  - Test account creation scripts
  - Database verification utilities
  - Configuration management

#### Technical Details
- **Backend Framework**: Flask 3.1.0
- **Database**: SQLite3 with 2 tables (users, patients)
- **Frontend Framework**: Bootstrap 5
- **Visualization Libraries**: Chart.js, Cytoscape.js
- **Security**: Werkzeug password hashing, Session-based auth
- **Data Processing**: Pandas CSV import/export
- **Template Engine**: Jinja2
- **Python Version**: 3.8+

#### Files Included
- `app.py` - Main Flask application
- `config.py` - Configuration settings
- `version.py` - Version information
- `requirements.txt` - Python dependencies
- `README.md` - Comprehensive documentation
- `CHANGELOG.md` - This file
- `GIT_INSTRUCTIONS.md` - Git setup guide
- `.gitignore` - Git ignore rules
- `database/db.py` - Database operations
- `routes/auth_routes.py` - Authentication routes
- `routes/dashboard_routes.py` - Dashboard routes
- `routes/patient_routes.py` - Patient CRUD routes
- `templates/` - HTML templates (11 files)

#### Test Accounts
- **Admin**: username: `admin`, password: `admin123`
- **Doctor**: username: `doctor1`, password: `doctor123`
- **Patient**: username: `patient1`, password: `patient123`

#### Dataset Information
- **Source**: Kaggle Stroke Prediction Dataset
- **Total Records**: 5,110 patients
- **Attributes**: 12 clinical fields
- **Stroke Cases**: 249 (4.87%)
- **Automatically Loaded**: Yes, on first run

#### Installation & Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run application: `python app.py`
3. Access at: `http://127.0.0.1:5000`
4. Login with test credentials
5. Explore role-based dashboards

#### Known Issues
- None identified in initial release

#### Future Enhancements (Planned)
- Email notifications for account approval
- Advanced filtering and search
- Machine learning stroke risk prediction
- PDF export for patient reports
- Multi-language support
- Mobile app integration
- Real-time notifications
- Audit logging
- Data visualization admin dashboard
- Patient appointment scheduling

---

## Version Information
- **Current Version**: 1.0.0
- **Release Date**: December 5, 2025
- **Author**: Just Ahsan
- **Student ID**: 1122
- **Course**: COM7033
- **Institution**: Leeds Trinity University
- **Repository**: https://github.com/CS-LTU/com7033-assignment-ahsanIqbal1122

---

## How to Use This Project

See README.md for:
- Detailed installation instructions
- Step-by-step usage guide
- Database schema documentation
- API route reference
- Troubleshooting guide

See GIT_INSTRUCTIONS.md for:
- Git repository setup
- Commit instructions
- Future update procedures

---

**Status**: Production Ready ✅
