# 📝 Attender - Smart Attendance Management System


**Attender**, a simple yet powerful attendance management system built with Django and MongoDB. It is designed for educational institutions to manage subject-wise attendance efficiently.

---

## 🚀 Features

- Department, Year, Semester, and Subject-based student management.
- Mark attendance with a clean checkbox/toggle UI.
- Automatically stores attendance with current date and weekday.
- Dynamic subject dropdown and MongoDB integration.
- Export/Import attendance data (Excel/CSV).
- View analytics and date-range reports.
- Single-window application (no popups).

---

## 🛠 Tech Stack

- **Frontend**: HTML, CSS (inline), minimal JavaScript  
- **Backend**: Django 5.1  
- **Database**: MongoDB Atlas (accessed via PyMongo)  
- **Libraries**: pandas, openpyxl (for Excel export/import)

---

## ⚙️ Setup Instructions

1. **Clone the repo:**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd last_days
# 📝 Attender - Smart Attendance Management System

`last_days` is the local working directory for **Attender**, a simple yet powerful attendance management system built with Django and MongoDB. It is designed for educational institutions to manage subject-wise attendance efficiently.

---

## 🚀 Features

- Department, Year, Semester, and Subject-based student management.
- Mark attendance with a clean checkbox/toggle UI.
- Automatically stores attendance with current date and weekday.
- Dynamic subject dropdown and MongoDB integration.
- Export/Import attendance data (Excel/CSV).
- View analytics and date-range reports.
- Single-window application (no popups).

---

## 🛠 Tech Stack

- **Frontend**: HTML, CSS (inline), minimal JavaScript  
- **Backend**: Django 5.1  
- **Database**: MongoDB Atlas (accessed via PyMongo), AWS
- **Libraries**: pandas, openpyxl (for Excel export/import)

---

Create a virtual environment:

python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate



Install dependencies:

pip install -r requirements.txt
Configure MongoDB URI in your settings.py:

python

from pymongo import MongoClient
client = MongoClient("your_mongodb_uri")
db = client["attender_db"]


Run the server:

python manage.py runserver



👨‍💻 Author
Akash
IT Engineering Student, 2023-27 Batch
GitHub: itattender2025
ORIGINAL GITHUB: AKASH-INCODE

