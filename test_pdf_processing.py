#!/usr/bin/env python
"""
Test PDF processing improvements
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'daycare_tracker.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from invoices.utils import parse_invoice_data, extract_amount_from_text

def test_amount_extraction():
    """Test improved amount extraction patterns"""
    print("🧪 TESTING AMOUNT EXTRACTION")
    print("=" * 50)
    
    test_texts = [
        "AMOUNT DUE: $32.90",
        "TOTAL: $125.50",
        "DUE: $87.25",
        "BALANCE DUE: $156.75",
        "Final Amount: $245.00",
        "You owe $99.99 for this period"
    ]
    
    for text in test_texts:
        print(f"\nTesting text: '{text}'")
        parsed = parse_invoice_data(text)
        print(f"Extracted amount_due: ${parsed['amount_due']}")

def test_child_name_extraction():
    """Test child name and reference extraction"""
    print("\n🧪 TESTING CHILD EXTRACTION")
    print("=" * 50)
    
    test_texts = [
        "Child: Emma Smith",
        "Student Name: John Doe", 
        "For: Sarah Johnson",
        "Child ID: CH123",
        "Student Reference: ST456"
    ]
    
    for text in test_texts:
        print(f"\nTesting text: '{text}'")
        parsed = parse_invoice_data(text)
        print(f"Extracted child_name: '{parsed['child_name']}'")
        print(f"Extracted child_reference: '{parsed['child_reference']}'")

if __name__ == '__main__':
    test_amount_extraction()
    test_child_name_extraction()
    print("\n🎉 PDF PROCESSING TESTING COMPLETE!")
    print("Check the debug output above to see the enhanced extraction patterns working.")
