#!/usr/bin/env python
"""
Test PDF processing through Django application
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from invoices.utils import extract_pdf_text, parse_invoice_data

def test_sofia_pdf_django():
    """Test Sofia PDF with Django setup"""
    pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
    
    print("🔍 TESTING SOFIA PDF WITH DJANGO")
    print("=" * 50)
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    try:
        # Extract text from PDF
        with open(pdf_path, 'rb') as file:
            print("📄 Extracting text from PDF...")
            extracted_text = extract_pdf_text(file)
            print(f"✅ Extracted {len(extracted_text)} characters")
            
            # Parse the data
            print("\n🔍 Parsing invoice data...")
            parsed_data = parse_invoice_data(extracted_text)
            
            print("\n📊 PARSED RESULTS:")
            print("-" * 30)
            
            key_results = {
                'child_name': parsed_data.get('child_name', ''),
                'child_reference': parsed_data.get('child_reference', ''),
                'invoice_reference': parsed_data.get('invoice_reference', ''),
                'issue_date': parsed_data.get('issue_date', ''),
                'period_start': parsed_data.get('period_start', ''),
                'period_end': parsed_data.get('period_end', ''),
                'amount_due': parsed_data.get('amount_due', ''),
                'fee_type': parsed_data.get('fee_type', ''),
                'provider_name': parsed_data.get('provider_name', ''),
            }
            
            for key, value in key_results.items():
                if value:
                    print(f"✅ {key}: {value}")
                else:
                    print(f"❌ {key}: [empty/not found]")
            
            print("\n🎯 VALIDATION:")
            print("-" * 20)
            
            # Check key fields
            success_count = 0
            total_checks = 6
            
            if 'Sofia' in str(parsed_data.get('child_name', '')):
                print("✅ Child name contains 'Sofia'")
                success_count += 1
            else:
                print("❌ Child name missing 'Sofia'")
            
            if parsed_data.get('child_reference') == 'SG300':
                print("✅ Child reference is SG300")
                success_count += 1
            else:
                print("❌ Child reference not SG300")
            
            if parsed_data.get('invoice_reference') == '78352':
                print("✅ Invoice reference is 78352")
                success_count += 1
            else:
                print("❌ Invoice reference not 78352")
            
            if parsed_data.get('amount_due'):
                print(f"✅ Amount due found: ${parsed_data.get('amount_due')}")
                success_count += 1
            else:
                print("❌ Amount due not found")
            
            if parsed_data.get('issue_date'):
                print(f"✅ Issue date found: {parsed_data.get('issue_date')}")
                success_count += 1
            else:
                print("❌ Issue date not found")
            
            if 'Fee' in str(parsed_data.get('fee_type', '')):
                print(f"✅ Fee type found: {parsed_data.get('fee_type')}")
                success_count += 1
            else:
                print("❌ Fee type not found")
            
            print(f"\n🏆 SUCCESS RATE: {success_count}/{total_checks} ({success_count/total_checks*100:.1f}%)")
            
            if success_count >= 5:
                print("🎉 PDF processing is working well!")
            else:
                print("⚠️ PDF processing needs more work")
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_sofia_pdf_django()
