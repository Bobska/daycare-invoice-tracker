#!/usr/bin/env python
"""
Test script to verify the previous balance calculation fix
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

def test_calculation_updates():
    """Test that previous balance changes trigger calculation updates"""
    print("🧪 TESTING PREVIOUS BALANCE CALCULATION UPDATES")
    print("=" * 60)
    
    # Create test data
    import time
    unique_suffix = str(int(time.time()))
    
    user, created = User.objects.get_or_create(
        username=f'testuser_calc_{unique_suffix}',
        defaults={
            'email': f'test_calc_{unique_suffix}@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    provider, created = DaycareProvider.objects.get_or_create(
        name='Test Calc Daycare',
        defaults={'email': 'calctest@test.com'}
    )
    
    child, created = Child.objects.get_or_create(
        user=user,
        name='Test Calc Child',
        defaults={
            'reference_number': f'TCC{unique_suffix}',
            'daycare_provider': provider
        }
    )
    
    # Test form access with debug console
    client = Client()
    client.login(username=user.username, password='testpass123')
    
    print("✅ Testing form with calculation debugging...")
    response = client.get(reverse('invoices:invoice_create'))
    print(f"Form response status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode()
        
        # Check if debug console.log statements are present
        debug_checks = [
            'console.log(\'calculateAmounts called\')',
            'console.log(\'Values:\', { originalAmount, discountPercentage, previousBalance })',
            'console.log(\'Setting up calculation event listeners\')',
            'addEventListener(\'keyup\'',
        ]
        
        for check in debug_checks:
            if check in content:
                print(f"✅ Debug logging found: {check[:50]}...")
            else:
                print(f"❌ Debug logging missing: {check[:50]}...")
                
        # Check if field styling is updated
        if 'data-calculated="true"' in content:
            print("✅ Updated field styling found")
        elif 'readonly' in content and 'discount_amount' in content:
            print("⚠️  Old readonly styling still present")
        else:
            print("❌ Field styling not found")
            
        # Check if previous_balance field has proper event listeners
        if 'id_previous_balance' in content and 'fieldsToWatch' in content:
            print("✅ Previous balance field included in event listeners")
        else:
            print("❌ Previous balance field missing from event listeners")
    
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("1. Open Create Invoice page")
    print("2. Enter Original Amount: 100")
    print("3. Enter Discount Percentage: 10")
    print("4. Enter Previous Balance: 50")
    print("5. Should see:")
    print("   - Discount Amount: 10.00 (auto-calculated)")
    print("   - Week Amount Due: 90.00 (auto-calculated)")
    print("   - Total Amount Due: 140.00 (auto-calculated)")
    print("6. Change Previous Balance to 75")
    print("7. Should see Total Amount Due update to: 165.00")
    
    print("\n🔧 DEBUG INSTRUCTIONS:")
    print("1. Open browser Developer Tools (F12)")
    print("2. Go to Console tab")
    print("3. Refresh the Create Invoice page")
    print("4. Look for debug messages when typing in fields")
    print("5. Check if 'calculateAmounts called' appears when changing Previous Balance")
    
    print("\n🎉 CALCULATION TEST SETUP COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_calculation_updates()
