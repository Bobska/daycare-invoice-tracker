# Utility functions for invoice processing and data extraction
import re
from decimal import Decimal
from typing import Dict, Optional, List
from datetime import datetime, date


def extract_pdf_text(pdf_file) -> str:
    """
    Extract text from PDF file (Phase 2 implementation)
    
    Args:
        pdf_file: Uploaded PDF file
        
    Returns:
        Extracted text content
    """
    # TODO: Implement PDF text extraction using PyPDF2
    # This will be implemented in Phase 2
    return ""


def parse_invoice_data(text: str) -> Dict:
    """
    Parse invoice data from extracted text (Phase 2 implementation)
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        Dictionary containing parsed invoice data
    """
    # TODO: Implement intelligent text parsing
    # This will include pattern matching for:
    # - Invoice reference numbers
    # - Dates (issue, due, period)
    # - Amounts (total, GST, discounts)
    # - Child information
    # - Provider details
    
    parsed_data = {
        'invoice_reference': '',
        'issue_date': None,
        'due_date': None,
        'period_start': None,
        'period_end': None,
        'original_amount': Decimal('0.00'),
        'amount_due': Decimal('0.00'),
        'child_reference': '',
        'fee_type': '',
    }
    
    return parsed_data


def extract_amount_from_text(text: str, pattern: str = None) -> Optional[Decimal]:
    """
    Extract monetary amounts from text
    
    Args:
        text: Text to search
        pattern: Optional regex pattern for amount extraction
        
    Returns:
        Decimal amount or None if not found
    """
    if pattern is None:
        # Default pattern for currency amounts
        pattern = r'\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
    
    match = re.search(pattern, text)
    if match:
        amount_str = match.group(1).replace(',', '')
        try:
            return Decimal(amount_str)
        except:
            pass
    
    return None


def extract_date_from_text(text: str, date_format: str = None) -> Optional[date]:
    """
    Extract dates from text
    
    Args:
        text: Text to search
        date_format: Optional date format string
        
    Returns:
        Date object or None if not found
    """
    # Common date patterns
    date_patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        r'(\d{1,2}\s+\w+\s+\d{2,4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            # Try common date formats
            for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d %B %Y', '%d %b %Y']:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
    
    return None


def validate_invoice_reference(reference: str) -> bool:
    """
    Validate invoice reference format
    
    Args:
        reference: Invoice reference string
        
    Returns:
        True if valid format
    """
    if not reference or len(reference.strip()) < 3:
        return False
    
    # Allow alphanumeric characters, hyphens, and underscores
    pattern = r'^[A-Za-z0-9\-_]+$'
    return bool(re.match(pattern, reference.strip()))


def calculate_discount_amount(original_amount: Decimal, discount_percentage: Decimal) -> Decimal:
    """
    Calculate discount amount from percentage
    
    Args:
        original_amount: Original invoice amount
        discount_percentage: Discount percentage (0-100)
        
    Returns:
        Calculated discount amount
    """
    if discount_percentage < 0 or discount_percentage > 100:
        return Decimal('0.00')
    
    return (original_amount * discount_percentage) / Decimal('100')


def format_currency(amount: Decimal) -> str:
    """
    Format decimal amount as currency string
    
    Args:
        amount: Decimal amount
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def generate_invoice_summary(invoice) -> Dict:
    """
    Generate summary information for an invoice
    
    Args:
        invoice: Invoice model instance
        
    Returns:
        Dictionary with summary information
    """
    return {
        'reference': invoice.invoice_reference,
        'child_name': invoice.child.name,
        'provider': invoice.child.daycare_provider.name,
        'period': f"{invoice.period_start.strftime('%b %d')} - {invoice.period_end.strftime('%b %d, %Y')}",
        'amount_due': format_currency(invoice.amount_due),
        'total_paid': format_currency(invoice.total_paid),
        'outstanding': format_currency(invoice.outstanding_balance),
        'status': invoice.get_payment_status_display(),
        'days_since_issue': (date.today() - invoice.issue_date).days,
    }


# Email automation utilities (for future phases)
def extract_invoice_from_email(email_content: str) -> Dict:
    """
    Extract invoice information from email content (Phase 3+)
    
    Args:
        email_content: Raw email content
        
    Returns:
        Dictionary with extracted invoice data
    """
    # TODO: Implement email parsing for automatic invoice detection
    return {}


def match_email_to_provider(sender_email: str, subject: str) -> Optional[int]:
    """
    Match email to daycare provider (Phase 3+)
    
    Args:
        sender_email: Email sender address
        subject: Email subject line
        
    Returns:
        Provider ID if match found, None otherwise
    """
    # TODO: Implement provider matching logic
    return None
