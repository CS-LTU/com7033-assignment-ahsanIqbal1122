"""
MongoDB Configuration

Configuration settings for MongoDB database connection.
MongoDB is used for flexible patient record storage with NoSQL schema.

Author: Just Ahsan
Course: COM7033 - Secure Programming
Institution: Leeds Trinity University

Database Architecture:
- SQLite: Used for user authentication and structured patient reports
- MongoDB: Used for flexible patient records with varying schemas

Connection String Format:
- Local: mongodb://localhost:27017/
- Remote: mongodb://username:password@host:port/
- Atlas: mongodb+srv://username:password@cluster.mongodb.net/

Collections:
- patients: Flexible patient medical records
"""

# MongoDB connection URI
# Local MongoDB instance on default port 27017
# For production, use environment variable: os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_URI = "mongodb://localhost:27017/"

# MongoDB database name
# All collections will be created under this database
MONGO_DBNAME = "stroke_pass_app"
