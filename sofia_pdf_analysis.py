#!/usr/bin/env python
"""
Sofia PDF Analysis - Debug PDF processing issues
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')
django.setup()

import PyPDF2
from invoices.utils import parse_invoice_data, extract_pdf_text

def analyze_sofia_pdf():
    """Analyze the Sofia PDF to understand extraction issues"""
    pdf_path = 'media/invoices/2025.08.25 - Sofia.pdf'
    
    print("🔍 ANALYZING SOFIA'S PDF")
    print("=" * 50)
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Step 1: Raw PDF text extraction
    print("📄 RAW PDF TEXT EXTRACTION:")
    print("-" * 30)
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"Pages: {len(pdf_reader.pages)}")
            
            raw_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                raw_text += page_text + "\n"
                print(f"\n=== PAGE {page_num + 1} ===")
                print(repr(page_text))  # Show raw representation
    
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return
    
    # Step 2: Using our extract function
    print(f"\n📝 USING OUR EXTRACT FUNCTION:")
    print("-" * 35)
    
    try:
        with open(pdf_path, 'rb') as file:
            extracted_text = extract_pdf_text(file)
            print("Extracted text length:", len(extracted_text))
            print("Extracted text:")
            print(repr(extracted_text))
    except Exception as e:
        print(f"❌ Error with extract function: {e}")
        return
    
    # Step 3: Parse the extracted data
    print(f"\n🔍 PARSING EXTRACTED DATA:")
    print("-" * 30)
    
    try:
        parsed_data = parse_invoice_data(extracted_text)
        print("Parsed results:")
        for key, value in parsed_data.items():
            print(f"  {key}: {repr(value)}")
    except Exception as e:
        print(f"❌ Error parsing data: {e}")

if __name__ == '__main__':
    analyze_sofia_pdf()
