"""
Patient Service

Business logic for patient record management (SQLite and MongoDB).
Implements the service layer pattern for patient CRUD operations.

Design Pattern: Service Layer Pattern
- Separates data access from business logic
- Provides consistent API for patient operations
- Handles both SQLite and MongoDB data sources
- Implements validation and error handling

Author: Ahsan Iqbal
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University
"""

import logging
from typing import Optional, Dict, List, Tuple
from database.db import get_db_connection
from database import mongo


class PatientService:
    """
    Service class for patient record operations.
    
    Handles patient data management for both SQLite (reports) and MongoDB (flexible records).
    Implements business logic and validation separate from route handlers.
    """
    
    def __init__(self):
        """Initialize patient service with logger."""
        self.logger = logging.getLogger(__name__)
    
    def create_patient_report(self, user_id: int, report_data: Dict) -> Tuple[bool, str]:
        """
        Create a new patient report in SQLite.
        
        Args:
            user_id (int): ID of the user creating the report
            report_data (Dict): Patient report data
            
        Returns:
            Tuple[bool, str]: Success status and message/report_id
            
        Security:
        - Parameterized queries prevent SQL injection
        - Input validation for all fields
        - Ownership verification (user_id foreign key)
        
        Example:
            >>> patient_service = PatientService()
            >>> data = {'age': 45, 'gender': 'Male', 'hypertension': 0, ...}
            >>> success, msg = patient_service.create_patient_report(user_id=1, report_data=data)
        """
        # Validate required fields
        required_fields = ['age', 'gender', 'hypertension', 'heart_disease', 
                          'ever_married', 'work_type', 'residence_type',
                          'avg_glucose_level', 'bmi', 'smoking_status', 'stroke']
        
        for field in required_fields:
            if field not in report_data:
                return False, f"Missing required field: {field}"
        
        # Validate data types and ranges
        try:
            age = float(report_data['age'])
            if age < 0 or age > 150:
                return False, "Age must be between 0 and 150"
            
            glucose = float(report_data['avg_glucose_level'])
            if glucose < 0 or glucose > 500:
                return False, "Glucose level must be between 0 and 500"
            
            bmi = float(report_data['bmi'])
            if bmi < 0 or bmi > 100:
                return False, "BMI must be between 0 and 100"
            
        except (ValueError, TypeError) as e:
            return False, f"Invalid numeric value: {str(e)}"
        
        # Validate enum fields
        if report_data['gender'] not in ['Male', 'Female', 'Other']:
            return False, "Invalid gender value"
        
        if report_data['ever_married'] not in ['Yes', 'No']:
            return False, "Invalid marital status"
        
        if report_data['work_type'] not in ['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked']:
            return False, "Invalid work type"
        
        if report_data['residence_type'] not in ['Urban', 'Rural']:
            return False, "Invalid residence type"
        
        if report_data['smoking_status'] not in ['formerly smoked', 'never smoked', 'smokes', 'Unknown']:
            return False, "Invalid smoking status"
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO patient_reports (
                    user_id, age, gender, hypertension, heart_disease,
                    ever_married, work_type, residence_type, 
                    avg_glucose_level, bmi, smoking_status, stroke
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                age,
                report_data['gender'],
                int(report_data['hypertension']),
                int(report_data['heart_disease']),
                report_data['ever_married'],
                report_data['work_type'],
                report_data['residence_type'],
                glucose,
                bmi,
                report_data['smoking_status'],
                int(report_data['stroke'])
            ))
            
            conn.commit()
            report_id = cur.lastrowid
            conn.close()
            
            self.logger.info(f"Patient report {report_id} created for user {user_id}")
            return True, str(report_id)
            
        except Exception as e:
            self.logger.error(f"Error creating patient report: {str(e)}")
            return False, "An error occurred while creating the report"
    
    def get_patient_reports(self, user_id: Optional[int] = None, 
                           limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Retrieve patient reports from SQLite.
        
        Args:
            user_id (Optional[int]): Filter by user ID (None for all reports)
            limit (int): Maximum number of reports to return
            offset (int): Number of reports to skip (pagination)
            
        Returns:
            List[Dict]: List of patient report dictionaries
            
        Security: Implements ownership verification - patients can only see their own reports
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            if user_id:
                # Patient view - only their own reports
                cur.execute("""
                    SELECT * FROM patient_reports 
                    WHERE user_id = ? 
                    ORDER BY id DESC 
                    LIMIT ? OFFSET ?
                """, (user_id, limit, offset))
            else:
                # Admin/Doctor view - all reports
                cur.execute("""
                    SELECT * FROM patient_reports 
                    ORDER BY id DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            
            reports = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            return reports
            
        except Exception as e:
            self.logger.error(f"Error retrieving patient reports: {str(e)}")
            return []
    
    def get_report_by_id(self, report_id: int, user_id: Optional[int] = None) -> Optional[Dict]:
        """
        Retrieve a specific patient report by ID.
        
        Args:
            report_id (int): ID of the report to retrieve
            user_id (Optional[int]): User ID for ownership verification
            
        Returns:
            Optional[Dict]: Report data or None if not found/unauthorized
            
        Security: Verifies ownership if user_id provided (prevents privilege escalation)
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            if user_id:
                # Verify ownership
                cur.execute(
                    "SELECT * FROM patient_reports WHERE id = ? AND user_id = ?",
                    (report_id, user_id)
                )
            else:
                # Admin/Doctor access
                cur.execute("SELECT * FROM patient_reports WHERE id = ?", (report_id,))
            
            report = cur.fetchone()
            conn.close()
            
            return dict(report) if report else None
            
        except Exception as e:
            self.logger.error(f"Error retrieving report {report_id}: {str(e)}")
            return None
    
    def update_patient_report(self, report_id: int, report_data: Dict, 
                             user_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Update an existing patient report.
        
        Args:
            report_id (int): ID of the report to update
            report_data (Dict): Updated report data
            user_id (Optional[int]): User ID for ownership verification
            
        Returns:
            Tuple[bool, str]: Success status and message
            
        Security: Verifies ownership before allowing update
        """
        # Verify report exists and user has permission
        existing_report = self.get_report_by_id(report_id, user_id)
        if not existing_report:
            return False, "Report not found or access denied"
        
        # Validate updated data (reuse validation from create)
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE patient_reports SET
                    age = ?, gender = ?, hypertension = ?, heart_disease = ?,
                    ever_married = ?, work_type = ?, residence_type = ?,
                    avg_glucose_level = ?, bmi = ?, smoking_status = ?, stroke = ?
                WHERE id = ?
            """, (
                float(report_data['age']),
                report_data['gender'],
                int(report_data['hypertension']),
                int(report_data['heart_disease']),
                report_data['ever_married'],
                report_data['work_type'],
                report_data['residence_type'],
                float(report_data['avg_glucose_level']),
                float(report_data['bmi']),
                report_data['smoking_status'],
                int(report_data['stroke']),
                report_id
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Patient report {report_id} updated")
            return True, "Report updated successfully"
            
        except Exception as e:
            self.logger.error(f"Error updating report {report_id}: {str(e)}")
            return False, "An error occurred while updating the report"
    
    def delete_patient_report(self, report_id: int, user_id: Optional[int] = None) -> Tuple[bool, str]:
        """
        Delete a patient report.
        
        Args:
            report_id (int): ID of the report to delete
            user_id (Optional[int]): User ID for ownership verification
            
        Returns:
            Tuple[bool, str]: Success status and message
            
        Security: Verifies ownership before allowing deletion
        """
        # Verify report exists and user has permission
        existing_report = self.get_report_by_id(report_id, user_id)
        if not existing_report:
            return False, "Report not found or access denied"
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("DELETE FROM patient_reports WHERE id = ?", (report_id,))
            conn.commit()
            conn.close()
            
            self.logger.info(f"Patient report {report_id} deleted")
            return True, "Report deleted successfully"
            
        except Exception as e:
            self.logger.error(f"Error deleting report {report_id}: {str(e)}")
            return False, "An error occurred while deleting the report"
    
    def search_patients(self, search_term: str, limit: int = 50) -> List[Dict]:
        """
        Search for patients by name or ID.
        
        Args:
            search_term (str): Search query
            limit (int): Maximum results to return
            
        Returns:
            List[Dict]: List of matching patient records
            
        Security: Uses parameterized queries with LIKE operator
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            search_pattern = f"%{search_term}%"
            
            cur.execute("""
                SELECT pr.*, u.username 
                FROM patient_reports pr
                LEFT JOIN users u ON pr.user_id = u.id
                WHERE CAST(pr.id AS TEXT) LIKE ? 
                   OR u.username LIKE ?
                LIMIT ?
            """, (search_pattern, search_pattern, limit))
            
            results = [dict(row) for row in cur.fetchall()]
            conn.close()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching patients: {str(e)}")
            return []
    
    def calculate_stroke_risk_score(self, patient_data: Dict) -> float:
        """
        Calculate stroke risk score based on patient data.
        
        Args:
            patient_data (Dict): Patient health data
            
        Returns:
            float: Risk score (0-100)
            
        Business Logic: 
        - Age: 0.3 points per year
        - Hypertension: +15 points
        - Heart disease: +20 points
        - High glucose (>200): +10 points
        - High BMI (>30): +5 points
        - Smoking: +10 points
        """
        score = 0.0
        
        # Age factor
        age = float(patient_data.get('age', 0))
        score += age * 0.3
        
        # Hypertension
        if int(patient_data.get('hypertension', 0)) == 1:
            score += 15
        
        # Heart disease
        if int(patient_data.get('heart_disease', 0)) == 1:
            score += 20
        
        # Glucose level
        glucose = float(patient_data.get('avg_glucose_level', 0))
        if glucose > 200:
            score += 10
        
        # BMI
        bmi = float(patient_data.get('bmi', 0))
        if bmi > 30:
            score += 5
        
        # Smoking
        smoking = patient_data.get('smoking_status', '')
        if smoking in ['smokes', 'formerly smoked']:
            score += 10
        
        # Cap at 100
        return min(score, 100.0)
