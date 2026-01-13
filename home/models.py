from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from pymongo import MongoClient

from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.utils.crypto import get_random_string
from django.utils import timezone


class Student(models.Model):
    name = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=10, unique=True)
    year = models.CharField(max_length=10)
    attendance = models.JSONField(default=dict)

    class Meta:
        db_table = "student_it_2nd_year"  # <-- This forces Django to use the existing collection

    def __str__(self):
        return f"{self.name} - {self.roll_number}"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.CharField(max_length=50)
    date = models.DateField()
    is_present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.date} - {'Present' if self.is_present else 'Absent'}"
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#for login and registration

# class User(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=255)

#     def set_password(self, raw_password):
#         self.password = make_password(raw_password)

#     def check_password(self, raw_password):
#         return check_password(raw_password, self.password)

#     def __str__(self):
#         return self.email
from pymongo import MongoClient
from bson.objectid import ObjectId
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from urllib.parse import quote_plus
import pymongo
import os

# Use centralized database connection
from .db import get_mongo_client, get_db, get_students_collection, get_users_collection, get_password_reset_collection

# Get database connections
client = get_mongo_client()
db = get_db()
students_collection = get_students_collection()
users_collection = get_users_collection()
password_reset_collection = get_password_reset_collection()




# class CustomUserManager:
#     """ Custom manager for CustomUser """

#     @staticmethod
#     def create_user(username, email, password, **extra_fields):
#         """ Creates a new user and stores it in MongoDB """
#         if not email:
#             raise ValueError("The Email field must be set")
        
#         email = email.lower()
#         hashed_password = make_password(password)  # Hash the password
#         user_data = {
#             "_id": ObjectId(),  # MongoDB generates _id
#             "username": username,
#             "email": email,
#             "password": hashed_password,
#             "is_authorized": extra_fields.get("is_authorized", False),
#             "login_token": None,
#             "date_joined": timezone.now(),
#             "is_staff": extra_fields.get("is_staff", False),
#             "is_superuser": extra_fields.get("is_superuser", False),
#         }
#         users_collection.insert_one(user_data)
#         return user_data

#     @staticmethod
#     def create_superuser(username, email, password, **extra_fields):
#         """ Creates and returns a superuser """
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         return CustomUserManager.create_user(username, email, password, **extra_fields)

#     @staticmethod
#     def get_user_by_email(email):
#         """ Retrieve a user by email """
#         return users_collection.find_one({"email": email})

# from django.conf import settings
import hashlib
import hmac
import os
from datetime import datetime
def generate_password_hash(password):
    salt = os.urandom(16)  # Generate a random salt
    hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + ":" + hash_obj.hex()

def check_password_hash(hashed_password, password):
    salt, stored_hash = hashed_password.split(":")
    new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), 100000).hex()
    return hmac.compare_digest(stored_hash, new_hash)

# Custom User Model
class CustomUser:
    def __init__(self, username, email, password, is_authorized=False):
        self._id = ObjectId()  # MongoDB ID
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)  # Store hashed password
        self.is_authorized = is_authorized
        self.login_token = None
        #self.date_joined = datetime.utcnow()

    def save(self):
        """ Save user to MongoDB """
        users_collection.insert_one(self.__dict__)

    @staticmethod
    def find_by_email(email):
        """ Find user by email """
        return users_collection.find_one({"email": email})

    @staticmethod
    def authenticate(email, password):
        """ Authenticate user """
        user = CustomUser.find_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None

    def __str__(self):
        return f"User({self.username}, {self.email})"


class PasswordResetRequest:
    TOKEN_VALIDITY_PERIOD = timezone.timedelta(hours=1)

    def __init__(self, email):
        self.email = email
        self.token = get_random_string(32)
        self.created_at = timezone.now()

    def save(self):
        password_reset_collection.insert_one({
            "email": self.email,
            "token": self.token,
            "created_at": self.created_at,
        })

    @classmethod
    def get_by_token(cls, token):
        request = password_reset_collection.find_one({"token": token})
        if request:
            return cls(**request)
        return None

    def is_valid(self):
        return timezone.now() <= self.created_at + self.TOKEN_VALIDITY_PERIOD