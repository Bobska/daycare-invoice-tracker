#!/usr/bin/env python
"""
Enhanced Financial Analysis - Multi-line Pattern Recognition
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

def enhanced_sofia_analysis():
    """Enhanced analysis considering multi-line financial data"""
    pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
    
    print("🔍 ENHANCED FINANCIAL ANALYSIS - MULTI-LINE PATTERNS")
    print("=" * 65)
    
    try:
        # Extract raw PDF text
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            raw_text = ""
            for page in pdf_reader.pages:
                raw_text += page.extract_text() + "\n"
        
        # Parse financial items with context awareness
        lines = raw_text.split('\n')
        financial_data = {
            'previous_balance': None,
            'original_amount': None,
            'discount_amount': None,
            'discount_percentage': None,
            'week_amount_due': None,
            'total_amount_due': None,
        }
        
        print("📊 CONTEXTUAL FINANCIAL EXTRACTION:")
        print("-" * 45)
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue
            
            # Previous Balance - direct pattern
            if 'Previous Balance' in line_clean:
                prev_match = re.search(r'\$(\d+\.\d{2})', line_clean)
                if prev_match:
                    financial_data['previous_balance'] = Decimal(prev_match.group(1))
                    print(f"✅ Previous Balance: ${financial_data['previous_balance']} (Line {i+1})")
            
            # Under 3 Fee - look at current and next line
            elif 'Under 3 Fee' in line_clean or '1Under 3 Fee' in line_clean:
                print(f"🔍 Found Under 3 Fee line: {repr(line_clean)}")
                # Check current line for amount
                amount_match = re.search(r'\$(\d+\.\d{2})', line_clean)
                if amount_match:
                    financial_data['original_amount'] = Decimal(amount_match.group(1))
                    print(f"✅ Original Amount (same line): ${financial_data['original_amount']}")
                # Check next line for amount
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    print(f"🔍 Checking next line: {repr(next_line)}")
                    next_amount_match = re.search(r'\$(\d+\.\d{2})', next_line)
                    if next_amount_match:
                        financial_data['original_amount'] = Decimal(next_amount_match.group(1))
                        print(f"✅ Original Amount (next line): ${financial_data['original_amount']}")
            
            # Fee Discount - percentage and amount extraction
            elif 'Fee Discount' in line_clean:
                print(f"🔍 Found Fee Discount line: {repr(line_clean)}")
                # Extract percentage
                pct_match = re.search(r'(\d+\.\d{2})%', line_clean)
                if pct_match:
                    financial_data['discount_percentage'] = Decimal(pct_match.group(1))
                    print(f"✅ Discount Percentage: {financial_data['discount_percentage']}%")
                
                # Look for discount amount in current or next line
                discount_match = re.search(r'-\$(\d+\.\d{2})', line_clean)
                if discount_match:
                    financial_data['discount_amount'] = Decimal(discount_match.group(1))
                    print(f"✅ Discount Amount (same line): -${financial_data['discount_amount']}")
                elif i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    print(f"🔍 Checking next line for discount: {repr(next_line)}")
                    next_discount_match = re.search(r'-\$(\d+\.\d{2})', next_line)
                    if next_discount_match:
                        financial_data['discount_amount'] = Decimal(next_discount_match.group(1))
                        print(f"✅ Discount Amount (next line): -${financial_data['discount_amount']}")
            
            # Amount due - total
            elif 'Amount due (GST incl)' in line_clean:
                total_match = re.search(r'\$(\d+\.\d{2})', line_clean)
                if total_match:
                    financial_data['total_amount_due'] = Decimal(total_match.group(1))
                    print(f"✅ Total Amount Due: ${financial_data['total_amount_due']} (Line {i+1})")
        
        # Check for amounts in standalone lines (lines with just $amount)
        print(f"\n🔍 SCANNING FOR STANDALONE AMOUNT LINES:")
        print("-" * 40)
        for i, line in enumerate(lines):
            line_clean = line.strip()
            # Look for lines that are just amounts
            if re.match(r'^\$?\d+\.\d{2}$', line_clean) or re.match(r'^-\$\d+\.\d{2}$', line_clean):
                print(f"Line {i+1}: {repr(line_clean)} (standalone amount)")
                
                # If this follows an Under 3 Fee line and we don't have original amount yet
                if (financial_data['original_amount'] is None and i > 0 and 
                    'Under 3 Fee' in lines[i-1]):
                    amount_match = re.search(r'\$(\d+\.\d{2})', line_clean)
                    if amount_match:
                        financial_data['original_amount'] = Decimal(amount_match.group(1))
                        print(f"✅ Original Amount (standalone): ${financial_data['original_amount']}")
                
                # If this follows a Fee Discount line and we don't have discount amount yet
                if (financial_data['discount_amount'] is None and i > 0 and 
                    'Fee Discount' in lines[i-1]):
                    discount_match = re.search(r'-\$(\d+\.\d{2})', line_clean)
                    if discount_match:
                        financial_data['discount_amount'] = Decimal(discount_match.group(1))
                        print(f"✅ Discount Amount (standalone): -${financial_data['discount_amount']}")
        
        # Calculate week amount due
        if (financial_data['original_amount'] is not None and 
            financial_data['discount_amount'] is not None):
            financial_data['week_amount_due'] = (
                financial_data['original_amount'] - financial_data['discount_amount']
            )
            print(f"\n🧮 CALCULATED Week Amount Due: ${financial_data['week_amount_due']}")
        
        print(f"\n📈 FINAL FINANCIAL BREAKDOWN:")
        print("-" * 35)
        for key, value in financial_data.items():
            if value is not None:
                if 'percentage' in key:
                    print(f"✅ {key.replace('_', ' ').title()}: {value}%")
                else:
                    print(f"✅ {key.replace('_', ' ').title()}: ${value}")
            else:
                print(f"❌ {key.replace('_', ' ').title()}: Not found")
        
        print(f"\n🧮 FINANCIAL VERIFICATION:")
        print("-" * 25)
        
        # Verify discount calculation
        if financial_data['original_amount'] and financial_data['discount_percentage']:
            calculated_discount = financial_data['original_amount'] * (financial_data['discount_percentage'] / 100)
            print(f"Expected discount: ${calculated_discount:.2f}")
            if financial_data['discount_amount']:
                print(f"Actual discount: ${financial_data['discount_amount']}")
                if abs(calculated_discount - financial_data['discount_amount']) < 0.01:
                    print("✅ Discount calculation CORRECT!")
                else:
                    print("❌ Discount calculation mismatch")
        
        # Verify total calculation
        if (financial_data['week_amount_due'] and 
            financial_data['previous_balance'] and 
            financial_data['total_amount_due']):
            calculated_total = financial_data['week_amount_due'] + financial_data['previous_balance']
            print(f"\nWeek due + Previous balance: ${calculated_total:.2f}")
            print(f"Actual total due: ${financial_data['total_amount_due']}")
            if abs(calculated_total - financial_data['total_amount_due']) < 0.01:
                print("✅ Total calculation CORRECT!")
            else:
                print("❌ Total calculation mismatch")
        
        return financial_data
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    result = enhanced_sofia_analysis()
    
    if result:
        print(f"\n🎯 KEY INSIGHTS FOR YOUR REQUIREMENTS:")
        print("-" * 45)
        
        if result['week_amount_due']:
            print(f"📅 Weekly Invoice Amount: ${result['week_amount_due']}")
            print("   (This is the amount due for JUST this week's services)")
        
        if result['total_amount_due']:
            print(f"📊 Total Amount Due: ${result['total_amount_due']}")
            print("   (This includes previous unpaid balance + this week)")
        
        if result['previous_balance']:
            print(f"📋 Previous Unpaid Balance: ${result['previous_balance']}")
            print("   (This should be tracked from previous invoices)")
        
        print(f"\n💡 SYSTEM DESIGN RECOMMENDATION:")
        print("- Store 'week_amount_due' as the main invoice amount")
        print("- Track 'previous_balance' separately for running totals")
        print("- Display both weekly and cumulative totals in UI")
        print("- Calculate discount percentage accurately from original amount")
