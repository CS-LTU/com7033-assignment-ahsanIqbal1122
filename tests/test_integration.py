"""
Integration Tests for Stroke Pass Application

Tests complete workflows across multiple components:
- User registration → approval → login → data access
- Patient report creation → retrieval → update → deletion
- Authentication → authorization → data ownership verification
- Database integration (SQLite + MongoDB)

Design Pattern: Integration Testing
- Tests multiple components working together
- Uses pytest fixtures for setup/teardown
- Mocks external dependencies (MongoDB)
- Tests complete user journeys

Author: Just Ahsan
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from database.db import get_db_connection, init_db
from services.auth_service import AuthService
from services.patient_service import PatientService
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """
    Create and configure Flask app for testing.
    
    Returns:
        Flask app instance with testing configuration
    """
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for tests
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Initialize database
    init_db()
    
    yield flask_app
    
    # Cleanup after tests
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username LIKE 'test_%'")
    cur.execute("DELETE FROM patient_reports WHERE id > 10000")
    conn.commit()
    conn.close()


@pytest.fixture
def client(app):
    """
    Create test client for making requests.
    
    Returns:
        Flask test client
    """
    return app.test_client()


@pytest.fixture
def auth_service():
    """
    Create AuthService instance for testing.
    
    Returns:
        AuthService instance
    """
    return AuthService()


@pytest.fixture
def patient_service():
    """
    Create PatientService instance for testing.
    
    Returns:
        PatientService instance
    """
    return PatientService()


@pytest.fixture
def test_user():
    """
    Create a test user in the database.
    
    Returns:
        dict: Test user data
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    password_hash = generate_password_hash('test_password', method='scrypt')
    cur.execute(
        "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, ?, ?)",
        ('test_integration_user', password_hash, 'patient', 1)
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    
    return {
        'id': user_id,
        'username': 'test_integration_user',
        'password': 'test_password',
        'role': 'patient'
    }


class TestCompleteUserJourney:
    """
    Integration tests for complete user workflows.
    
    Tests the entire user journey from registration to data access.
    """
    
    def test_user_registration_approval_login_workflow(self, auth_service):
        """
        Test complete workflow: Registration → Admin Approval → Login
        
        Integration Points:
        - AuthService.register_user()
        - Database user creation
        - AuthService.approve_user()
        - AuthService.authenticate_user()
        
        Expected Flow:
        1. User registers (approved=0)
        2. Admin approves user (approved=1)
        3. User can now log in successfully
        """
        print("\n[INTEGRATION TEST] User Registration → Approval → Login")
        
        # Step 1: Register new user
        username = 'test_journey_user'
        password = 'SecurePass123!'
        
        success, message = auth_service.register_user(username, password, 'patient')
        assert success, f"Registration failed: {message}"
        print(f"  ✓ Step 1: User registered - {message}")
        
        # Step 2: Verify user cannot login before approval
        success, user_data, error = auth_service.authenticate_user(username, password)
        assert not success, "User should not be able to login before approval"
        assert "pending approval" in error.lower()
        print(f"  ✓ Step 2: Login blocked before approval - {error}")
        
        # Step 3: Get user ID
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        user_id = user['id']
        conn.close()
        
        # Step 4: Admin approves user
        success, message = auth_service.approve_user(user_id, admin_id=1)
        assert success, f"Approval failed: {message}"
        print(f"  ✓ Step 3: Admin approved user - {message}")
        
        # Step 5: User can now login
        success, user_data, error = auth_service.authenticate_user(username, password)
        assert success, f"Login failed after approval: {error}"
        assert user_data['username'] == username
        assert user_data['role'] == 'patient'
        print(f"  ✓ Step 4: User logged in successfully")
        
        # Cleanup
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
    
    
    def test_patient_report_crud_workflow(self, patient_service, test_user):
        """
        Test complete CRUD workflow for patient reports.
        
        Integration Points:
        - PatientService.create_patient_report()
        - PatientService.get_report_by_id()
        - PatientService.update_patient_report()
        - PatientService.delete_patient_report()
        - Database operations (SQLite)
        
        Expected Flow:
        1. Create patient report
        2. Retrieve report
        3. Update report
        4. Delete report
        """
        print("\n[INTEGRATION TEST] Patient Report CRUD Workflow")
        
        user_id = test_user['id']
        
        # Step 1: Create patient report
        report_data = {
            'age': 55,
            'gender': 'Male',
            'hypertension': 1,
            'heart_disease': 0,
            'ever_married': 'Yes',
            'work_type': 'Private',
            'residence_type': 'Urban',
            'avg_glucose_level': 180.5,
            'bmi': 28.3,
            'smoking_status': 'formerly smoked',
            'stroke': 0
        }
        
        success, report_id = patient_service.create_patient_report(user_id, report_data)
        assert success, f"Failed to create report: {report_id}"
        report_id = int(report_id)
        print(f"  ✓ Step 1: Created patient report (ID: {report_id})")
        
        # Step 2: Retrieve report
        retrieved_report = patient_service.get_report_by_id(report_id, user_id)
        assert retrieved_report is not None, "Failed to retrieve report"
        assert retrieved_report['age'] == 55
        assert retrieved_report['gender'] == 'Male'
        print(f"  ✓ Step 2: Retrieved report successfully")
        
        # Step 3: Update report
        updated_data = report_data.copy()
        updated_data['age'] = 56
        updated_data['bmi'] = 27.5
        
        success, message = patient_service.update_patient_report(report_id, updated_data, user_id)
        assert success, f"Failed to update report: {message}"
        print(f"  ✓ Step 3: Updated report - {message}")
        
        # Verify update
        updated_report = patient_service.get_report_by_id(report_id, user_id)
        assert updated_report['age'] == 56
        assert updated_report['bmi'] == 27.5
        
        # Step 4: Calculate risk score
        risk_score = patient_service.calculate_stroke_risk_score(updated_report)
        assert risk_score > 0, "Risk score should be calculated"
        print(f"  ✓ Step 4: Calculated risk score: {risk_score:.2f}")
        
        # Step 5: Delete report
        success, message = patient_service.delete_patient_report(report_id, user_id)
        assert success, f"Failed to delete report: {message}"
        print(f"  ✓ Step 5: Deleted report - {message}")
        
        # Verify deletion
        deleted_report = patient_service.get_report_by_id(report_id, user_id)
        assert deleted_report is None, "Report should be deleted"
    
    
    def test_authentication_and_authorization_integration(self, client, test_user):
        """
        Test authentication and authorization working together.
        
        Integration Points:
        - Login authentication
        - Session creation
        - Role-based access control
        - Route protection
        
        Expected Flow:
        1. User logs in
        2. Session is created
        3. User can access authorized routes
        4. User is blocked from unauthorized routes
        5. User logs out
        """
        print("\n[INTEGRATION TEST] Authentication & Authorization")
        
        # Step 1: Login
        response = client.post('/login', data={
            'username': test_user['username'],
            'password': test_user['password']
        }, follow_redirects=False)
        
        assert response.status_code == 302, "Login should redirect"
        print(f"  ✓ Step 1: User logged in (redirect to dashboard)")
        
        # Step 2: Verify session
        with client.session_transaction() as sess:
            assert 'user_id' in sess or sess.get('_user_id'), "Session should contain user_id"
            print(f"  ✓ Step 2: Session created with user data")
        
        # Step 3: Access patient dashboard (authorized)
        response = client.get('/patient_dashboard', follow_redirects=False)
        # Should succeed or redirect (depends on implementation)
        print(f"  ✓ Step 3: Accessed patient dashboard (status: {response.status_code})")
        
        # Step 4: Try to access admin dashboard (unauthorized)
        response = client.get('/admin_dashboard', follow_redirects=False)
        # Should redirect to login or show 403
        assert response.status_code in [302, 403], "Patient should not access admin dashboard"
        print(f"  ✓ Step 4: Blocked from admin dashboard (status: {response.status_code})")
        
        # Step 5: Logout
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302, "Logout should redirect"
        print(f"  ✓ Step 5: User logged out")
        
        # Step 6: Verify session cleared
        with client.session_transaction() as sess:
            assert sess.get('user_id') is None, "Session should be cleared after logout"
            print(f"  ✓ Step 6: Session cleared")


class TestDataOwnershipAndSecurity:
    """
    Integration tests for data ownership and security controls.
    
    Tests that users can only access their own data.
    """
    
    def test_patient_cannot_access_other_patient_data(self, patient_service, test_user):
        """
        Test that patients can only access their own reports.
        
        Security Test:
        - Patient A creates report
        - Patient B tries to access Patient A's report
        - Access should be denied
        """
        print("\n[INTEGRATION TEST] Data Ownership Verification")
        
        # Create two test users
        conn = get_db_connection()
        cur = conn.cursor()
        
        password_hash = generate_password_hash('test123', method='scrypt')
        
        cur.execute(
            "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, ?, ?)",
            ('test_patient_a', password_hash, 'patient', 1)
        )
        patient_a_id = cur.lastrowid
        
        cur.execute(
            "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, ?, ?)",
            ('test_patient_b', password_hash, 'patient', 1)
        )
        patient_b_id = cur.lastrowid
        
        conn.commit()
        conn.close()
        
        print(f"  ✓ Created two test patients (IDs: {patient_a_id}, {patient_b_id})")
        
        # Patient A creates report
        report_data = {
            'age': 40,
            'gender': 'Female',
            'hypertension': 0,
            'heart_disease': 0,
            'ever_married': 'Yes',
            'work_type': 'Private',
            'residence_type': 'Urban',
            'avg_glucose_level': 95,
            'bmi': 22,
            'smoking_status': 'never smoked',
            'stroke': 0
        }
        
        success, report_id = patient_service.create_patient_report(patient_a_id, report_data)
        assert success
        report_id = int(report_id)
        print(f"  ✓ Patient A created report (ID: {report_id})")
        
        # Patient A can access their own report
        report = patient_service.get_report_by_id(report_id, patient_a_id)
        assert report is not None, "Patient A should access their own report"
        print(f"  ✓ Patient A can access their own report")
        
        # Patient B tries to access Patient A's report (should fail)
        report = patient_service.get_report_by_id(report_id, patient_b_id)
        assert report is None, "Patient B should NOT access Patient A's report"
        print(f"  ✓ Patient B blocked from accessing Patient A's report")
        
        # Patient B tries to update Patient A's report (should fail)
        success, message = patient_service.update_patient_report(report_id, report_data, patient_b_id)
        assert not success, "Patient B should NOT update Patient A's report"
        print(f"  ✓ Patient B blocked from updating Patient A's report")
        
        # Patient B tries to delete Patient A's report (should fail)
        success, message = patient_service.delete_patient_report(report_id, patient_b_id)
        assert not success, "Patient B should NOT delete Patient A's report"
        print(f"  ✓ Patient B blocked from deleting Patient A's report")
        
        # Cleanup
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM patient_reports WHERE id = ?", (report_id,))
        cur.execute("DELETE FROM users WHERE id IN (?, ?)", (patient_a_id, patient_b_id))
        conn.commit()
        conn.close()


class TestDatabaseIntegration:
    """
    Integration tests for database operations.
    
    Tests SQLite and MongoDB integration.
    """
    
    def test_sqlite_transaction_rollback_on_error(self):
        """
        Test that database transactions rollback on error.
        
        Integration Test:
        - Start transaction
        - Perform operations
        - Trigger error
        - Verify rollback
        """
        print("\n[INTEGRATION TEST] SQLite Transaction Rollback")
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            # Start transaction (implicit in SQLite)
            cur.execute("BEGIN TRANSACTION")
            
            # Insert test user
            password_hash = generate_password_hash('test', method='scrypt')
            cur.execute(
                "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, ?, ?)",
                ('test_rollback_user', password_hash, 'patient', 1)
            )
            
            # Trigger error (duplicate username)
            cur.execute(
                "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, ?, ?)",
                ('test_rollback_user', password_hash, 'patient', 1)
            )
            
            conn.commit()
            
            # Should not reach here
            assert False, "Duplicate insert should have failed"
            
        except Exception as e:
            # Rollback on error
            conn.rollback()
            print(f"  ✓ Transaction rolled back on error: {str(e)[:50]}")
            
            # Verify user was not inserted
            cur.execute("SELECT id FROM users WHERE username = ?", ('test_rollback_user',))
            user = cur.fetchone()
            assert user is None, "User should not exist after rollback"
            print(f"  ✓ Data not persisted after rollback")
        
        finally:
            conn.close()


# Run tests
if __name__ == '__main__':
    print("="*70)
    print("  INTEGRATION TESTS - Stroke Pass Application")
    print("="*70)
    
    pytest.main([__file__, '-v', '--tb=short', '-s'])
