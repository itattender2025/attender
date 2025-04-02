from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [
    path('', views.index, name='index'),
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    path('select-subject/', views.select_subject, name='select_subject'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('submit-attendance/', views.submit_attendance, name='submit_attendance'),
    path('attendance/', views.attendance_view, name='attendance_view'), 
    path('analytics/', views.view_analytics, name='view_analytics'),
    
    path("signup/", views.signup, name="signup"),
      path("login/", views.login_view, name="login"),
    path("logout/", views.logout, name="logout"),
    
    # 🔥 New route for manual attendance updates
    #path('manual-attendance/', views.manual_attendance_update, name='manual_attendance_update'),
]