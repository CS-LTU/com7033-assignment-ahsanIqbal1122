"""
Routes Package

Contains Flask Blueprint modules for the Stroke Intelligence System.

Author: Ahsan Iqbal
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University

Blueprints:
    - auth_routes: User authentication (login, registration, logout)
    - dashboard_routes: Role-based dashboards (admin, doctor, patient)
    - patient_routes: SQLite patient report management (CRUD operations)
    - mongo_patient_routes: MongoDB patient record management

All blueprints are registered in app.py with appropriate URL prefixes.
"""
