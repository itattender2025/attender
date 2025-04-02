from django.http import HttpResponse,request
from django.shortcuts import render,redirect
from datetime import datetime
from .models import Student,User

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






username = quote_plus("it24akashmondal")
password = quote_plus("akashmondal@2004")



client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster007.oznj7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster007")
db = client["attender_db"]
students_collection = db["student_it_2nd_year"]  # Collection where student records are stored


def index(request):
    return render(request,'index.html')
def take_attendance(request):
    return render(request, 'attendance.html')  # Renders the attendance form page

def select_subject(request):
    """First Page - Select Subject, Year, and Date"""
    if request.method == "POST":
        year = request.POST.get("year")
        subject = request.POST.get("subject")
        date = request.POST.get("date", datetime.today().strftime('%Y-%m-%d'))

        # Redirect to the attendance marking page with selected values
        return redirect(f"/mark-attendance/?year={year}&subject={subject}&date={date}")

    return render(request, "select_subject.html")





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

    # Fetch students from MongoDB
    students = Student.objects.filter(year=str(year))
    print(f"📌 Found Students: {list(students)}")  # Debugging

    return render(request, "mark_attendance.html", {
        "students": students,
        "subject": subject,
        "date": date,
        "year": year,
        "show_loader": True,  # Optional: Show loading spinner
    })




@csrf_exempt
def submit_attendance(request):
    if request.method == "POST":
        try:
            subject = request.POST.get("subject", "").strip()  # Ensure subject is not empty
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

                students_collection.update_one(
                    {"_id": student["_id"]},
                    {"$push": {update_path: status}}  # Use `$push` to append
                )

            return render(request, "index.html", {"show_loader": True})  # Added loader
        except Exception as e:
            return HttpResponse(f"❌ Error: {e}", status=500)

    return HttpResponse("🚫 Invalid request to submit attendance", status=400)

#all ok till now


from django.shortcuts import render
from pymongo import MongoClient
from collections import defaultdict


# Connect to MongoDB
def attendance_view(request):
    subject = "MATH"  # Change dynamically if needed
    attendance_records = list(students_collection.find({}))

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
            "name": record["name"],
            "roll_number": record["roll_number"],
            "year": record["year"],
            "attendance": attendance_data,  # Processed dictionary
            "total_present": total_present,  # Corrected count
        })

    sorted_dates = sorted(all_dates, key=lambda date: datetime.strptime(date, "%d-%m"))

    return render(
        request,
        "attendance_view.html",
        {"attendance_data": students, "dates": sorted_dates, "subject": subject},
    )




# #########################################################################

def parse_date(date_str):
    """Convert string date (YYYY-MM-DD) to a datetime.date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def view_analytics(request):
    students = Student.objects.all()

    student_name = request.GET.get('student_name', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    subject_filter = request.GET.get('subject', '')

    if student_name:
        students = students.filter(name__icontains=student_name)

    # Convert start_date and end_date from string to date
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    processed_students = []

    for student in students:
        attendance_records = []

        # Extract attendance data from MongoDB
        if isinstance(student.attendance, dict):
            for subject, attendance in student.attendance.items():
                if isinstance(attendance, dict):  # Ensure it's a dictionary
                    for date_str, statuses in attendance.items():
                        # Convert "26-03" to "2025-03-26"
                        formatted_date_str = f"2025-{date_str[-2:]}-{date_str[:2]}"
                        parsed_date = parse_date(formatted_date_str)

                        # Ensure statuses are always a list (to handle multiple entries)
                        if isinstance(statuses, str):
                            statuses = [statuses]  # Convert single value to list

                        for status in statuses:
                            attendance_records.append({
                                "date": parsed_date,
                                "subject": subject,
                                "status": status
                            })

        # Filter attendance by date range
        filtered_attendance = [
            a for a in attendance_records
            if a["date"] and (start_date is None or start_date <= a["date"] <= end_date)
        ]

        # Apply subject filter if needed
        if subject_filter:
            filtered_attendance = [a for a in filtered_attendance if a["subject"] == subject_filter]

        # Count attendance
        total_classes = len(filtered_attendance)
        attended_classes = sum(1 for a in filtered_attendance if a["status"] == "P")

        # Calculate attendance percentage
        attendance_percentage = (attended_classes / total_classes) * 100 if total_classes > 0 else 0

        # Color coding
        color_class = "green" if attendance_percentage >= 75 else "orange" if attendance_percentage >= 50 else "red"

        # Track absent dates
        absent_dates = [a["date"] for a in filtered_attendance if a["status"] == "A"]

        processed_students.append({
            "name": student.name,
            "roll_number": student.roll_number,
            "attendance": f"{attended_classes} / {total_classes}",
            "percentage": f"{attendance_percentage:.2f}%",
            "color": color_class,
            "absent_dates": absent_dates,
        })

    return render(request, 'analytics.html', {"students": processed_students})







# #for login and registration

from django.contrib import messages
from django.contrib.auth import logout as django_logout
def signup(request):
    if request.method == "POST":
        name = request.POST["name"]
        email = request.POST["email"]
        password = request.POST["password"]
        
        # 🔹 Check if user already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "⚠️ Email already registered!")
            return redirect("signup")
        
        user = User(name=name, email=email)
        user.set_password(password)  # Hash the password
        user.save()
        
        messages.success(request, "✅ Signup successful! Please login.")
        return redirect("login")
    
    return render(request, "signup.html")


# ✅ LOGIN VIEW
def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                request.session["user_id"] = str(user.id)  # Store user ID in session
                request.session["user_name"] = user.name
                messages.success(request, "✅ Login successful!")
                return redirect("dashboard")  # Redirect to dashboard
            else:
                messages.error(request, "❌ Incorrect password!")
        except User.DoesNotExist:
            messages.error(request, "❌ User not found!")
    
    return render(request, "login.html")


# ✅ LOGOUT VIEW
def logout(request):
    django_logout(request)
    request.session.flush()  # Clear session
    messages.success(request, "✅ You have been logged out!")
    return redirect("login")


def attendance_page(request):
    if "user_id" not in request.session:
        messages.error(request, "⚠️ Please login first!")
        return redirect("login")
    
    # ✅ Your attendance logic here...
    return render(request, "attendance.html", {"user_name": request.session.get("user_name")})
