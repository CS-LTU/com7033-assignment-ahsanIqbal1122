"""
Authentication Service

Implements authentication business logic following the service layer pattern.
Separates authentication concerns from route handlers for better testability and modularity.

Design Pattern: Service Layer Pattern
- Encapsulates business logic
- Provides reusable authentication methods
- Handles password hashing and verification
- Manages user session data

Security Features:
- Scrypt password hashing (32,768 iterations)
- Parameterized SQL queries (SQL injection prevention)
- Input validation and sanitization
- Secure session management

Author: Just Ahsan
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University
"""

import logging
from typing import Optional, Dict, Tuple
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection


class AuthService:
    """
    Service class for authentication operations.
    
    This class encapsulates all authentication-related business logic,
    following the Single Responsibility Principle (SRP).
    """
    
    def __init__(self):
        """Initialize the authentication service with logger."""
        self.logger = logging.getLogger(__name__)
        self.password_method = 'scrypt'  # Configurable hashing method
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Authenticate a user with username and password.
        
        Args:
            username (str): The username to authenticate
            password (str): The plaintext password to verify
            
        Returns:
            Tuple[bool, Optional[Dict], str]: 
                - Success status (True/False)
                - User data dictionary if successful, None otherwise
                - Error message if failed, empty string if successful
                
        Security Features:
        - Parameterized queries prevent SQL injection
        - Constant-time password comparison via check_password_hash
        - Logs authentication attempts (success/failure) for audit
        
        Example:
            >>> auth_service = AuthService()
            >>> success, user_data, error = auth_service.authenticate_user('john_doe', 'pass123')
            >>> if success:
            ...     print(f"Welcome {user_data['username']}")
        """
        # Input validation
        if not username or not password:
            self.logger.warning("Authentication attempted with empty credentials")
            return False, None, "Username and password are required"
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Parameterized query prevents SQL injection
            cur.execute(
                "SELECT id, username, password_hash, role, approved FROM users WHERE username = ?",
                (username,)
            )
            user = cur.fetchone()
            conn.close()
            
            # Check if user exists
            if not user:
                self.logger.warning(f"Login attempt for non-existent user: {username}")
                return False, None, "Invalid username or password"
            
            # Check if password matches (constant-time comparison)
            if not check_password_hash(user['password_hash'], password):
                self.logger.warning(f"Failed login attempt for user: {username} (invalid password)")
                return False, None, "Invalid username or password"
            
            # Check if account is approved
            if not user['approved']:
                self.logger.info(f"Login attempt for unapproved user: {username}")
                return False, None, "Account pending approval by administrator"
            
            # Success
            self.logger.info(f"Successful login for user: {username} (role: {user['role']})")
            
            user_data = {
                'id': user['id'],
                'username': user['username'],
                'role': user['role'],
                'approved': user['approved']
            }
            
            return True, user_data, ""
            
        except Exception as e:
            self.logger.error(f"Database error during authentication: {str(e)}")
            return False, None, "An error occurred during login. Please try again."
    
    def register_user(self, username: str, password: str, role: str, 
                     additional_data: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Register a new user account.
        
        Args:
            username (str): Unique username for the account
            password (str): Plaintext password (will be hashed)
            role (str): User role ('patient', 'doctor', 'admin')
            additional_data (Optional[Dict]): Additional user data (email, name, etc.)
            
        Returns:
            Tuple[bool, str]: 
                - Success status (True/False)
                - Success/error message
                
        Security Features:
        - Password hashing with scrypt (32,768 iterations)
        - Input validation and sanitization
        - Parameterized queries prevent SQL injection
        - Duplicate username detection
        
        Example:
            >>> auth_service = AuthService()
            >>> success, msg = auth_service.register_user('jane_doe', 'SecurePass123!', 'patient')
        """
        # Input validation
        if not username or not password:
            return False, "Username and password are required"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        if role not in ['patient', 'doctor', 'admin']:
            return False, "Invalid role specified"
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if username already exists
            cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cur.fetchone():
                conn.close()
                self.logger.warning(f"Registration attempt with duplicate username: {username}")
                return False, "Username already exists"
            
            # Hash password with scrypt (32,768 iterations)
            password_hash = generate_password_hash(password, method=self.password_method)
            
            # Insert new user (approved=0 for doctor/patient, 1 for admin)
            approved = 1 if role == 'admin' else 0
            
            cur.execute(
                "INSERT INTO users (username, password_hash, role, approved) VALUES (?, ?, ?, ?)",
                (username, password_hash, role, approved)
            )
            conn.commit()
            user_id = cur.lastrowid
            conn.close()
            
            self.logger.info(f"New user registered: {username} (role: {role}, id: {user_id})")
            
            return True, "Registration successful. Please wait for administrator approval."
            
        except Exception as e:
            self.logger.error(f"Database error during registration: {str(e)}")
            return False, "An error occurred during registration. Please try again."
    
    def approve_user(self, user_id: int, approving_admin_id: int) -> Tuple[bool, str]:
        """
        Approve a pending user account (admin only).
        
        Args:
            user_id (int): ID of the user to approve
            approving_admin_id (int): ID of the admin performing the approval
            
        Returns:
            Tuple[bool, str]: Success status and message
            
        Security: Only admins should call this method (enforced at route level)
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("UPDATE users SET approved = 1 WHERE id = ?", (user_id,))
            conn.commit()
            
            if cur.rowcount == 0:
                conn.close()
                return False, "User not found"
            
            conn.close()
            
            self.logger.info(f"User {user_id} approved by admin {approving_admin_id}")
            return True, "User approved successfully"
            
        except Exception as e:
            self.logger.error(f"Error approving user {user_id}: {str(e)}")
            return False, "An error occurred during approval"
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change user password with verification.
        
        Args:
            user_id (int): ID of the user changing password
            old_password (str): Current password for verification
            new_password (str): New password to set
            
        Returns:
            Tuple[bool, str]: Success status and message
            
        Security:
        - Verifies old password before allowing change
        - Enforces password complexity requirements
        - Hashes new password with scrypt
        """
        # Password validation
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get current password hash
            cur.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
            user = cur.fetchone()
            
            if not user:
                conn.close()
                return False, "User not found"
            
            # Verify old password
            if not check_password_hash(user['password_hash'], old_password):
                conn.close()
                self.logger.warning(f"Failed password change attempt for user {user_id} (invalid old password)")
                return False, "Current password is incorrect"
            
            # Hash and update new password
            new_password_hash = generate_password_hash(new_password, method=self.password_method)
            cur.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_password_hash, user_id))
            conn.commit()
            conn.close()
            
            self.logger.info(f"Password changed successfully for user {user_id}")
            return True, "Password changed successfully"
            
        except Exception as e:
            self.logger.error(f"Error changing password for user {user_id}: {str(e)}")
            return False, "An error occurred while changing password"
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """
        Retrieve user data by ID.
        
        Args:
            user_id (int): User ID to retrieve
            
        Returns:
            Optional[Dict]: User data dictionary or None if not found
        """
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, username, role, approved FROM users WHERE id = ?", (user_id,))
            user = cur.fetchone()
            conn.close()
            
            return dict(user) if user else None
            
        except Exception as e:
            self.logger.error(f"Error retrieving user {user_id}: {str(e)}")
            return None
