from django.db import models

# Create your models here.
from djongo import models

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