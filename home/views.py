from django.http import HttpResponse,request
from django.shortcuts import render,redirect
from datetime import datetime
from .models import Student

from datetime import datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
from .models import Student, Attendance
from datetime import datetime
from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt
import pymongo
from urllib.parse import quote_plus
#Connect to MongoDB

username = quote_plus("it24akashmondal")
password = quote_plus("akashmondal@2004")


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



client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster007.oznj7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster007")
db = client["attender_db"]
students_collection = db["student_it_2nd_year"]  # Collection where student records are stored




@csrf_exempt
def submit_attendance(request):
    if request.method == "POST":
        try:
            subject = request.POST.get("subject")  
            date = request.POST.get("date")  
            present_students = request.POST.getlist("present_students")  

            if not subject or not date:
                return HttpResponse("⚠️ Missing required fields!", status=400)

            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m")

            # Fetch all students from DB
            all_students = list(students_collection.find({}, {"_id": 1, "roll_number": 1}))
            if not all_students:
                return HttpResponse("🚫 No students found!", status=400)

            # ✅ Update attendance for each student
            for student in all_students:
                roll_number = str(student.get("roll_number", ""))  
                status = "P" if roll_number in present_students else "A"

                students_collection.update_one(
                    {"_id": student["_id"]},
                    {"$set": {f"attendance.{subject}.{formatted_date}": status}}
                )

            #return HttpResponse("✅ Attendance submitted successfully!")
            return render(request, "index.html", {"show_loader": True})  # Added loader
        except Exception as e:
            return HttpResponse(f"❌ Error: {e}", status=500)

    return HttpResponse("🚫 Invalid request to submit attendance", status=400)





#all ok till now



# def view_attendance(request):
#     students = Student.objects.all()
#     dates = Attendance.objects.values_list("date", flat=True).distinct().order_by("date")
    
#     attendance_records = []
#     for student in students:
#         attendance = {date: Attendance.objects.filter(student=student, date=date, is_present=True).exists() for date in dates}
#         attendance_records.append({
#             "roll_number": student.roll_number,
#             "name": student.name,
#             "attendance": attendance
#         })

#     context = {
#         "attendance_records": attendance_records,
#         "dates": dates
#     }
    
#     return render(request, "view_attendance.html", context)
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

        # Collect all dates
        all_dates.update(student_attendance.keys())

        # Store attendance with default "A" for missing dates
        attendance_data = {date: student_attendance.get(date, "A") for date in all_dates}

        students.append({
            "name": record["name"],
            "roll_number": record["roll_number"],
            "year": record["year"],
            "attendance": attendance_data,  # Processed dictionary
            "total_present": sum(1 for status in student_attendance.values() if status == "P"),
        })

    sorted_dates = sorted(all_dates)  # Sort dates for display

    return render(
        request,
        "attendance_view.html",
        {"attendance_data": students, "dates": sorted_dates, "subject": subject},
    )





# #########################################################################
from datetime import datetime
def parse_date(date_str):
    """Convert string date (YYYY-MM-DD) to a datetime.date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

# def view_analytics(request):
#     students = Student.objects.all()

#     # Get filters from request
#     student_name = request.GET.get('student_name', '').strip()
#     start_date = parse_date(request.GET.get('start_date', ''))
#     end_date = parse_date(request.GET.get('end_date', ''))

#     # Filter by name
#     if student_name:
#         students = students.filter(name__icontains=student_name)

#     # Filter by date range
#     for student in students:
#         student.filtered_attendance = {}
#         for subject, attendance in student.attendance.items():
#             for date, status in attendance.items():
#                 parsed_date = parse_date(date)
#                 if parsed_date and start_date and end_date:
#                     if start_date <= parsed_date <= end_date:
#                         student.filtered_attendance[date] = status
#                 elif not start_date or not end_date:
#                     student.filtered_attendance[date] = status  # If no valid dates, keep all data

#     return render(request, 'analytics.html', {'students': students})

# from django.shortcuts import render
# from django.utils.dateparse import parse_date
# from datetime import datetime
# from .models import Student

# def view_analytics(request):
#     students = Student.objects.all()

#     # Get filters from request
#     student_name = request.GET.get('student_name', '').strip()
#     start_date = parse_date(request.GET.get('start_date', ''))
#     end_date = parse_date(request.GET.get('end_date', ''))

#     # Validate dates
#     if not start_date or not end_date:
#         return render(request, 'analytics.html', {'students': [], 'error': "Invalid date range."})

#     # Filter by name
#     if student_name:
#         students = students.filter(name__icontains=student_name)

#     for student in students:
#         total_classes = 0
#         attended_classes = 0

#         print(f"🔍 {student.name} Attendance Data: {student.attendance}")

#         if isinstance(student.attendance, dict):
#             for subject, attendance in student.attendance.items():
#                 if isinstance(attendance, dict):
#                     for date_str, status in attendance.items():
#                         # Convert "27-03" to "2025-03-27"
#                         formatted_date_str = f"2025-{date_str[-2:]}-{date_str[:2]}"
#                         parsed_date = parse_date(formatted_date_str)

#                         print(f"➡️ Checking {student.name}: {date_str} → {formatted_date_str} → {parsed_date}")

#                         if parsed_date and start_date <= parsed_date <= end_date:
#                             total_classes += 1
#                             if status.lower() == 'p':  # Assuming 'P' means Present
#                                 attended_classes += 1

#         print(f"📊 {student.name} - Total: {total_classes}, Attended: {attended_classes}")

#         student.filtered_attendance = f"{attended_classes} / {total_classes}" if total_classes > 0 else "No records found."

#     return render(request, 'analytics.html', {'students': students})
from django.shortcuts import render
from django.utils.dateparse import parse_date
from datetime import datetime

def view_analytics(request):
    students = Student.objects.all()

    student_name = request.GET.get('student_name', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    subject_filter = request.GET.get('subject', '')

    if student_name:
        students = students.filter(name__icontains=student_name)

    processed_students = []

    # Convert start_date and end_date from string to date (once)
    start_date = datetime.strptime(start_date, r"%Y-%m-%d").date() if start_date else None
    end_date = datetime.strptime(end_date, r"%Y-%m-%d").date() if end_date else None
    print(start_date, end_date)
    for student in students:
        attendance_records = []

        # Process attendance data from MongoDB
        if isinstance(student.attendance, dict):
            for subject, attendance in student.attendance.items():
                if isinstance(attendance, dict):
                    for date_str, status in attendance.items():
                        # Convert "27-03" to "2025-03-27"
                        formatted_date_str = f"2025-{date_str[-2:]}-{date_str[:2]}"
                        parsed_date = parse_date(formatted_date_str)

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
