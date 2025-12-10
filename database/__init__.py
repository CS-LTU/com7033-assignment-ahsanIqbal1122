"""
Database Package

Contains database management modules for the Stroke Intelligence System.

Author: Ahsan Iqbal
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University

Modules:
    - db.py: SQLite database operations (users, patient_reports, Kaggle dataset)
    - mongo.py: MongoDB operations (flexible patient records)

This package provides a dual-database architecture:
    1. SQLite: Structured data (authentication, reports)
    2. MongoDB: NoSQL flexible patient records
"""
