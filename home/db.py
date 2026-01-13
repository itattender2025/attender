"""
Centralized MongoDB connection module
Provides a single source of truth for database connections
"""
import os
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Singleton pattern for MongoDB client
_client = None
_db = None


def get_mongo_client():
    """Get or create MongoDB client (singleton)"""
    global _client
    if _client is None:
        # Get credentials from environment
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")
        
        if not username or not password:
            raise ValueError("MongoDB credentials not found in environment variables")
        
        # Encode credentials
        username_encoded = quote_plus(username)
        password_encoded = quote_plus(password)
        
        # Build connection string
        mongo_uri = f"mongodb+srv://{username_encoded}:{password_encoded}@cluster007.qhfdiks.mongodb.net/?retryWrites=true&w=majority&appName=Cluster007"
        
        # Create client with proper TLS validation
        _client = MongoClient(mongo_uri, tls=True)
        
    return _client


def get_db():
    """Get or create database connection (singleton)"""
    global _db
    if _db is None:
        client = get_mongo_client()
        _db = client["attender_db"]
    return _db


# Convenience functions for common collections
def get_students_collection():
    """Get students collection"""
    db = get_db()
    return db["student_it_2nd_year"]


def get_users_collection():
    """Get users collection"""
    db = get_db()
    return db["home_user"]


def get_password_reset_collection():
    """Get password reset collection"""
    db = get_db()
    return db["home_passwordresetrequest"]


def get_lab_groups_collection():
    """Get lab groups collection"""
    db = get_db()
    return db["lab_groups"]
