#!/usr/bin/env python
"""
Test script for validating bug fixes in Phase 2 functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from invoices.models import Child, DaycareProvider, Invoice, Payment
from decimal import Decimal

def test_form_submissions():
    """Test form submissions with debugging output"""
    print("🧪 TESTING FORM SUBMISSIONS")
    print("=" * 50)
    
    client = Client()
    User = get_user_model()
    
    # Create test user
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(
        username=f'testformuser{unique_id}',
        password='testpass123',
        email=f'test{unique_id}@example.com'
    )
    
    # Login
    login_success = client.login(username=f'testformuser{unique_id}', password='testpass123')
    print(f"✅ Login successful: {login_success}")
    
    # Create a daycare provider first (needed for child)
    provider = DaycareProvider.objects.create(
        name='Test Daycare Center',
        email='test@daycare.com',
        phone='123-456-7890'
    )
    print(f"✅ Created test provider: {provider.name}")
    
    # Test 1: Child Creation
    print("\n📝 Testing Child Creation...")
    child_data = {
        'name': 'Test Child Form',
        'reference_number': 'FORM001',
        'daycare_provider': provider.pk,
        'enrollment_date': '2025-01-15'
    }
    
    response = client.post(reverse('invoices:child_create'), data=child_data)
    print(f"Child form response status: {response.status_code}")
    
    if response.status_code == 302:  # Redirect indicates success
        child = Child.objects.filter(user=user, name='Test Child Form').first()
        if child:
            print(f"✅ Child creation SUCCESSFUL: {child.name}")
        else:
            print("❌ Child creation FAILED: No child found in database")
    else:
        print(f"❌ Child creation FAILED: Status {response.status_code}")
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            print(f"Form errors: {response.context['form'].errors}")
    
    # Test 2: Invoice Creation (without PDF)
    print("\n📄 Testing Invoice Creation...")
    child = Child.objects.filter(user=user).first()
    
    if child:
        invoice_data = {
            'child': child.pk,
            'invoice_reference': 'TEST-INV-001',
            'issue_date': '2025-08-25',
            'due_date': '2025-09-01',
            'period_start': '2025-08-01',
            'period_end': '2025-08-31',
            'original_amount': '150.00',
            'amount_due': '150.00',
            'discount_percentage': '0.00',  # Add required discount fields
            'discount_amount': '0.00',
            'fee_type': 'Monthly Fee'
        }
        
        response = client.post(reverse('invoices:invoice_create'), data=invoice_data)
        print(f"Invoice form response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect indicates success
            invoice = Invoice.objects.filter(invoice_reference='TEST-INV-001').first()
            if invoice:
                print(f"✅ Invoice creation SUCCESSFUL: {invoice.invoice_reference}")
            else:
                print("❌ Invoice creation FAILED: No invoice found in database")
        else:
            print(f"❌ Invoice creation FAILED: Status {response.status_code}")
            if hasattr(response, 'context') and response.context and 'form' in response.context:
                print(f"Form errors: {response.context['form'].errors}")
    else:
        print("❌ Cannot test invoice creation: No child found")
    
    # Test 3: Payment Creation
    print("\n💰 Testing Payment Creation...")
    invoice = Invoice.objects.filter(child__user=user).first()
    
    if invoice:
        payment_data = {
            'invoice': invoice.pk,
            'payment_date': '2025-08-26',
            'amount_paid': '75.00',
            'payment_method': 'credit_card'
        }
        
        response = client.post(reverse('invoices:payment_create'), data=payment_data)
        print(f"Payment form response status: {response.status_code}")
        
        if response.status_code == 302:  # Redirect indicates success
            payment = Payment.objects.filter(invoice=invoice).first()
            if payment:
                print(f"✅ Payment creation SUCCESSFUL: ${payment.amount_paid}")
            else:
                print("❌ Payment creation FAILED: No payment found in database")
        else:
            print(f"❌ Payment creation FAILED: Status {response.status_code}")
            if hasattr(response, 'context') and response.context and 'form' in response.context:
                print(f"Form errors: {response.context['form'].errors}")
    else:
        print("❌ Cannot test payment creation: No invoice found")
    
    print("\n📊 Final Database State:")
    print(f"Children created: {Child.objects.filter(user=user).count()}")
    print(f"Invoices created: {Invoice.objects.filter(child__user=user).count()}")
    print(f"Payments created: {Payment.objects.filter(invoice__child__user=user).count()}")


def test_logout_functionality():
    """Test logout doesn't give 405 error"""
    print("\n🚪 TESTING LOGOUT FUNCTIONALITY")
    print("=" * 50)
    
    client = Client()
    User = get_user_model()
    
    # Create and login user
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(
        username=f'testlogoutuser{unique_id}',
        password='testpass123'
    )
    
    client.login(username=f'testlogoutuser{unique_id}', password='testpass123')
    
    # Test logout with POST (should work)
    response = client.post(reverse('accounts:logout'))
    print(f"Logout POST response status: {response.status_code}")
    
    if response.status_code in [200, 302]:  # Success or redirect
        print("✅ Logout functionality WORKING")
    else:
        print(f"❌ Logout functionality FAILED: Status {response.status_code}")


if __name__ == '__main__':
    try:
        test_form_submissions()
        test_logout_functionality()
        
        print("\n🎉 BUG FIX TESTING COMPLETE!")
        print("Check the console output above for any debug information from form submissions.")
        print("If forms are working, you should see success messages and database objects created.")
        
    except Exception as e:
        print(f"❌ Test script error: {str(e)}")
        import traceback
        traceback.print_exc()
