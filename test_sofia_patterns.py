#!/usr/bin/env python
"""
Test updated PDF processing patterns with Sofia's PDF
"""

import re
from decimal import Decimal
from datetime import datetime

def parse_date_string(date_str: str):
    """Test date parsing"""
    date_formats = [
        '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
        '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d',
        '%d/%m/%y', '%m/%d/%y', '%y/%m/%d',
        '%d-%m-%y', '%m-%d-%y', '%y-%m-%d',
        '%d %B %Y',  # Format for "25 August 2025"
        '%d %b %Y',  # Format for "25 Aug 2025"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None

def test_sofia_patterns():
    """Test patterns against Sofia's PDF text"""
    sofia_text = """Statement for Sofia Green-SG300

Active Explorers Ashburton requires payments for fees to be paid on a weekly basis as per
our terms of trade. Our preferred method of payment is direct credit into 12-3244-0038754-
19 quoting your child's reference number SG300

Remittance Advice - Please detach this and return with your payment 
Statement / Tax Invoice
To: Dmitry Green & Erika Green From: Active Explorers Ashburton
65 Acton Road 23-25 Archibald Street,Tinwald
Rd 11
Rakaia 7781 Ashburton 7700
Licence
Number:70566
Issued: 25 August 2025 Period: 25 Aug 2025 - 29 Aug 2025
Attention: Dmitry Green & Erika Green GST No: 100-434-210
Item Description Type Ref Date Debit Credit
Previous Balance $86.52
1Under 3 Fee May 2025 23 Aug-29 Aug INV 78352
6929 Aug 2025 $321.75
2Fee Discount of 75.00% INV 78352
6929 Aug 2025 -$241.31
Amount due (GST incl) $166.96
To: Active Explorers Ashburton From: Dmitry Green & Erika Green
23-25 Archibald Street,Tinwald 65 Acton Road
Rd 11
Ashburton 7700 Rakaia 7781
Name: Sofia Green Amount due
(GST incl)$166.96
Reference: SG300 Amount Paid: __________"""

    text_upper = sofia_text.upper()
    print("🔍 TESTING SOFIA'S PDF PATTERNS")
    print("=" * 50)
    
    # Test child name extraction
    print("\n👶 CHILD NAME EXTRACTION:")
    child_patterns_upper = [
        r'CHILD\s*NAME\s*:\s*([A-Z\s]+)',
        r'STUDENT\s*NAME\s*:\s*([A-Z\s]+)',
        r'CHILD\s*:\s*([A-Z\s]+)',
        r'FOR\s*:\s*([A-Z\s]+)',
        r'STATEMENT\s+FOR\s+([A-Z\s]+?)(?:-\w+)?',  # Pattern for "Statement for Sofia Green-SG300"
        r'NAME\s*:\s*([A-Z\s]+)',  # Pattern for "Name: Sofia Green"
    ]
    
    for pattern in child_patterns_upper:
        match = re.search(pattern, text_upper)
        if match:
            name_part = match.group(1).strip()
            child_name = ' '.join(word.capitalize() for word in name_part.split())
            print(f"  ✅ Found: '{child_name}' using pattern: {pattern}")
        else:
            print(f"  ❌ No match for pattern: {pattern}")
    
    # Test child reference extraction
    print("\n🏷️ CHILD REFERENCE EXTRACTION:")
    ref_patterns = [
        r'CHILD\s*(?:REF|REFERENCE|ID|NO)\s*:\s*(\w+)',
        r'STUDENT\s*(?:REF|REFERENCE|ID|NO)\s*:\s*(\w+)',
        r'(?:REFERENCE|REF)\s*:\s*(\w+)',
        r'(?:ID|NO)\s*:\s*(\w+)',
        r'STATEMENT\s+FOR\s+[A-Z\s]+-(\w+)',  # Pattern for "Statement for Sofia Green-SG300"
        r'REFERENCE\s+NUMBER\s+(\w+)',  # Pattern for "reference number SG300"
    ]
    
    for pattern in ref_patterns:
        match = re.search(pattern, text_upper)
        if match:
            print(f"  ✅ Found: '{match.group(1)}' using pattern: {pattern}")
        else:
            print(f"  ❌ No match for pattern: {pattern}")
    
    # Test invoice reference extraction
    print("\n📋 INVOICE REFERENCE EXTRACTION:")
    invoice_patterns = [
        r'INVOICE\s*(?:NO|NUMBER|#)?\s*:?\s*(\w+[\w\-]*)',
        r'REFERENCE\s*(?:NO|NUMBER)?\s*:?\s*(\w+[\w\-]*)',
        r'INV\s*(?:NO|#)?\s*:?\s*(\w+[\w\-]*)',
        r'INV\s+(\d+)',  # Pattern for "INV 78352"
        r'REF\s+(\w+)',   # Pattern for "REF 78352"
    ]
    
    for pattern in invoice_patterns:
        match = re.search(pattern, text_upper)
        if match:
            print(f"  ✅ Found: '{match.group(1)}' using pattern: {pattern}")
        else:
            print(f"  ❌ No match for pattern: {pattern}")
    
    # Test date extraction
    print("\n📅 DATE EXTRACTION:")
    date_patterns = {
        'issue_date': [
            r'ISSUE\s*DATE\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'DATE\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'INVOICE\s*DATE\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'ISSUED\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})',  # Pattern for "Issued: 25 August 2025"
        ],
        'period_start': [
            r'PERIOD\s*FROM\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'FROM\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'PERIOD\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})',  # Pattern for "Period: 25 Aug 2025"
        ],
        'period_end': [
            r'PERIOD\s*TO\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'TO\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'PERIOD\s*:?\s*\d{1,2}\s+\w+\s+\d{4}\s*-\s*(\d{1,2}\s+\w+\s+\d{4})',  # Pattern for period end
        ]
    }
    
    for date_key, patterns in date_patterns.items():
        print(f"  {date_key}:")
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                date_str = match.group(1)
                parsed_date = parse_date_string(date_str)
                print(f"    ✅ Found: '{date_str}' -> {parsed_date} using pattern: {pattern}")
            else:
                print(f"    ❌ No match for pattern: {pattern}")
    
    # Test amount extraction
    print("\n💰 AMOUNT EXTRACTION:")
    amount_patterns = {
        'amount_due': [
            r'TOTAL\s*(?:DUE|AMOUNT)?\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'AMOUNT\s*DUE\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'FINAL\s*AMOUNT\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'DUE\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'BALANCE\s*DUE\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'OUTSTANDING\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'AMOUNT\s+DUE\s*\(\w+\s+\w+\)\s*\$(\d{1,3}(?:\.\d{2})?)',  # Pattern for "Amount due (GST incl) $166.96"
        ],
        'discount_amount': [
            r'DISCOUNT\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'REDUCTION\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'FEE\s+DISCOUNT.*?-\$(\d{1,3}(?:\.\d{2})?)',  # Pattern for "Fee Discount of 75.00% ... -$241.31"
        ]
    }
    
    for amount_key, patterns in amount_patterns.items():
        print(f"  {amount_key}:")
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = Decimal(amount_str)
                    print(f"    ✅ Found: ${amount} using pattern: {pattern}")
                except:
                    print(f"    ❌ Found but failed to parse: '{amount_str}' using pattern: {pattern}")
            else:
                print(f"    ❌ No match for pattern: {pattern}")
    
    # Test fee type extraction
    print("\n🏷️ FEE TYPE EXTRACTION:")
    fee_patterns = [
        r'FEE\s*TYPE\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'SERVICE\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'DESCRIPTION\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(UNDER\s+\d+\s+FEE)',  # Pattern for "Under 3 Fee"
        r'(\d+\w*\s+FEE)',  # Pattern for fee types like "3 Fee", "Under3 Fee"
    ]
    
    for pattern in fee_patterns:
        match = re.search(pattern, sofia_text, re.IGNORECASE)
        if match:
            print(f"  ✅ Found: '{match.group(1).strip()}' using pattern: {pattern}")
        else:
            print(f"  ❌ No match for pattern: {pattern}")

if __name__ == '__main__':
    test_sofia_patterns()
