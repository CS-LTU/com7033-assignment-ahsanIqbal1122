# mongo.py
"""
MongoDB connection and patient record operations for Stroke Intelligence System.
"""
from pymongo import MongoClient
import os

# MongoDB connection URI (default: localhost)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("MONGO_DBNAME", "stroke_pass_app")
COLLECTION_NAME = "patients"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
patients_collection = db[COLLECTION_NAME]

def add_patient(patient_data):
    """Insert a new patient record into MongoDB."""
    return patients_collection.insert_one(patient_data)

def get_patient(patient_id):
    """Retrieve a patient record by _id."""
    return patients_collection.find_one({"_id": patient_id})

def update_patient(patient_id, update_data):
    """Update a patient record by _id."""
    return patients_collection.update_one({"_id": patient_id}, {"$set": update_data})

def delete_patient(patient_id):
    """Delete a patient record by _id."""
    return patients_collection.delete_one({"_id": patient_id})

def list_patients(query=None):
    """List all patient records (optionally filtered by query)."""
    return list(patients_collection.find(query or {}))
