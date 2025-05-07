from django.contrib import admin
from django.urls import path, include
from home import views

urlpatterns = [
    path('', views.index, name='index'),
    path('take-attendance/', views.take_attendance, name='take_attendance'),
    # path('select-subject/', views.select_subject, name='select_subject'),
    path('mark-attendance/', views.mark_attendance, name='mark_attendance'),
    # path('submit-attendance/', views.submit_attendance, name='submit_attendance'),
    path('attendance/', views.attendance_view, name='attendance_view'), 
    path('analytics/', views.view_analytics, name='view_analytics'),
     path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path("forgot-password/", views.forgot_password_view, name="forgot_password"),
    
    path('logout/', views.logout_view, name='logout'),
    path('accounts/', include('allauth.urls')),
    path('promote/', views.promotion_dashboard, name='promotion_dashboard'),
    
    path('update/', views.update_options, name='update_options'),

    # path('update/promote/', views.promote_students, name='promote_students'),
    path('update/delete/', views.delete_collections, name='delete_collections'),
    path('update/import/', views.import_collection, name='import_collection'),
    path('export-collection/', views.export_collection, name='export_collection'),
    # path('get_subjects/', views.get_subjects, name='get_subjects'),
    # path('export-subject-attendance/', views.export_subject_attendance, name='export_subject_attendance'),
    path("reset-password/<str:token>/", views.reset_password_view, name="reset_password"),
    path('create-staff/', views.create_staff_view, name='create_staff'),


    ]