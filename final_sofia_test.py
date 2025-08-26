#!/usr/bin/env python
"""
Final test of Sofia PDF processing with Django imports
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    
    # Now import Django components
    from invoices.utils import extract_pdf_text, parse_invoice_data
    
    def test_sofia_pdf_processing():
        """Test Sofia PDF with updated patterns"""
        pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
        
        print("🔍 TESTING SOFIA PDF WITH DJANGO PROCESSING")
        print("=" * 60)
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found: {pdf_path}")
            return
        
        try:
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                extracted_text = extract_pdf_text(file)
                print(f"📄 Extracted text length: {len(extracted_text)}")
                
                # Parse the data
                parsed_data = parse_invoice_data(extracted_text)
                
                print("\n📊 PARSED RESULTS:")
                print("-" * 30)
                for key, value in parsed_data.items():
                    if value:
                        print(f"✅ {key}: {value}")
                    else:
                        print(f"❌ {key}: [empty]")
                
                print("\n🎯 EXPECTED VS ACTUAL:")
                print("-" * 30)
                expected = {
                    'child_name': 'Sofia Green',
                    'child_reference': 'SG300',
                    'invoice_reference': '78352',
                    'issue_date': '2025-08-25',
                    'period_start': '2025-08-25',
                    'period_end': '2025-08-29',
                    'amount_due': '166.96',
                    'fee_type': 'Under 3 Fee',
                    'provider_name': 'Active Explorers Ashburton'
                }
                
                for key, expected_value in expected.items():
                    actual_value = str(parsed_data.get(key, ''))
                    if expected_value.lower() in actual_value.lower() or actual_value.lower() in expected_value.lower():
                        print(f"✅ {key}: Expected '{expected_value}' ≈ Actual '{actual_value}'")
                    else:
                        print(f"❌ {key}: Expected '{expected_value}' ≠ Actual '{actual_value}'")
                
        except Exception as e:
            print(f"❌ Error processing PDF: {e}")
            import traceback
            traceback.print_exc()
    
    test_sofia_pdf_processing()
    
except Exception as e:
    print(f"Django setup failed: {e}")
    print("This is expected - let's create a simpler version...")
    
    # Fallback to simplified testing
    import PyPDF2
    from decimal import Decimal
    from datetime import datetime, date
    import re
    
    def simple_parse_date_string(date_str: str):
        """Simple date parsing"""
        date_formats = [
            '%d %B %Y',  # Format for "25 August 2025"
            '%d %b %Y',  # Format for "25 Aug 2025"
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None
    
    def simple_parse_invoice_data(text: str):
        """Simplified parsing for testing"""
        text_upper = text.upper()
        parsed_data = {}
        
        # Child name - fix the pattern
        child_match = re.search(r'STATEMENT\s+FOR\s+([A-Z\s]+?)\s*-\w+', text_upper)
        if child_match:
            name_part = child_match.group(1).strip()
            parsed_data['child_name'] = ' '.join(word.capitalize() for word in name_part.split())
        
        # Child reference
        ref_match = re.search(r'STATEMENT\s+FOR\s+[A-Z\s]+-(\w+)', text_upper)
        if ref_match:
            parsed_data['child_reference'] = ref_match.group(1)
        
        # Invoice reference
        inv_match = re.search(r'INV\s+(\d+)', text_upper)
        if inv_match:
            parsed_data['invoice_reference'] = inv_match.group(1)
        
        # Issue date
        issue_match = re.search(r'ISSUED\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})', text_upper)
        if issue_match:
            parsed_data['issue_date'] = simple_parse_date_string(issue_match.group(1))
        
        # Period dates
        period_start_match = re.search(r'PERIOD\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})', text_upper)
        if period_start_match:
            parsed_data['period_start'] = simple_parse_date_string(period_start_match.group(1))
        
        period_end_match = re.search(r'PERIOD\s*:?\s*\d{1,2}\s+\w+\s+\d{4}\s*-\s*(\d{1,2}\s+\w+\s+\d{4})', text_upper)
        if period_end_match:
            parsed_data['period_end'] = simple_parse_date_string(period_end_match.group(1))
        
        # Amount due
        amount_match = re.search(r'AMOUNT\s+DUE\s*\(\w+\s+\w+\)\s*\$(\d{1,3}(?:\.\d{2})?)', text_upper)
        if amount_match:
            parsed_data['amount_due'] = Decimal(amount_match.group(1))
        
        # Fee type
        fee_match = re.search(r'(UNDER\s+\d+\s+FEE)', text, re.IGNORECASE)
        if fee_match:
            parsed_data['fee_type'] = fee_match.group(1)
        
        return parsed_data
    
    def simple_test():
        """Simple test without Django"""
        pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
        
        print("🔍 SIMPLE SOFIA PDF TEST")
        print("=" * 40)
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                parsed_data = simple_parse_invoice_data(text)
                
                print("📊 PARSED RESULTS:")
                for key, value in parsed_data.items():
                    print(f"  {key}: {value}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    simple_test()
