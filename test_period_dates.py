#!/usr/bin/env python
"""
Test period date extraction specifically
"""

import re
from datetime import datetime

def parse_date_string(date_str: str):
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

def test_period_extraction():
    """Test period date extraction"""
    text = "ISSUED: 25 AUGUST 2025 PERIOD: 25 AUG 2025 - 29 AUG 2025"
    
    print("🔍 TESTING PERIOD DATE EXTRACTION")
    print("=" * 40)
    print(f"Text: {text}")
    print()
    
    # Test period start
    period_start_patterns = [
        r'PERIOD\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})\s*-',  # Pattern for start of "Period: 25 Aug 2025 - 29 Aug 2025"
        r'PERIOD\s*FROM\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'FROM\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    ]
    
    print("📅 Period Start:")
    for pattern in period_start_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            parsed_date = parse_date_string(date_str)
            print(f"  ✅ Found: '{date_str}' -> {parsed_date} using pattern: {pattern}")
        else:
            print(f"  ❌ No match for pattern: {pattern}")
    
    # Test period end
    period_end_patterns = [
        r'PERIOD\s*:?\s*\d{1,2}\s+\w+\s+\d{4}\s*-\s*(\d{1,2}\s+\w+\s+\d{4})',  # Pattern for period end from "Period: 25 Aug 2025 - 29 Aug 2025"
        r'PERIOD\s*TO\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'TO\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    ]
    
    print("\n📅 Period End:")
    for pattern in period_end_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            parsed_date = parse_date_string(date_str)
            print(f"  ✅ Found: '{date_str}' -> {parsed_date} using pattern: {pattern}")
        else:
            print(f"  ❌ No match for pattern: {pattern}")

if __name__ == '__main__':
    test_period_extraction()
