from django.http import HttpResponse,request
from django.shortcuts import render,redirect
from datetime import datetime
from .models import Student

from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
from .models import Student, Attendance
from datetime import datetime
from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt
import pymongo
from urllib.parse import quote_plus
#Connect to MongoDB

from django.shortcuts import render
from django.utils.dateparse import parse_date
from datetime import datetime

from datetime import datetime
from django.shortcuts import render
from django.utils.dateparse import parse_date
from .models import Student

from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, PasswordResetRequest
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password


username = quote_plus("it24akashmondal")
password = quote_plus("akashmondal@2004")



client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster007.oznj7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster007")
db = client["attender_db"]
students_collection = db["student_it_2nd_year"]  # Collection where student records are stored
users_collection = db["home_user"]
password_reset_collection = db["home_passwordresetrequest"]

from django.contrib.auth import authenticate, login, logout



from django.contrib.auth.models import User
from django.contrib import messages






users_collection = db["home_user"]  # Ensure collection name is correct

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not (first_name and last_name and email and password):
            messages.error(request, "⚠️ All fields are required!")
            return redirect("signup")

        # 🔹 Check if email already exists
        existing_user = users_collection.find_one({"email": email}, {"_id": 1})
        if existing_user:
            messages.error(request, "🚫 Email already registered.")
            return redirect("signup")

        hashed_password = make_password(password)

        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": email,
            "password": hashed_password,
        }

        # 🔹 Insert user into MongoDB
        users_collection.insert_one(user_data)

        messages.success(request, "✅ Signup successful! Please log in.")
        return redirect("login")

    return render(request, 'login.html')
from django.contrib.auth.hashers import check_password




from django.contrib.auth import login
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User  # Temporary, just for login()
from bson import ObjectId

class MongoDBAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        user = users_collection.find_one({"email": email})
        if user and check_password(password, user["password"]):
            # Create a temporary Django user object (not saved in DB)
            temp_user = User(id=user["_id"], username=user["email"])
            temp_user.backend = "yourapp.backends.MongoDBAuthBackend"  # Ensure proper backend
            return temp_user
        return None

    def get_user(self, user_id):
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return User(id=str(user["_id"]), username=user["email"])
        return None



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password  # Use Django's password checker
from pymongo import MongoClient
from bson.objectid import ObjectId




from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.urls import reverse

# def login_view(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")

#         user = users_collection.find_one({"email": email})

#         if user and check_password(password, user["password"]):
#             request.session["user_id"] = str(user["_id"])  # Store session
#             request.session.modified = True

#             # 🔴 DEBUG: Print session to check if it’s stored
#             print("\n🔵 SESSION DATA AFTER LOGIN:", dict(request.session.items()))
#             request.session.save()
#             next_url = request.GET.get("next") or reverse("index")
#             return redirect(next_url)  # Redirect to index or next page
#         else:
#             messages.error(request, "Invalid email or password.")
#             return redirect("login")

#     return render(request, "login.html")


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        user_data = users_collection.find_one({"email": email})

        if user_data:
            token = get_random_string(32)
            password_reset_collection.insert_one({"email": email, "token": token})

            # You need to implement email sending
            reset_link = f"http://localhost:8000/reset-password/{token}/"
            print(f"Reset Link: {reset_link}")  # Debugging: Log the reset link

            messages.success(request, "Reset link sent to your email.")
        else:
            messages.error(request, "Email not found.")

    return render(request, 'login.html')
# def logout_view(request):
#     pass
from django.shortcuts import render, redirect
from functools import wraps
from pymongo import MongoClient
from datetime import datetime, timedelta
import secrets
from django.contrib.auth.hashers import check_password


users = db.home_user
sessions = db.django_session

# 🔹 Custom Authentication Decorator
from datetime import datetime, timezone

from django.utils.timezone import now  # Django's timezone-aware datetime
from django.utils.timezone import now  # Use Django's timezone-aware datetime

def custom_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        session_token = request.COOKIES.get("session_token")
        print("🔹 Session Token from Cookie:", session_token)

        if not session_token:
            print("❌ No session token found, redirecting to login.")
            return redirect("login")

        session = sessions.find_one({"session_token": session_token})

        if not session:
            print("❌ Session not found, redirecting to login.")
            return redirect("login")

        # Ensure session["expires_at"] is timezone-aware
        session_expires_at = session["expires_at"]
        
        if isinstance(session_expires_at, str):  
            session_expires_at = datetime.fromisoformat(session_expires_at).replace(tzinfo=timezone.utc)
        elif session_expires_at.tzinfo is None:  
            session_expires_at = session_expires_at.replace(tzinfo=timezone.utc)  

        if session_expires_at < now():  # Compare using timezone-aware `now()`
            print("❌ Session expired, redirecting to login.")
            return redirect("login")

        request.user = {"id": session["user_id"], "email": session["email"]}
        return view_func(request, *args, **kwargs)

    return wrapper



# 🔹 Login View
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print("🔍 Full Form Data:", request.POST.dict())  # Debugging

        # Find user in MongoDB
        user = users.find_one({"email": email})
        if user and check_password(password, user["password"]):
            session_token = secrets.token_hex(32)  # Generate a session token
            session_data = {
                "user_id": str(user["_id"]),
                "email": email,
                "session_token": session_token,
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=1)
            }
            sessions.insert_one(session_data)

            response = redirect("index")

            print("✅ Session Created:", session_data)
            print("✅ Setting Cookie:", session_token)

            response.set_cookie(
                "session_token",
                session_token,
                httponly=True,
                secure=False,  # Use True for HTTPS
                samesite="Lax",
                max_age=3600
            )
            response = redirect("index")
            response.set_cookie("session_token", session_token, httponly=True, max_age=3600)
            
            # Store username in Django session as well for easy access
            request.session['username'] = email
            request.session['name'] = user.get("name", "")
            return response  
        else:
            print("❌ Invalid Login Attempt")
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")

# 🔹 Index View (Uses Custom Authentication)
@custom_login_required
def index(request):
    first_name = request.session.get('name', '').split()[0]
    return render(request, "index.html", {"username": first_name})

# 🔹 Logout View
def logout_view(request):
    session_token = request.COOKIES.get("session_token")
    if session_token:
        sessions.delete_one({"session_token": session_token})  # Remove from MongoDB

    response = redirect("login")
    response.delete_cookie("session_token")  # Remove cookie
    return response





# def login_view(request):
#     if request.method == "POST":
#         email = request.POST["email"]
#         password = request.POST["password"]

#         user = authenticate(request, username=email, password=password)  # Use authenticate properly
#         if user is not None:
#             login(request, user)  # Pass both `request` and `user`
#             request.session["user_name"] = user.first_name  # Store user's first name
#             messages.success(request, "✅ Login successful!")
#             return redirect("index")  # Redirect to the homepage after login
#         else:
#             messages.error(request, "❌ Invalid email or password!")

#     return render(request, "login.html")



def take_attendance(request):
    first_name = request.session.get('name', '').split()[0]
    return render(request, 'attendance.html', {"username": first_name})  # Renders the attendance form page

def select_subject(request):
    """First Page - Select Subject, Year, and Date"""
    if request.method == "POST":
        year = request.POST.get("year")
        subject = request.POST.get("subject")
        date = request.POST.get("date", datetime.today().strftime('%Y-%m-%d'))

        # Redirect to the attendance marking page with selected values
        return redirect(f"/mark-attendance/?year={year}&subject={subject}&date={date}")

    return render(request, "select_subject.html")






from django.shortcuts import render
from django.http import HttpResponse
from pymongo import MongoClient


def mark_attendance(request):
    if request.method == "POST":
        year = request.POST.get("year")
        subject = request.POST.get("subject")
        date = request.POST.get("date")
    else:
        year = request.GET.get("year")
        subject = request.GET.get("subject")
        date = request.GET.get("date")

    if not year or not subject or not date:
        return HttpResponse("⚠️ Missing required parameters!", status=400)

    # Convert year for MongoDB
    year_map = {
        "1st Year": "1",
        "2nd Year": "2",
        "3rd Year": "3",
        "4th Year": "4",
    }
    year = year_map.get(year, year)  # Default to same year if not found

    # Fetch students from MongoDB (Use PyMongo, not Django ORM)
    students_collection = db[f"student_it_2nd_year"]  # Collection name based on year
    students = list(students_collection.find({}, {"_id": 0}))  # Exclude MongoDB _id field

    print(f"📌 Found Students: {students}")  # Debugging
    first_name = request.session.get('name', '').split()[0]
    return render(request, "mark_attendance.html", {
        "students": students,
        "subject": subject,
        "date": date,
        "year": year,
        "show_loader": True,  # Optional: Show loading spinner
        "username": first_name
    })



from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from datetime import datetime
import urllib.parse


@csrf_exempt
def submit_attendance(request):
    if request.method == "POST":
        try:
            subject = request.POST.get("subject", "").strip()
            date = request.POST.get("date", "").strip()
            present_students = request.POST.getlist("present_students")

            if not subject:
                return HttpResponse("⚠️ Subject is missing!", status=400)
            if not date:
                return HttpResponse("⚠️ Date is missing!", status=400)

            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m")

            # Fetch all students from DB
            all_students = list(students_collection.find({}, {"_id": 1, "roll_number": 1}))
            if not all_students:
                return HttpResponse("🚫 No students found!", status=400)

            # ✅ Update attendance for each student
            for student in all_students:
                roll_number = str(student.get("roll_number", ""))
                status = "P" if roll_number in present_students else "A"

                update_path = f"attendance.{subject}.{formatted_date}"
                if ".." in update_path:
                    return HttpResponse(f"❌ Error: Invalid update path '{update_path}'", status=400)

                # 🔹 Use `$set` instead of `$push` (as per new PyMongo best practices)
                students_collection.update_one(
                    {"_id": student["_id"]},
                    {"$push": {update_path: status}}
                )

            return render(request, "index.html", {"show_loader": True})  # Show loader after update
        except Exception as e:
            return HttpResponse(f"❌ Error: {e}", status=500)

    return HttpResponse("🚫 Invalid request to submit attendance", status=400)

#all ok till now




from django.shortcuts import render
from pymongo import MongoClient
from collections import defaultdict


# Connect to MongoDB
@custom_login_required
def attendance_view(request):
      # Change dynamically if needed
    attendance_records = list(students_collection.find({}))
    # views.py
    all_subjects = ['MATH', 'CA', 'AUTOMATA']
    
    subject = request.GET.get('subject')
    # ... rest of your view logic ...
    students = []
    all_dates = set()

    for record in attendance_records:

        student_attendance = record.get("attendance", {}).get(subject, {})

        # Collect all unique dates
        all_dates.update(student_attendance.keys())

        # Process attendance with default "A" for missing dates
        attendance_data = {
            date: student_attendance.get(date, "A") for date in all_dates
        }

        # Count total "P" occurrences (handling arrays)
        total_present = sum(
            sum(1 for status in (value if isinstance(value, list) else [value]) if status == "P")
            for value in student_attendance.values()
        )

        students.append({
            "all_subjects": all_subjects,
            "name": record.get("name","Unknown"),
            "roll_number": record.get("roll_number", "Unknown"),
            "year": record.get("year", "Unknown"),
            "attendance": attendance_data,  # Processed dictionary
            "total_present": total_present,  # Corrected count
        })

    sorted_dates = sorted(all_dates, key=lambda date: datetime.strptime(date, "%d-%m"))
    first_name = request.session.get('name', '').split()[0]
    return render(
        request,
        "attendance_view.html",
        {
            "username": first_name,
            "all_subjects": all_subjects,
            "attendance_data": students,
            "dates": sorted_dates,
            "subject": subject
        },
    )


# #########################################################################

def parse_date(date_str):
    """Convert string date (YYYY-MM-DD) to a datetime.date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None



#@login_required(login_url="login")
from django.shortcuts import render
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from pymongo import MongoClient
from datetime import datetime
import urllib.parse

# def view_analytics(request):
#     student_name = request.GET.get('student_name', '').strip()
#     start_date = request.GET.get('start_date', '').strip()
#     end_date = request.GET.get('end_date', '').strip()
#     subject_filter = request.GET.get('subject', '').strip()

#     # Convert start_date and end_date from string to date
#     start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
#     end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

#     # 🔹 Fetch students from MongoDB
#     query = {}
#     if student_name:
#         query["name"] = {"$regex": student_name, "$options": "i"}  # Case-insensitive search

#     students = list(students_collection.find(query, {"_id": 0, "name": 1, "roll_number": 1, "attendance": 1}))

#     processed_students = []

#     for student in students:
#         attendance_records = []

#         # Extract attendance data from MongoDB
#         if isinstance(student.get("attendance"), dict):
#             for subject, attendance in student["attendance"].items():
#                 if isinstance(attendance, dict):  # Ensure it's a dictionary
#                     for date_str, statuses in attendance.items():
#                         try:
#                             # Convert "26-03" to "YYYY-MM-DD" dynamically
#                             current_year = datetime.now().year
#                             formatted_date_str = f"{current_year}-{date_str[-2:]}-{date_str[:2]}"
#                             parsed_date = parse_date(formatted_date_str)

#                             # Ensure statuses are always a list (to handle multiple entries)
#                             if isinstance(statuses, str):
#                                 statuses = [statuses]  # Convert single value to list

#                             for status in statuses:
#                                 attendance_records.append({
#                                     "date": parsed_date,
#                                     "subject": subject,
#                                     "status": status
#                                 })
#                         except ValueError:
#                             continue  # Skip if date format is incorrect

#         # Filter attendance by date range
#         filtered_attendance = [
#             a for a in attendance_records
#             if a["date"] and (start_date is None or start_date <= a["date"] <= end_date)
#         ]

#         # Apply subject filter if needed
#         if subject_filter:
#             filtered_attendance = [a for a in filtered_attendance if a["subject"] == subject_filter]

#         # Count attendance
#         total_classes = len(filtered_attendance)
#         attended_classes = sum(1 for a in filtered_attendance if a["status"] == "P")

#         # Calculate attendance percentage
#         attendance_percentage = (attended_classes / total_classes) * 100 if total_classes > 0 else 0

#         # Color coding
#         color_class = "green" if attendance_percentage >= 75 else "orange" if attendance_percentage >= 50 else "red"

#         # Track absent dates
#         absent_dates = [a["date"] for a in filtered_attendance if a["status"] == "A"]
#         first_name = request.session.get('name', '').split()[0]
#         processed_students.append({
#             "name": student.get("name"),
#             "roll_number": student.get("roll_number"),
#             "attendance": f"{attended_classes} / {total_classes}",
#             "percentage": f"{attendance_percentage:.2f}%",
#             "color": color_class,
#             "absent_dates": absent_dates,
#         })

#     return render(request, 'analytics.html', {"students": processed_students, "username": first_name})

from datetime import datetime, date

from datetime import datetime, date
from django.contrib import messages

@custom_login_required
def view_analytics(request):
    # Get all filter parameters
    student_name = request.GET.get('student_name', '').strip()
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    subject_filter = request.GET.get('subject', '')
    min_percentage_str = request.GET.get('min_percentage', '')

    # Initialize filter variables
    start_date = None
    end_date = None
    min_percentage = 0

    # Parse dates
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
    
    # Parse minimum percentage
    try:
        min_percentage = float(min_percentage_str) if min_percentage_str else 0
    except ValueError:
        messages.error(request, "Invalid percentage value.")
        min_percentage = 0

    # Build MongoDB query
    query = {}
    if student_name:
        query["name"] = {"$regex": student_name, "$options": "i"}  # Case-insensitive search

    # Fetch students with filters
    students_data = list(students_collection.find(query, {"_id": 0, "name": 1, "roll_number": 1, "attendance": 1}))
    processed_students = []

    for student in students_data:
        subject_stats = {}
        absent_dates = []

        # Initialize only the filtered subject or all subjects if none selected
        subjects_to_check = [subject_filter] if subject_filter else ["MATH", "CA", "AUTOMATA"]
        
        for subject in subjects_to_check:
            subject_stats[subject] = {"present": 0, "total": 0}

        if isinstance(student.get("attendance"), dict):
            for subject, attendance in student["attendance"].items():
                # Skip if we're filtering by subject and this isn't it
                if subject_filter and subject != subject_filter:
                    continue
                    
                if isinstance(attendance, dict):
                    for date_str, statuses in attendance.items():
                        try:
                            # Parse date from format "dd-mm" to date object
                            day, month = map(int, date_str.split('-'))
                            current_year = datetime.now().year
                            parsed_date = date(current_year, month, day)

                            # Apply date filter
                            if start_date and parsed_date < start_date:
                                continue
                            if end_date and parsed_date > end_date:
                                continue

                            # Process attendance statuses
                            if isinstance(statuses, str):
                                statuses = [statuses]

                            for status in statuses:
                                if subject not in subject_stats:
                                    subject_stats[subject] = {"present": 0, "total": 0}
                                subject_stats[subject]["total"] += 1
                                if status == "P":
                                    subject_stats[subject]["present"] += 1
                                else:
                                    absent_dates.append(parsed_date.strftime("%Y-%m-%d"))
                        except (ValueError, IndexError):
                            continue

        # Calculate percentages only for relevant subjects
        percentages = {}
        for subject in subjects_to_check:
            stats = subject_stats.get(subject, {"present": 0, "total": 0})
            percentages[subject] = (stats["present"] / stats["total"] * 100) if stats["total"] > 0 else 0
        
        # Calculate overall percentage
        total_classes = sum(stats["total"] for stats in subject_stats.values())
        attended_classes = sum(stats["present"] for stats in subject_stats.values())
        overall_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0

        # Apply minimum percentage filter
        if overall_percentage < min_percentage:
            continue

        # Prepare student data - only include filtered subject if specified
        student_data = {
            "name": student.get("name", "Unknown"),
            "roll_number": student.get("roll_number", "Unknown"),
            "overall_percentage": overall_percentage,
            "absent_dates": absent_dates
        }

        # Add subject percentages
        if subject_filter:
            student_data["filtered_subject_percentage"] = percentages.get(subject_filter, 0)
        else:
            for subject in ["MATH", "CA", "AUTOMATA"]:
                student_data[f"{subject.lower()}_percentage"] = percentages.get(subject, 0)

        processed_students.append(student_data)

    return render(request, 'analytics.html', {
        "students": processed_students,
        "username": request.session.get('name', '').split()[0],
        "subject_filter": subject_filter,
        "filters": {
            "student_name": student_name,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "min_percentage": min_percentage_str
        }
    })


def update_data(request):
    pass
