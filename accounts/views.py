from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form for registration"""
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required
        self.fields['email'].required = True
        # Add CSS classes
        for fieldname in ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs['class'] = 'form-control'


class RegisterView(CreateView):
    """User registration view"""
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('invoices:dashboard')
    
    def form_valid(self, form):
        """Log in the user after successful registration"""
        # Save the user first
        user = form.save()
        # Log in the user
        login(self.request, user)
        # Add success message
        messages.success(self.request, f'Welcome to DayCare Invoice Tracker, {user.first_name or user.username}!')
        # Redirect to success URL
        return redirect(self.success_url)
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect authenticated users to dashboard"""
        if request.user.is_authenticated:
            return redirect('invoices:dashboard')
        return super().dispatch(request, *args, **kwargs)
