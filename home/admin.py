from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import CustomUser
# Register your models here.

# Custom UserAdmin with conditional logic for superusers and staff
# class CustomUserAdmin(DefaultUserAdmin):
#     # Customize which fields are displayed in the admin form
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
#         ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
#                                     'groups', 'user_permissions')}),
        
#     )
#     list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')

#     # Customize queryset to separate superusers and staff in the admin list view
#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         if request.user.is_superuser:
#             return queryset  # Superusers see all users
#         return queryset.filter(is_superuser=False)  # Staff sees only non-superusers

# # Register the CustomUser model with the custom admin
# admin.site.register(CustomUser, CustomUserAdmin)