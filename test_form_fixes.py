#!/usr/bin/env python
"""
Test script to verify the invoice form fixes are working
"""
import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from invoices.models import Child, DaycareProvider

User = get_user_model()

def test_form_fixes():
    """Test that the form loads correctly and calculations work"""
    print("🧪 TESTING INVOICE FORM FIXES")
    print("=" * 50)
    
    # Create test data - use unique email to avoid conflicts
    import time
    unique_suffix = str(int(time.time()))
    
    user, created = User.objects.get_or_create(
        username=f'testuser_{unique_suffix}',
        defaults={
            'email': f'test_{unique_suffix}@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    provider = DaycareProvider.objects.create(
        name='Test Daycare',
        email='daycare@test.com'
    )
    
    child = Child.objects.create(
        user=user,
        name='Test Child',
        reference_number='TC001',
        daycare_provider=provider
    )
    
    # Test form access
    client = Client()
    client.login(username=user.username, password='testpass123')
    
    print("✅ Testing form access...")
    response = client.get(reverse('invoices:invoice_create'))
    print(f"Form response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Form loads successfully")
        
        # Check if form contains our new fields
        content = response.content.decode()
        required_fields = [
            'id_original_amount',
            'id_discount_percentage', 
            'id_discount_amount',
            'id_previous_balance',
            'id_week_amount_due',
            'id_total_amount_due'
        ]
        
        for field in required_fields:
            if field in content:
                print(f"✅ Field {field} found in form")
            else:
                print(f"❌ Field {field} missing from form")
                
        # Check if JavaScript calculation function is present
        if 'calculateAmounts' in content:
            print("✅ JavaScript calculation function found")
        else:
            print("❌ JavaScript calculation function missing")
            
    else:
        print(f"❌ Form failed to load: {response.status_code}")
    
    print("\n🧪 Testing form submission...")
    
    # Test form submission with valid data
    form_data = {
        'child': child.id,
        'invoice_reference': 'TEST001',
        'period_start': '2025-08-25',
        'period_end': '2025-08-29',
        'issue_date': '2025-08-25',
        'original_amount': '321.75',
        'discount_percentage': '75.00',
        'discount_amount': '241.31',  # Should be calculated
        'previous_balance': '86.52',
        'week_amount_due': '80.44',  # Should be calculated
        'total_amount_due': '166.96',  # Should be calculated
        'fee_type': 'Under 3 Fee',
    }
    
    response = client.post(reverse('invoices:invoice_create'), data=form_data)
    print(f"Form submission status: {response.status_code}")
    
    if response.status_code == 302:  # Redirect after successful creation
        print("✅ Form submission successful")
        print("✅ No 'method' attribute error encountered")
    else:
        print(f"❌ Form submission failed: {response.status_code}")
        if hasattr(response, 'content'):
            print("Response content:", response.content.decode()[:500])
    
    print("\n🎉 FORM FIXES TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_form_fixes()
