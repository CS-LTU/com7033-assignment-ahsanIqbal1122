"""
Services Module

This module contains business logic services that implement the service layer pattern,
separating business logic from route handlers for better modularity and testability.

Author: Ahsan Iqbal
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University
"""

from .auth_service import AuthService
from .patient_service import PatientService
from .logger_service import setup_logger

__all__ = ['AuthService', 'PatientService', 'setup_logger']
