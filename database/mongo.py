"""
MongoDB Operations Module

Handles NoSQL database operations for flexible patient record storage.

Author: Ahsan Iqbal
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University

Database Architecture:
    - Database: stroke_pass_app
    - Collection: patients
    - Document Structure: Flexible JSON-like documents (no fixed schema)
    
Features:
    - CRUD operations: Create, Read, Update, Delete patient records
    - Flexible schema: No migrations needed for schema changes
    - Environment-based configuration
    - pymongo integration for MongoDB operations

Configuration:
    - MONGO_URI: MongoDB connection string (default: mongodb://localhost:27017/)
    - MONGO_DBNAME: Database name (default: stroke_pass_app)
    - Set via environment variables or config_mongo.py

Dependencies:
    - pymongo: Python MongoDB driver (third-party integration)
    - bson.objectid: MongoDB document ID type

Usage:
    >>> from database.mongo import add_patient, get_patient
    >>> patient_data = {"name": "John Doe", "age": 45, "gender": "Male"}
    >>> result = add_patient(patient_data)
    >>> patient = get_patient(result.inserted_id)
"""

# Third-party imports
from pymongo import MongoClient  # MongoDB Python driver

# Standard library imports
import os  # Environment variable access

# ============================================================
# MONGODB CONNECTION CONFIGURATION
# ============================================================

# MongoDB connection URI - supports local, remote, and MongoDB Atlas
# Default: Local MongoDB instance on port 27017
# Production: Set MONGO_URI environment variable
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

# Database name for the Stroke Intelligence System
DB_NAME = os.environ.get("MONGO_DBNAME", "stroke_pass_app")

# Collection name for patient records
COLLECTION_NAME = "patients"

# ============================================================
# MONGODB CLIENT INITIALIZATION
# ============================================================

# Create MongoDB client connection
# Lazy connection: Actual connection established on first operation
client = MongoClient(MONGO_URI)

# Get database reference
db = client[DB_NAME]

# Get collection reference for patient records
patients_collection = db[COLLECTION_NAME]

# ============================================================
# CRUD OPERATIONS - Create, Read, Update, Delete
# ============================================================

def add_patient(patient_data):
    """
    Insert a new patient record into MongoDB.
    
    Args:
        patient_data (dict): Patient record data as JSON-like dictionary
            Example: {
                "name": "John Doe",
                "age": 45,
                "gender": "Male",
                "hypertension": 1,
                "stroke": 0
            }
    
    Returns:
        pymongo.results.InsertOneResult: Result object with inserted_id attribute
        
    Example:
        >>> result = add_patient({"name": "Jane", "age": 50})
        >>> print(result.inserted_id)
        ObjectId('507f1f77bcf86cd799439011')
    """
    return patients_collection.insert_one(patient_data)


def get_patient(patient_id):
    """
    Retrieve a single patient record by MongoDB ObjectId.
    
    Args:
        patient_id (ObjectId): MongoDB document ID
            Must be a bson.objectid.ObjectId instance
    
    Returns:
        dict or None: Patient document if found, None otherwise
        
    Example:
        >>> from bson.objectid import ObjectId
        >>> patient = get_patient(ObjectId("507f1f77bcf86cd799439011"))
        >>> print(patient['name'])
    """
    return patients_collection.find_one({"_id": patient_id})


def update_patient(patient_id, update_data):
    """
    Update an existing patient record by MongoDB ObjectId.
    
    Uses MongoDB $set operator to update specific fields without replacing entire document.
    
    Args:
        patient_id (ObjectId): MongoDB document ID
        update_data (dict): Fields to update
            Example: {"age": 46, "hypertension": 1}
    
    Returns:
        pymongo.results.UpdateResult: Result object with matched_count and modified_count
        
    Example:
        >>> result = update_patient(patient_id, {"age": 46})
        >>> print(result.modified_count)  # Number of documents modified
    """
    return patients_collection.update_one({"_id": patient_id}, {"$set": update_data})


def delete_patient(patient_id):
    """
    Delete a patient record by MongoDB ObjectId.
    
    Args:
        patient_id (ObjectId): MongoDB document ID to delete
    
    Returns:
        pymongo.results.DeleteResult: Result object with deleted_count attribute
        
    Example:
        >>> result = delete_patient(patient_id)
        >>> print(result.deleted_count)  # 1 if deleted, 0 if not found
    """
    return patients_collection.delete_one({"_id": patient_id})


def list_patients(query=None):
    """
    List all patient records with optional query filter.
    
    Args:
        query (dict, optional): MongoDB query filter
            Examples:
            - None or {}: Returns all patients
            - {"age": {"$gt": 50}}: Patients older than 50
            - {"gender": "Male", "stroke": 1}: Male patients with stroke
    
    Returns:
        list: List of patient documents (dicts)
        
    Examples:
        >>> # Get all patients
        >>> all_patients = list_patients()
        
        >>> # Get patients with hypertension
        >>> hypertensive = list_patients({"hypertension": 1})
        
        >>> # Get elderly patients (age > 65)
        >>> elderly = list_patients({"age": {"$gt": 65}})
    """
    return list(patients_collection.find(query or {}))
