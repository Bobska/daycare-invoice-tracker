#!/usr/bin/env python
"""
Test script to verify the JavaScript calculation fixes
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

def test_javascript_calculation():
    """Test that the form JavaScript is properly included"""
    print("🧪 TESTING JAVASCRIPT CALCULATION FIXES")
    print("=" * 50)
    
    # Create test data
    user, created = User.objects.get_or_create(
        username='calctest',
        defaults={
            'email': 'calctest@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    provider, _ = DaycareProvider.objects.get_or_create(
        name='Calc Test Daycare',
        defaults={'email': 'calc@test.com'}
    )
    
    child, _ = Child.objects.get_or_create(
        user=user,
        name='Calc Test Child',
        reference_number='CTC001',
        defaults={'daycare_provider': provider}
    )
    
    # Test form access
    client = Client()
    client.login(username='calctest', password='testpass123')
    
    print("✅ Testing form JavaScript inclusion...")
    response = client.get(reverse('invoices:invoice_create'))
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check for JavaScript function
        if 'function calculateAmounts()' in content:
            print("✅ calculateAmounts function found")
        else:
            print("❌ calculateAmounts function missing")
            
        # Check for event listener setup
        if 'setupCalculationListeners' in content:
            print("✅ setupCalculationListeners function found")
        else:
            print("❌ setupCalculationListeners function missing")
            
        # Check for debug logging
        if 'console.log(' in content:
            print("✅ Debug logging found")
        else:
            print("❌ Debug logging missing")
            
        # Check for field IDs
        required_ids = ['id_original_amount', 'id_discount_percentage', 'id_previous_balance']
        for field_id in required_ids:
            if field_id in content:
                print(f"✅ Field {field_id} found in template")
            else:
                print(f"❌ Field {field_id} missing from template")
                
        # Check for calculated field styling
        if 'data-calculated' in content:
            print("✅ Calculated field attributes found")
        else:
            print("❌ Calculated field attributes missing")
            
        print(f"\n📊 Template size: {len(content)} characters")
        
    else:
        print(f"❌ Form failed to load: {response.status_code}")
    
    print("\n🎉 JAVASCRIPT TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_javascript_calculation()
