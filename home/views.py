from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from datetime import datetime, date, timedelta
from .models import Student, Attendance, CustomUser, PasswordResetRequest

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.conf import settings
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from django.urls import reverse

from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import quote_plus
import urllib.parse
import secrets
import pymongo
from functools import wraps

from datetime import datetime, timezone


from .mongo_utils import get_db_connection, get_all_student_collections, create_new_collection

username = quote_plus("it24akashmondal")
password = quote_plus("akashmondal@2004")



client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster007.qhfdiks.mongodb.net/?retryWrites=true&w=majority&appName=Cluster007")
db = client["attender_db"]
students_collection = db["student_it_2nd_year"]  # Collection where student records are stored
users_collection = db["home_user"]
password_reset_collection = db["home_passwordresetrequest"]






users = db["home_user"]
sessions = db.django_session

# 🔹 Custom Authentication Decorator

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

def signup_view(request):
    # Check if an admin already exists
    admin_exists = users_collection.find_one({"role": "admin"})

    if request.method == 'POST':
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not (first_name and last_name and email and password):
            messages.error(request, "⚠️ All fields are required!")
            return redirect("signup")

        # Check if email already exists
        existing_user = users_collection.find_one({"email": email}, {"_id": 1})
        if existing_user:
            messages.error(request, "🚫 Email already registered.")
            return redirect("signup")

        # Hash password
        hashed_password = make_password(password)

        # If no admin exists, create the first admin. Otherwise, create a staff user.
        if not admin_exists:
            role = "admin"
        else:
            role = "staff"

        # Create user data
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": email,
            "password": hashed_password,
            "role": role  # Set role as admin for first user, staff for others
        }

        # Insert user into MongoDB
        users_collection.insert_one(user_data)

        # If admin is created, display appropriate message
        if role == "admin":
            messages.success(request, "✅ Admin created successfully. Please log in.")
        else:
            messages.success(request, "✅ Staff account created successfully. Please log in.")

        return redirect("login")

    return render(request, 'signup.html')


from django.contrib.auth.hashers import check_password

@custom_login_required
def create_staff_view(request):
    # Allow only admins to access this page
    if request.session.get('role') != 'admin':
        messages.error(request, "❌ Only admins can create staff accounts.")
        return redirect("index")

    if request.method == 'POST':
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()
        is_admin = request.POST.get("is_admin") == "on"  # Toggle switch value

        if not (first_name and last_name and email and password):
            messages.error(request, "⚠️ All fields are required!")
            return redirect("create_staff")

        # Check if the email already exists
        existing_user = users_collection.find_one({"email": email}, {"_id": 1})
        if existing_user:
            messages.error(request, "🚫 Email already registered.")
            return redirect("create_staff")

        # Hash the password
        hashed_password = make_password(password)

        # Role assignment based on toggle
        role = "admin" if is_admin else "staff"

        # Create user data
        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "username": email,
            "password": hashed_password,
            "role": role
        }

        # Insert into MongoDB
        users_collection.insert_one(user_data)

        messages.success(request, f"✅ {role.capitalize()} account created successfully.")
        return redirect("index")

    return render(request, "create_staff.html")



from django.http import JsonResponse
from bson.regex import Regex

@custom_login_required
def search_users_api(request):
    if request.session.get("role") != "admin":
        return JsonResponse([], safe=False)

    query = request.GET.get("q", "").strip().lower()
    if not query:
        return JsonResponse([], safe=False)

    regex = Regex(f".*{query}.*", "i")  # case-insensitive match
    users = users_collection.find(
        {"$or": [
            {"first_name": regex},
            {"last_name": regex}
        ]},
        {"first_name": 1, "last_name": 1, "email": 1, "role": 1}
    )

    results = [{
        "label": f"{user['first_name']} {user['last_name']} ({user['role']})",
        "email": user["email"]
    } for user in users]

    return JsonResponse(results, safe=False)




@custom_login_required
def delete_user_view(request):
    # Only admins can delete users
    if request.session.get('role') != 'admin':
        messages.error(request, "❌ Only admins can delete users.")
        return redirect("index")

    if request.method == 'POST':
        email_to_delete = request.POST.get('email')

        if not email_to_delete:
            messages.error(request, "⚠️ No user selected.")
            return redirect("delete_user")

        # Don't allow deleting yourself
        if email_to_delete == request.session.get('email'):
            messages.error(request, "🚫 You cannot delete your own account.")
            return redirect("delete_user")

        result = users_collection.delete_one({"email": email_to_delete})

        if result.deleted_count == 1:
            messages.success(request, f"✅ User '{email_to_delete}' deleted successfully.")
        else:
            messages.error(request, "❌ User not found or already deleted.")

        return redirect("index")

    # GET request: Fetch all staff/admin users (excluding yourself)
    users = list(users_collection.find(
        {"role": {"$in": ["admin", "staff"]}, "email": {"$ne": request.session.get("email")}},
        {"first_name": 1, "last_name": 1, "email": 1, "role": 1, "_id": 0}
    ))

    return render(request, "delete_user.html", {"users": users})


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



def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        user_data = users_collection.find_one({"email": email})

        if user_data:
            token = get_random_string(32)
            password_reset_collection.insert_one({"email": email, "token": token})

            reset_link = f"https://attender-auwz.onrender.com/reset-password/{token}/"


            # ✅ Send the reset email
            send_mail(
                subject="Password Reset Request",
                message=f"Click the link below to reset your password:\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "Reset link sent to your email.")
        else:
            messages.error(request, "Email not found.")

    return render(request, 'login.html')




def reset_password_view(request, token):
    # Check token in DB
    token_data = password_reset_collection.find_one({"token": token})
    
    if not token_data:
        return render(request, 'reset_password.html', {"error": "Invalid or expired link"})

    if request.method == 'POST':
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            return render(request, 'reset_password.html', {"error": "Passwords do not match."})

        # Hash and update password
        hashed_pw = make_password(new_password)
        users_collection.update_one(
            {"email": token_data["email"]},
            {"$set": {"password": hashed_pw}}
        )

        # Delete used token
        password_reset_collection.delete_one({"token": token})
        messages.success(request, "Password reset successfully. Please login.")
        return redirect("login")

    return render(request, "reset_password.html", {"token": token})










# 🔹 Login View
# def login_view(request):
#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")
#         #request.session['role'] = user.get("role", "staff")


#         print("🔍 Full Form Data:", request.POST.dict())  # Debugging

#         # Find user in MongoDB
#         user = users.find_one({"$or": [{"email": email}, {"username": email}]})

#         if user and check_password(password, user["password"]):
#             session_token = secrets.token_hex(32)  # Generate a session token
#             session_data = {
#                 "user_id": str(user["_id"]),
#                 "email": email,
#                 "session_token": session_token,
#                 "created_at": datetime.now(timezone.utc),
#                 "expires_at": datetime.now(timezone.utc) + timedelta(hours=1)
#             }
#             if user and user.role == 'admin':
#                 request.session['role'] = 'admin'
#             else:
#                 request.session['role'] = 'staff'
#             sessions.insert_one(session_data)

#             response = redirect("index")

#             print("✅ Session Created:", session_data)
#             print("✅ Setting Cookie:", session_token)

#             response.set_cookie(
#                 "session_token",
#                 session_token,
#                 httponly=True,
#                 secure=False,  # Use True for HTTPS
#                 samesite="Lax",
#                 max_age=3600
#             )
#             response = redirect("index")
#             response.set_cookie("session_token", session_token, httponly=True, max_age=3600)
            
#             # Store username in Django session as well for easy access
#             request.session['username'] = email
#             request.session['name'] = user.get("name", "")
#             return response  
#         else:
#             print("❌ Invalid Login Attempt")
#             return render(request, "login.html", {"error": "Invalid credentials"})

#     return render(request, "login.html")
from django.contrib.auth.hashers import check_password
from datetime import datetime, timedelta, timezone
import secrets

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        print("🔍 Full Form Data:", request.POST.dict())  # Debugging

        # Find user in MongoDB
        user = users.find_one({"$or": [{"email": email}, {"username": email},]})

        if user and check_password(password, user["password"]):  # Correct password comparison
            session_token = secrets.token_hex(32)  # Generate a session token
            session_data = {
                "user_id": str(user["_id"]),
                "email": email,
                "session_token": session_token,
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc) + timedelta(hours=1)
            }
            # Set the role of the user in the session
            if user.get("role") == 'admin':
                request.session['role'] = 'admin'
            else:
                request.session['role'] = 'staff'
            
            # Store session data in MongoDB
            sessions.insert_one(session_data)

            # Prepare response and set session cookie
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

            # Store username in Django session for easy access
            request.session['username'] = email
            request.session['first_name'] = user.get("first_name", "")

            return response  
        else:
            print("❌ Invalid Login Attempt")
            return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")


# 🔹 Index View (Uses Custom Authentication)
@custom_login_required
def index(request):
    name = request.session.get('first_name', '').split()
    if len(name) > 0:
        first_name = name[0]
    else:
        first_name = "Guest"
    return render(request, "index.html", {"username": first_name})

# 🔹 Logout View
def logout_view(request):
    session_token = request.COOKIES.get("session_token")
    if session_token:
        sessions.delete_one({"session_token": session_token})  # Remove from MongoDB

    response = redirect("login")
    response.delete_cookie("session_token")  # Remove cookie
    response["Location"] += "?refresh=true"
     # Add a no-cache header to prevent caching of the index page
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, proxy-revalidate"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@custom_login_required
def take_attendance(request):
    name = request.session.get('first_name', '').split()
    first_name = name[0] if len(name) > 0 else "Guest"

    # Get all student collections
    collections = [col for col in db.list_collection_names() if col.startswith('student_it_')]

    semesters = []
    academic_years = []

    for col in collections:
        parts = col.split("_")
        if len(parts) >= 4:
            sem_part = parts[2]
            year_part = parts[3]

            if "sem" in sem_part:
                semesters.append(sem_part.replace("sem", ""))
            if "-" in year_part:
                academic_years.append(year_part)

    semesters = sorted(list(set(semesters)))
    academic_years = sorted(list(set(academic_years)))

    # GET: show attendance.html
    selected_sem = request.GET.get("sem")
    selected_year = request.GET.get("year")
    subject_list = []

    if selected_sem and selected_year:
        collection_name = f"student_it_{selected_sem}sem_{selected_year}"
        if collection_name in collections:
            pipeline = [
                {"$project": {"subjects": {"$objectToArray": "$subjects"}}},
                {"$unwind": "$subjects"},
                {"$group": {"_id": None, "subjects": {"$addToSet": "$subjects.k"}}}
            ]
            result = db[collection_name].aggregate(pipeline)
            try:
                subject_list = list(result)[0]['subjects']
            except (IndexError, KeyError):
                pass

    if request.method == "POST":
        sem = request.POST.get("sem")
        year = request.POST.get("year")
        subject = request.POST.get("subject")
        date = request.POST.get("date")

        if sem and year and subject and date:
            collection = f"student_it_{sem}sem_{year}"
            return redirect(f'/mark-attendance/?collection={collection}&subject={subject}&date={date}')
        
        else:
            messages.error(request, "Please fill all required fields")
    overwrite = request.POST.get("overwrite", "off")


    return render(request, 'attendance.html', {
        "username": first_name,
        "collections": collections,
        "today": datetime.today().strftime('%Y-%m-%d'),
        "subjects": sorted(subject_list),
        "semesters": semesters,
        "years": academic_years,
        "semester": selected_sem,
        "year": selected_year,
    })

@custom_login_required
def mark_attendance(request):
    if request.method == "POST":
        # Saving attendance logic
        collection_name = request.POST.get("collection")
        subject = request.POST.get("subject")
        date = request.POST.get("date")
        overwrite = request.POST.get("overwrite", "off")  # Get overwrite value

        all_students = request.POST.getlist("all_students")
        present_students = request.POST.getlist("present_students")

        print('all_students:', all_students, 'present_students:', present_students,
              'collection_name:', collection_name, 'subject:', subject,
              'date:', date, 'overwrite:', overwrite, 'request.POST:', request.POST)

        if not (collection_name and subject and date and all_students):
            return HttpResponse("Missing required fields in POST request!", status=400)

        try:
            students_collection = db[collection_name]

            for roll in all_students:
                status = "P" if roll in present_students else "A"

                update_query = (
                    {"$set": {f"subjects.{subject}.{date}": [status]}} if overwrite == "on"
                    else {"$push": {f"subjects.{subject}.{date}": status}}
                )

                students_collection.update_one(
                    {"roll_number": roll},
                    update_query
                )

            messages.success(request, "Attendance saved successfully!")
            return redirect("index")

        except Exception as e:
            return HttpResponse(f"Error saving attendance: {str(e)}", status=500)

    elif request.method == "GET":
        # Loading the form to mark attendance
        overwrite = request.GET.get("overwrite", "off")

        collection_name = request.GET.get("collection")
        subject = request.GET.get("subject")
        date = request.GET.get("date")
        if not (collection_name and subject and date):
            return HttpResponse("Missing required parameters!", status=400)

        try:
            students_collection = db[collection_name]
            students = list(students_collection.find({}, {"_id": 0}))

            available_subjects = []
            if students:
                available_subjects = list(students[0].get('subjects', {}).keys())

        except Exception as e:
            return HttpResponse(f"Error fetching students: {str(e)}", status=500)

        name = request.session.get('first_name', '').split()
        first_name = name[0] if len(name) > 0 else "Guest"

        return render(request, "mark_attendance.html", {
            "students": students,
            "subject": subject,
            "date": date,
            "collection": collection_name,
            "available_subjects": available_subjects,
            "username": first_name,
            "overwrite": overwrite  # Pass to template if needed
        })










# # Connect to MongoDB
# @custom_login_required
# def attendance_view(request):
#       # Change dynamically if needed
#     attendance_records = list(students_collection.find({}))
#     # views.py
#     all_subjects = ['MATH', 'CA', 'AUTOMATA']
    
#     subject = request.GET.get('subject')
#     # ... rest of your view logic ...
#     students = []
#     all_dates = set()

#     for record in attendance_records:

#         student_attendance = record.get("attendance", {}).get(subject, {})

#         # Collect all unique dates
#         all_dates.update(student_attendance.keys())

#         # Process attendance with default "A" for missing dates
#         attendance_data = {
#             date: student_attendance.get(date, "A") for date in all_dates
#         }

#         # Count total "P" occurrences (handling arrays)
#         total_present = sum(
#             sum(1 for status in (value if isinstance(value, list) else [value]) if status == "P")
#             for value in student_attendance.values()
#         )

#         students.append({
#             "all_subjects": all_subjects,
#             "name": record.get("name","Unknown"),
#             "roll_number": record.get("roll_number", "Unknown"),
#             "year": record.get("year", "Unknown"),
#             "attendance": attendance_data,  # Processed dictionary
#             "total_present": total_present,  # Corrected count
#         })

#     sorted_dates = sorted(all_dates, key=lambda date: datetime.strptime(date, "%d-%m"))
#     name = request.session.get('name', '').split()
#     if len(name) > 0:
#         first_name = name[0]
#     else:
#         first_name = "Guest"
#     return render(
#         request,
#         "attendance_view.html",
#         {
#             "username": first_name,
#             "all_subjects": all_subjects,
#             "attendance_data": students,
#             "dates": sorted_dates,
#             "subject": subject
#         },
#     )


# #########################################################################

def parse_date(date_str):
    """Convert string date (YYYY-MM-DD) to a datetime.date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None




from datetime import datetime, date

from .mongo_utils import get_db_connection, get_all_student_collections


@custom_login_required
def view_analytics(request):
    collections = [col for col in db.list_collection_names() if col.startswith('student_it_')]

    # Get filter parameters
    student_name = request.GET.get("student_name", "").strip()
    subject_filter = request.GET.get("subject", "").strip()
    start_date_str = request.GET.get("start_date", "")
    end_date_str = request.GET.get("end_date", "")
    min_percentage_str = request.GET.get("min_percentage", "0").strip()
    selected_collection = request.GET.get("collection", "")

    # Convert dates
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None
    except ValueError:
        start_date, end_date = None, None
        
    min_percentage = float(min_percentage_str) if min_percentage_str else 0

    processed_students = []
    subject_list = []

    if selected_collection and selected_collection in collections:
        students_collection = db[selected_collection]

        # Dynamically get subject list
        try:
            pipeline = [
                {"$project": {"subjects": {"$objectToArray": "$subjects"}}},
                {"$unwind": "$subjects"},
                {"$group": {"_id": None, "subjects": {"$addToSet": "$subjects.k"}}}
            ]
            result = list(students_collection.aggregate(pipeline))
            subject_list = result[0]['subjects'] if result else []
        except Exception as e:
            print("DEBUG >> Subject extraction error:", e)
            subject_list = []

        # Build student query
        query = {}
        if student_name:
            query["name"] = {"$regex": student_name, "$options": "i"}

        students_data = list(students_collection.find(query, {
            "_id": 0, "name": 1, "roll_number": 1, "subjects": 1
        }))

        for student in students_data:
            subject_stats = {}
            absent_dates = []
            subjects_to_check = [subject_filter] if subject_filter else subject_list

            for subject in subjects_to_check:
                subject_stats[subject] = {"present": 0, "total": 0}

            if isinstance(student.get("subjects"), dict):
                for subject in subjects_to_check:
                    subject_data = student["subjects"].get(subject, {})
                    
                    # Handle both direct dates and nested attendance objects
                    attendance_records = {}
                    if isinstance(subject_data, dict):
                        attendance_records = subject_data
                    elif isinstance(subject_data.get("attendance"), dict):
                        attendance_records = subject_data["attendance"]
                    
                    for date_str, status in attendance_records.items():
                        try:
                            # Parse date in YYYY-MM-DD format
                            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                            
                            if start_date and parsed_date < start_date:
                                continue
                            if end_date and parsed_date > end_date:
                                continue
                            
                            # Handle different status formats
                            statuses = []
                            if isinstance(status, str):
                                statuses = [status]
                            elif isinstance(status, list):
                                statuses = status
                            
                            for s in statuses:
                                if subject not in subject_stats:
                                    subject_stats[subject] = {"present": 0, "total": 0}
                                subject_stats[subject]["total"] += 1
                                if s == "P":
                                    subject_stats[subject]["present"] += 1
                                else:
                                    absent_dates.append(date_str)  # Store original date string
                        except (ValueError, AttributeError):
                            continue

            # Calculate percentages
            percentages = {}
            for subject in subjects_to_check:
                stats = subject_stats.get(subject, {"present": 0, "total": 0})
                percentages[subject] = round((stats["present"] / stats["total"] * 100) if stats["total"] > 0 else 0, 2)

            total_classes = sum(stats["total"] for stats in subject_stats.values())
            attended_classes = sum(stats["present"] for stats in subject_stats.values())
            overall_percentage = round((attended_classes / total_classes * 100) if total_classes > 0 else 0, 2)

            if overall_percentage < min_percentage:
                continue

            # Prepare student record
            student_data = {
                "name": student.get("name", "Unknown"),
                "roll_number": student.get("roll_number", "Unknown"),
                "overall_percentage": overall_percentage,
                "absent_dates": list(set(absent_dates)) or ["No absences"],
            }

            if subject_filter:
                student_data["filtered_subject_percentage"] = percentages.get(subject_filter, 0)
            else:
                student_data["subject_percentages_flat"] = [
                    {"name": subject, "percent": percentages.get(subject, 0)}
                    for subject in subject_list
                ]

            processed_students.append(student_data)

    # Get session name for greeting
    name = request.session.get('first_name', '').split()
    first_name = name[0] if name else "Guest"

    return render(request, 'analytics.html', {
        "students": processed_students,
        "username": first_name,
        "subject_filter": subject_filter,
        "collections": collections,
        "selected_collection": selected_collection,
        "subject_list": subject_list,
        "filters": {
            "student_name": student_name,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "min_percentage": min_percentage_str
        }
    })


@custom_login_required
def promotion_dashboard(request):
    try:
        
        collections = get_all_student_collections(db)
        
        if request.method == 'POST':
            source_collection = request.POST.get('source_collection')
            target_semester = request.POST.get('target_semester')
            academic_year = request.POST.get('academic_year')
            num_subjects = int(request.POST.get('num_subjects', 0))
            
            if not all([source_collection, target_semester, academic_year, num_subjects > 0]):
                messages.error(request, "Please fill all required fields")
                return redirect('promotion_dashboard')
            
            subjects = []
            for i in range(1, num_subjects + 1):
                subject = request.POST.get(f'subject_{i}')
                if subject:
                    subjects.append(subject.strip())
            
            if not subjects:
                messages.error(request, "Please enter at least one subject")
                return redirect('promotion_dashboard')
            
            new_collection_name = f"student_it_{target_semester}sem_{academic_year}"
            
            try:
                student_count = create_new_collection(
                    db=db,
                    source_collection=source_collection,
                    new_collection_name=new_collection_name,
                    subjects=subjects
                )
                messages.success(request, f"Successfully promoted {student_count} students to {new_collection_name}")
                return render(request, 'promotion_success.html', {
                    'student_count': student_count,
                    'new_collection': new_collection_name
                })
            
            except Exception as e:
                messages.error(request, f"Promotion failed: {str(e)}")
                return redirect('promotion_dashboard')
        
        return render(request, 'promotion_form.html', {
            'collections': collections,
            'current_year': datetime.now().year
        })
    
    except Exception as e:
        messages.error(request, f"System error: {str(e)}")
        return render(request, 'error.html')
@custom_login_required
def update_options(request):
    return render(request, 'update.html')



def staff_list_view(request):
    return render(request, 'update_staff.html')


@custom_login_required
def delete_collections(request):
    if request.method == "POST":
        academic_year = request.POST.get("academic_year")

        if not academic_year:
            messages.error(request, "Please provide an academic year.")
            return redirect('delete_collections')

        
        deleted = []

        # Get all collection names and filter those ending with the academic year
        for collection_name in db.list_collection_names():
            if collection_name.endswith(academic_year):
                db.drop_collection(collection_name)
                deleted.append(collection_name)

        if deleted:
            messages.success(request, f"Deleted collections: {', '.join(deleted)}")
        else:
            messages.info(request, "No collections matched the academic year.")
        return redirect("update_options")

    return render(request, "delete_collections.html")

from django.core.files.storage import default_storage
import os
import pandas as pd
@custom_login_required
def import_collection(request):
    message = ""
    if request.method == "POST":
        dept = request.POST.get("department")
        semester = request.POST.get("semester")
        academic_year = request.POST.get("academic_year")

        # Collect all subjects from dynamically generated fields
        subject_names = []
        for key in request.POST:
            if key.startswith("subject_") and request.POST[key].strip():
                subject_names.append(request.POST[key].strip())

        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            file_path = default_storage.save(uploaded_file.name, uploaded_file)
            abs_path = os.path.join(default_storage.location, file_path)

            ext = os.path.splitext(file_path)[-1].lower()
            df = pd.read_excel(abs_path) if ext == ".xlsx" else pd.read_csv(abs_path)

            collection_name = f"student_{dept}_{semester}_{academic_year}".lower()
            student_collection = db[collection_name]

            documents = []
            for _, row in df.iterrows():
                # Create a dictionary of subjects, each initialized as an empty dict
                subject_data = {subject: {} for subject in subject_names}

                doc = {
                    "name": str(row["name"]),
                    "roll_number": str(row["roll_number"]),
                    "current_semester": semester,
                    "academic_year": academic_year,
                    "subjects": subject_data
                }
                documents.append(doc)

            student_collection.insert_many(documents)
            messages.success(request, "Collection imported successfully!")
            return redirect("index")

    return render(request, "import_collection.html", {"message": message})
@custom_login_required
def export_collection_page(request):
    years = ["2023-2024", "2024-2025", "2025-2026"]
    semesters = [1, 2, 3, 4, 5, 6]
    today = datetime.date.today().isoformat()
    return render(request, "export_collection.html", {
        "years": years,
        "semesters": semesters,
        "today": today
    })

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient
import pandas as pd
import io
def get_semester_with_suffix(sem):
    suffixes = {'1': '1st', '2': '2nd', '3': '3rd'}
    return suffixes.get(sem, f"{sem}th")

@custom_login_required
def export_collection(request):
    departments = ['it']
    semesters = ['1', '2', '3', '4', '5', '6', '7', '8']

    years = []
    collections = db.list_collection_names()
    for col in collections:
        if col.startswith("student_"):
            parts = col.split('_')
            if len(parts) >= 4:
                years.append(parts[3])
    years = sorted(set(years), reverse=True)

    selected_dept = request.GET.get('dept') or request.POST.get('dept')
    selected_sem = request.GET.get('sem') or request.POST.get('sem')
    selected_year = request.GET.get('year') or request.POST.get('year')

    subjects = []
    if selected_dept and selected_sem and selected_year:
        sem_with_suffix = get_semester_with_suffix(selected_sem)
        collection_name = f"student_{selected_dept}_{sem_with_suffix}sem_{selected_year}"
        if collection_name in collections:
            try:
                sample_doc = db[collection_name].find_one()
                if sample_doc:
                    subjects = list(sample_doc.get("subjects", {}).keys())
            except Exception as e:
                print("Error reading subject keys:", e)

    if request.method == "POST":
        subject = request.POST.get("subject")
        export_type = request.POST.get("export_type")

        if not all([selected_dept, selected_sem, selected_year, subject, export_type]):
            return HttpResponse("Missing required fields", status=400)

        sem_with_suffix = get_semester_with_suffix(selected_sem)
        collection_name = f"student_{selected_dept}_{sem_with_suffix}sem_{selected_year}"

        data = []
        all_dates = set()

        for student in db[collection_name].find():
            name = student.get("name")
            roll = student.get("roll_number") or student.get("roll")
            attendance = student.get("subjects", {}).get(subject, {})

            row = {"Name": name, "Roll No": roll}
            for date, status_list in attendance.items():
                value = status_list[0] if isinstance(status_list, list) and status_list else ''
                row[date] = value
                all_dates.add(date)
            data.append(row)

        if not data:
            return HttpResponse("No attendance data found.", status=404)

        # Sort columns: Name, Roll No, Date1, Date2, ...
        all_dates = sorted(all_dates)
        columns = ['Name', 'Roll No'] + all_dates

        df = pd.DataFrame(data)
        df = df.reindex(columns=columns, fill_value='')

        if export_type == "csv":
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{subject}_attendance.csv"'
            df.to_csv(path_or_buf=response, index=False)
            return response
        else:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Attendance')
            buffer.seek(0)
            response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{subject}_attendance.xlsx"'
            return response

    return render(request, 'export_collection.html', {
        "departments": departments,
        "semesters": semesters,
        "years": years,
        "subjects": subjects,
        "selected_dept": selected_dept,
        "selected_sem": selected_sem,
        "selected_year": selected_year
    })
