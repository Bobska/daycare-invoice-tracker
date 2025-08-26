#!/usr/bin/env python
"""
Detailed Financial Analysis of Sofia's PDF
Understanding the complete financial breakdown structure
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')
django.setup()

import PyPDF2
import re

def analyze_sofia_financial_breakdown():
    """Analyze Sofia's PDF for detailed financial structure"""
    pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
    
    print("💰 DETAILED FINANCIAL ANALYSIS - SOFIA'S PDF")
    print("=" * 60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    try:
        # Extract raw PDF text
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            raw_text = ""
            for page in pdf_reader.pages:
                raw_text += page.extract_text() + "\n"
        
        print("📄 RAW PDF TEXT:")
        print("-" * 40)
        print(raw_text)
        print("\n" + "=" * 60)
        
        # Parse financial items line by line
        lines = raw_text.split('\n')
        print("\n📊 LINE-BY-LINE FINANCIAL ANALYSIS:")
        print("-" * 50)
        
        financial_data = {
            'previous_balance': None,
            'original_amount': None,
            'discount_amount': None,
            'discount_percentage': None,
            'week_amount_due': None,
            'total_amount_due': None,
        }
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
            
            print(f"Line {i+1:2d}: {repr(line_clean)}")
            
            # Look for Previous Balance
            if 'Previous Balance' in line_clean:
                prev_match = re.search(r'\$(\d+\.\d{2})', line_clean)
                if prev_match:
                    financial_data['previous_balance'] = Decimal(prev_match.group(1))
                    print(f"    🔍 FOUND Previous Balance: ${financial_data['previous_balance']}")
            
            # Look for Under 3 Fee (original amount)
            elif 'Under 3 Fee' in line_clean or '1Under 3 Fee' in line_clean:
                # This line should contain the original weekly fee
                amount_match = re.search(r'\$(\d+\.\d{2})', line_clean)
                if amount_match:
                    financial_data['original_amount'] = Decimal(amount_match.group(1))
                    print(f"    🔍 FOUND Original Weekly Fee: ${financial_data['original_amount']}")
            
            # Look for Fee Discount
            elif 'Fee Discount' in line_clean:
                # Extract discount percentage
                pct_match = re.search(r'(\d+\.\d{2})%', line_clean)
                if pct_match:
                    financial_data['discount_percentage'] = Decimal(pct_match.group(1))
                    print(f"    🔍 FOUND Discount Percentage: {financial_data['discount_percentage']}%")
                
                # Extract discount amount (should be negative)
                discount_match = re.search(r'-\$(\d+\.\d{2})', line_clean)
                if discount_match:
                    financial_data['discount_amount'] = Decimal(discount_match.group(1))
                    print(f"    🔍 FOUND Discount Amount: -${financial_data['discount_amount']}")
            
            # Look for Amount due (total)
            elif 'Amount due (GST incl)' in line_clean:
                total_match = re.search(r'\$(\d+\.\d{2})', line_clean)
                if total_match:
                    financial_data['total_amount_due'] = Decimal(total_match.group(1))
                    print(f"    🔍 FOUND Total Amount Due: ${financial_data['total_amount_due']}")
        
        # Calculate week amount due (excluding previous balance)
        if (financial_data['original_amount'] is not None and 
            financial_data['discount_amount'] is not None):
            financial_data['week_amount_due'] = (
                financial_data['original_amount'] - financial_data['discount_amount']
            )
            print(f"    🧮 CALCULATED Week Amount Due: ${financial_data['week_amount_due']}")
        
        print(f"\n📈 FINANCIAL BREAKDOWN SUMMARY:")
        print("-" * 40)
        for key, value in financial_data.items():
            if value is not None:
                if 'percentage' in key:
                    print(f"✅ {key.replace('_', ' ').title()}: {value}%")
                else:
                    print(f"✅ {key.replace('_', ' ').title()}: ${value}")
            else:
                print(f"❌ {key.replace('_', ' ').title()}: Not found")
        
        print(f"\n🧮 VERIFICATION CALCULATIONS:")
        print("-" * 35)
        
        if financial_data['original_amount'] and financial_data['discount_percentage']:
            calculated_discount = financial_data['original_amount'] * (financial_data['discount_percentage'] / 100)
            print(f"Expected discount amount: ${calculated_discount:.2f}")
            if financial_data['discount_amount']:
                print(f"Actual discount amount: ${financial_data['discount_amount']}")
                if abs(calculated_discount - financial_data['discount_amount']) < 0.01:
                    print("✅ Discount calculation matches!")
                else:
                    print("❌ Discount calculation mismatch!")
        
        if financial_data['week_amount_due'] and financial_data['previous_balance'] and financial_data['total_amount_due']:
            calculated_total = financial_data['week_amount_due'] + financial_data['previous_balance']
            print(f"\nExpected total (week + previous): ${calculated_total:.2f}")
            print(f"Actual total amount due: ${financial_data['total_amount_due']}")
            if abs(calculated_total - financial_data['total_amount_due']) < 0.01:
                print("✅ Total calculation matches!")
            else:
                print("❌ Total calculation mismatch!")
        
        print(f"\n💡 EXTRACTION PATTERNS NEEDED:")
        print("-" * 35)
        print("1. Previous Balance: r'Previous Balance\\s+\\$(\\d+\\.\\d{2})'")
        print("2. Original Amount: r'Under 3 Fee.*?\\$(\\d+\\.\\d{2})'")
        print("3. Discount %: r'Fee Discount of (\\d+\\.\\d{2})%'")
        print("4. Discount Amount: r'Fee Discount.*?-\\$(\\d+\\.\\d{2})'")
        print("5. Total Due: r'Amount due \\(GST incl\\)\\s*\\$(\\d+\\.\\d{2})'")
        
        return financial_data
        
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    analyze_sofia_financial_breakdown()
