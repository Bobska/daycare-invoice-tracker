from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model to support future email integration"""
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    notification_preferences = models.JSONField(
        default=dict,
        help_text="User preferences for email/SMS notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
