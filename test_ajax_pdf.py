#!/usr/bin/env python
"""
Test script to verify AJAX endpoint returns all financial fields
"""
import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from invoices.models import Child, DaycareProvider
import json

User = get_user_model()

def test_ajax_pdf_upload():
    """Test the AJAX PDF upload endpoint"""
    print("🧪 TESTING AJAX PDF UPLOAD ENDPOINT")
    print("=" * 50)
    
    # Create test user if needed
    user, created = User.objects.get_or_create(
        username='testuser_ajax',
        defaults={
            'email': 'testajax@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Create test provider and child
    provider, _ = DaycareProvider.objects.get_or_create(
        name='Test Daycare Ajax',
        defaults={'email': 'daycare@testajax.com'}
    )
    
    child, _ = Child.objects.get_or_create(
        user=user,
        name='Sofia Green',
        reference_number='SG300',
        defaults={'daycare_provider': provider}
    )
    
    # Test AJAX endpoint
    client = Client()
    client.login(username='testuser_ajax', password='testpass123')
    
    print("✅ Testing AJAX PDF upload endpoint...")
    
    # Use Sofia's actual PDF file
    pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    with open(pdf_path, 'rb') as pdf_file:
        response = client.post(
            reverse('invoices:invoice_upload_ajax'),
            {'pdf_file': pdf_file},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
    
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ AJAX response received successfully")
        print(f"Success: {data.get('success', False)}")
        
        if data.get('success') and data.get('data'):
            extracted_data = data['data']
            print("\n📊 EXTRACTED FINANCIAL DATA:")
            print("-" * 40)
            
            # Check all the financial fields
            financial_fields = [
                'previous_balance',
                'original_amount', 
                'discount_percentage',
                'discount_amount',
                'week_amount_due',
                'total_amount_due',
                'amount_due'
            ]
            
            for field in financial_fields:
                value = extracted_data.get(field)
                if value is not None:
                    print(f"✅ {field}: {value}")
                else:
                    print(f"❌ {field}: MISSING")
            
            # Check other important fields
            other_fields = ['child_name', 'child_reference', 'invoice_reference']
            print("\n📋 OTHER EXTRACTED DATA:")
            print("-" * 40)
            for field in other_fields:
                value = extracted_data.get(field)
                if value is not None:
                    print(f"✅ {field}: {value}")
                else:
                    print(f"❌ {field}: MISSING")
                    
            print(f"\n🔍 FULL RESPONSE DATA:")
            print(json.dumps(data, indent=2, default=str))
            
        else:
            print("❌ No data in response or processing failed")
            if data.get('errors'):
                print(f"Errors: {data['errors']}")
                
    else:
        print(f"❌ AJAX request failed: {response.status_code}")
        print(f"Response content: {response.content.decode()}")
    
    print("\n🎉 AJAX TEST COMPLETE")
    print("=" * 50)

if __name__ == "__main__":
    test_ajax_pdf_upload()
