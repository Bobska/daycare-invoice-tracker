from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser model"""
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    # Add custom fields to the user form
    fieldsets = list(UserAdmin.fieldsets) + [
        ('Additional Info', {
            'fields': ('phone_number', 'notification_preferences')
        }),
    ]
    
    # Add custom fields to the add user form
    add_fieldsets = list(UserAdmin.add_fieldsets) + [
        ('Additional Info', {
            'fields': ('email', 'phone_number')
        }),
    ]


admin.site.register(CustomUser, CustomUserAdmin)
