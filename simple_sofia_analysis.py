#!/usr/bin/env python
"""
Simple Sofia PDF Analysis - No Django dependencies
"""

import PyPDF2
import re
from decimal import Decimal

def analyze_sofia_pdf():
    """Analyze the Sofia PDF to understand extraction issues"""
    pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
    
    print("🔍 ANALYZING SOFIA'S PDF")
    print("=" * 50)
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"📄 Number of pages: {len(pdf_reader.pages)}")
            
            all_text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                all_text += page_text + "\n"
                print(f"\n=== PAGE {page_num + 1} TEXT ===")
                print(page_text)
                print(f"\n=== PAGE {page_num + 1} RAW REPR ===")
                print(repr(page_text))
            
            print(f"\n📝 COMBINED TEXT LENGTH: {len(all_text)}")
            print(f"\n📝 COMBINED TEXT:")
            print(repr(all_text))
            
            # Try to find patterns in the text
            print(f"\n🔍 PATTERN ANALYSIS:")
            print("-" * 30)
            
            # Look for dates
            date_patterns = [
                r'\b(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})\b',
                r'\b(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})\b',
                r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\b',
                r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})\b'
            ]
            
            print("🗓️ Date matches:")
            for pattern in date_patterns:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                if matches:
                    print(f"  Pattern {pattern}: {matches}")
            
            # Look for amounts
            amount_patterns = [
                r'[\$£€]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*[\$£€]',
                r'Total[:\s]*[\$£€]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'Amount[:\s]*[\$£€]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
            ]
            
            print("\n💰 Amount matches:")
            for pattern in amount_patterns:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                if matches:
                    print(f"  Pattern {pattern}: {matches}")
            
            # Look for invoice references
            ref_patterns = [
                r'Invoice[:\s#]*([A-Z0-9\-]+)',
                r'Reference[:\s#]*([A-Z0-9\-]+)',
                r'Invoice\s*Number[:\s#]*([A-Z0-9\-]+)',
                r'#([A-Z0-9\-]{3,})'
            ]
            
            print("\n📋 Reference matches:")
            for pattern in ref_patterns:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                if matches:
                    print(f"  Pattern {pattern}: {matches}")
            
            # Look for fee types
            fee_patterns = [
                r'(Childcare|Daycare|Care|Nursery|Fees?)',
                r'(Daily|Weekly|Monthly)\s+(Rate|Fee|Charge)',
                r'(Before|After)\s+School\s+(Care|Program)'
            ]
            
            print("\n🏷️ Fee type matches:")
            for pattern in fee_patterns:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                if matches:
                    print(f"  Pattern {pattern}: {matches}")
            
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    analyze_sofia_pdf()
