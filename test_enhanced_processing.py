#!/usr/bin/env python
"""
Test enhanced PDF processing with new financial fields
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')
django.setup()

from invoices.utils import extract_pdf_text, parse_invoice_data

def test_enhanced_pdf_processing():
    """Test Sofia PDF with enhanced financial processing"""
    pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
    
    print("💰 TESTING ENHANCED FINANCIAL PDF PROCESSING")
    print("=" * 60)
    
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
            print(f"\n🔍 Parsing enhanced financial data...")
            parsed_data = parse_invoice_data(extracted_text)
            
            print(f"\n📊 ENHANCED FINANCIAL RESULTS:")
            print("-" * 40)
            
            # Core financial data
            financial_fields = [
                'original_amount',
                'discount_percentage', 
                'discount_amount',
                'previous_balance',
                'week_amount_due',
                'total_amount_due',
                'amount_due'  # Legacy field
            ]
            
            for field in financial_fields:
                value = parsed_data.get(field, '')
                if value:
                    if 'percentage' in field:
                        print(f"✅ {field.replace('_', ' ').title()}: {value}%")
                    else:
                        print(f"✅ {field.replace('_', ' ').title()}: ${value}")
                else:
                    print(f"❌ {field.replace('_', ' ').title()}: [empty]")
            
            # Other key fields
            other_fields = [
                'child_name',
                'child_reference', 
                'invoice_reference',
                'issue_date',
                'period_start',
                'period_end',
                'fee_type'
            ]
            
            print(f"\n📋 OTHER INVOICE DETAILS:")
            print("-" * 30)
            for field in other_fields:
                value = parsed_data.get(field, '')
                if value:
                    print(f"✅ {field.replace('_', ' ').title()}: {value}")
                else:
                    print(f"❌ {field.replace('_', ' ').title()}: [empty]")
            
            print(f"\n🧮 FINANCIAL VERIFICATION:")
            print("-" * 30)
            
            # Verify calculations
            success_count = 0
            total_checks = 5
            
            # Check discount calculation
            if (parsed_data.get('original_amount') and 
                parsed_data.get('discount_percentage') and 
                parsed_data.get('discount_amount')):
                expected_discount = parsed_data['original_amount'] * (parsed_data['discount_percentage'] / 100)
                actual_discount = parsed_data['discount_amount']
                if abs(expected_discount - actual_discount) < 0.01:
                    print("✅ Discount calculation correct")
                    success_count += 1
                else:
                    print(f"❌ Discount mismatch: expected ${expected_discount:.2f}, got ${actual_discount}")
            else:
                print("❌ Missing discount data for verification")
            
            # Check week amount calculation
            if (parsed_data.get('original_amount') and 
                parsed_data.get('discount_amount') and 
                parsed_data.get('week_amount_due')):
                expected_week = parsed_data['original_amount'] - parsed_data['discount_amount']
                actual_week = parsed_data['week_amount_due']
                if abs(expected_week - actual_week) < 0.01:
                    print("✅ Week amount calculation correct")
                    success_count += 1
                else:
                    print(f"❌ Week amount mismatch: expected ${expected_week:.2f}, got ${actual_week}")
            else:
                print("❌ Missing week amount data for verification")
            
            # Check total calculation
            if (parsed_data.get('week_amount_due') and 
                parsed_data.get('previous_balance') and 
                parsed_data.get('total_amount_due')):
                expected_total = parsed_data['week_amount_due'] + parsed_data['previous_balance']
                actual_total = parsed_data['total_amount_due']
                if abs(expected_total - actual_total) < 0.01:
                    print("✅ Total amount calculation correct")
                    success_count += 1
                else:
                    print(f"❌ Total mismatch: expected ${expected_total:.2f}, got ${actual_total}")
            else:
                print("❌ Missing total amount data for verification")
            
            # Check legacy field sync
            if (parsed_data.get('amount_due') and 
                parsed_data.get('total_amount_due')):
                if parsed_data['amount_due'] == parsed_data['total_amount_due']:
                    print("✅ Legacy amount_due field synced correctly")
                    success_count += 1
                else:
                    print("❌ Legacy amount_due field not synced")
            else:
                print("❌ Missing amount_due data for sync check")
            
            # Check all required fields extracted
            required_fields = ['child_name', 'invoice_reference', 'original_amount', 'total_amount_due']
            all_present = all(parsed_data.get(field) for field in required_fields)
            if all_present:
                print("✅ All required fields extracted")
                success_count += 1
            else:
                missing = [f for f in required_fields if not parsed_data.get(f)]
                print(f"❌ Missing required fields: {missing}")
            
            print(f"\n🏆 OVERALL SUCCESS RATE: {success_count}/{total_checks} ({success_count/total_checks*100:.1f}%)")
            
            if success_count >= 4:
                print("🎉 Enhanced PDF processing is working excellently!")
                print("\n💡 BUSINESS INSIGHTS:")
                print(f"📅 This week's fee: ${parsed_data.get('week_amount_due', 0)}")
                print(f"📋 Previous unpaid: ${parsed_data.get('previous_balance', 0)}")
                print(f"📊 Total owed: ${parsed_data.get('total_amount_due', 0)}")
                if parsed_data.get('discount_percentage'):
                    print(f"💰 Discount applied: {parsed_data.get('discount_percentage')}%")
            else:
                print("⚠️ Enhanced PDF processing needs adjustment")
            
            return parsed_data
            
    except Exception as e:
        print(f"❌ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    test_enhanced_pdf_processing()
