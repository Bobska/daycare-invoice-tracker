# Utility functions for invoice processing and data extraction
import re
from decimal import Decimal
from typing import Dict, Optional, List
from datetime import datetime, date
import PyPDF2
import logging

logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_file) -> str:
    """
    Extract text from PDF file using PyPDF2
    
    Args:
        pdf_file: Uploaded PDF file
        
    Returns:
        Extracted text content
    """
    try:
        # Reset file pointer to beginning
        pdf_file.seek(0)
        
        # Create PDF reader
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        
        # Extract text from all pages
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n"
        
        logger.info(f"Successfully extracted text from PDF: {len(text)} characters")
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        return ""


def parse_invoice_data(text: str) -> Dict:
    """
    Parse invoice data from extracted text using pattern recognition
    
    Args:
        text: Extracted text from PDF
        
    Returns:
        Dictionary containing parsed invoice data
    """
    parsed_data = {
        'invoice_reference': '',
        'issue_date': None,
        'due_date': None,
        'period_start': None,
        'period_end': None,
        'original_amount': Decimal('0.00'),
        'amount_due': Decimal('0.00'),
        'discount_amount': Decimal('0.00'),
        'discount_percentage': Decimal('0.00'),
        'child_reference': '',
        'child_name': '',
        'fee_type': '',
        'provider_name': '',
    }
    
    # Normalize text for better pattern matching
    text_lines = [line.strip() for line in text.split('\n') if line.strip()]
    text_upper = text.upper()
    
    # Extract invoice reference number
    invoice_patterns = [
        r'INVOICE\s*(?:NO|NUMBER|#)?\s*:?\s*(\w+[\w\-]*)',
        r'REFERENCE\s*(?:NO|NUMBER)?\s*:?\s*(\w+[\w\-]*)',
        r'INV\s*(?:NO|#)?\s*:?\s*(\w+[\w\-]*)',
    ]
    
    for pattern in invoice_patterns:
        match = re.search(pattern, text_upper)
        if match:
            parsed_data['invoice_reference'] = match.group(1)
            break
    
    # Extract child name and reference
    child_patterns = [
        r'CHILD\s*(?:NAME)?\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'STUDENT\s*(?:NAME)?\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'(?:FOR|CHILD):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in child_patterns:
        match = re.search(pattern, text)
        if match:
            parsed_data['child_name'] = match.group(1).strip()
            break
    
    # Extract child reference number
    ref_patterns = [
        r'CHILD\s*(?:REF|REFERENCE|ID|NO)\s*:?\s*(\w+)',
        r'STUDENT\s*(?:REF|REFERENCE|ID|NO)\s*:?\s*(\w+)',
        r'ID\s*:?\s*(\w+)',
    ]
    
    for pattern in ref_patterns:
        match = re.search(pattern, text_upper)
        if match:
            parsed_data['child_reference'] = match.group(1)
            break
    
    # Extract dates
    date_patterns = {
        'issue_date': [
            r'ISSUE\s*DATE\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'DATE\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'INVOICE\s*DATE\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ],
        'due_date': [
            r'DUE\s*DATE\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'PAYMENT\s*DUE\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ],
        'period_start': [
            r'PERIOD\s*FROM\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'FROM\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ],
        'period_end': [
            r'PERIOD\s*TO\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'TO\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        ]
    }
    
    for date_key, patterns in date_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                parsed_date = parse_date_string(match.group(1))
                if parsed_date:
                    parsed_data[date_key] = parsed_date
                    break
        if parsed_data[date_key]:
            break
    
    # Extract amounts
    amount_patterns = {
        'original_amount': [
            r'SUBTOTAL\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'AMOUNT\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'TOTAL\s*(?:BEFORE|GROSS)\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ],
        'amount_due': [
            r'TOTAL\s*(?:DUE|AMOUNT)\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'AMOUNT\s*DUE\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'FINAL\s*AMOUNT\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ],
        'discount_amount': [
            r'DISCOUNT\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'REDUCTION\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]
    }
    
    for amount_key, patterns in amount_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    parsed_data[amount_key] = Decimal(amount_str)
                    break
                except:
                    continue
        if parsed_data[amount_key] != Decimal('0.00'):
            break
    
    # Extract discount percentage
    discount_pct_pattern = r'DISCOUNT\s*:?\s*(\d{1,2})%'
    match = re.search(discount_pct_pattern, text_upper)
    if match:
        try:
            parsed_data['discount_percentage'] = Decimal(match.group(1))
        except:
            pass
    
    # Extract fee type
    fee_patterns = [
        r'FEE\s*TYPE\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'SERVICE\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'DESCRIPTION\s*:?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
    ]
    
    for pattern in fee_patterns:
        match = re.search(pattern, text)
        if match:
            parsed_data['fee_type'] = match.group(1).strip()
            break
    
    # Extract provider name (usually at the top of the invoice)
    for line in text_lines[:5]:  # Check first 5 lines
        if len(line) > 10 and 'DAYCARE' in line.upper() or 'CHILDCARE' in line.upper():
            parsed_data['provider_name'] = line.strip()
            break
    
    logger.info(f"Parsed invoice data: {parsed_data}")
    return parsed_data


def parse_date_string(date_str: str) -> Optional[date]:
    """
    Parse a date string into a date object
    
    Args:
        date_str: Date string to parse
        
    Returns:
        Date object or None if parsing fails
    """
    date_formats = [
        '%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d',
        '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d',
        '%d/%m/%y', '%m/%d/%y', '%y/%m/%d',
        '%d-%m-%y', '%m-%d-%y', '%y-%m-%d',
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None


def extract_amount_from_text(text: str, pattern: Optional[str] = None) -> Optional[Decimal]:
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


def extract_date_from_text(text: str, date_format: Optional[str] = None) -> Optional[date]:
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


# File validation utilities
def validate_pdf_file(file) -> Dict[str, str]:
    """
    Validate uploaded PDF file
    
    Args:
        file: Uploaded file object
        
    Returns:
        Dictionary with validation results (errors if any)
    """
    errors = {}
    
    # Check file extension
    if not file.name.lower().endswith('.pdf'):
        errors['file_type'] = 'Only PDF files are allowed.'
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file.size > max_size:
        errors['file_size'] = f'File size must be less than 10MB. Current size: {file.size / (1024*1024):.1f}MB'
    
    # Check if file is empty
    if file.size == 0:
        errors['file_empty'] = 'File appears to be empty.'
    
    # Try to read PDF content
    if not errors:
        try:
            file.seek(0)
            pdf_reader = PyPDF2.PdfReader(file)
            if len(pdf_reader.pages) == 0:
                errors['pdf_invalid'] = 'PDF file contains no pages.'
        except Exception as e:
            errors['pdf_corrupt'] = f'PDF file appears to be corrupted: {str(e)}'
        finally:
            file.seek(0)  # Reset file pointer
    
    return errors


def process_uploaded_invoice(pdf_file, user) -> Dict:
    """
    Process uploaded invoice PDF and extract data
    
    Args:
        pdf_file: Uploaded PDF file
        user: User uploading the file
        
    Returns:
        Dictionary with processing results
    """
    result = {
        'success': False,
        'data': {},
        'errors': {},
        'warnings': []
    }
    
    # Validate file
    validation_errors = validate_pdf_file(pdf_file)
    if validation_errors:
        result['errors'] = validation_errors
        return result
    
    try:
        # Extract text from PDF
        text = extract_pdf_text(pdf_file)
        
        if not text:
            result['warnings'].append('No text could be extracted from PDF. Manual entry will be required.')
            result['success'] = True
            return result
        
        # Parse invoice data
        parsed_data = parse_invoice_data(text)
        
        # Validate parsed data
        if not parsed_data.get('invoice_reference'):
            result['warnings'].append('Invoice reference number could not be extracted.')
        
        if not parsed_data.get('amount_due') or parsed_data['amount_due'] == Decimal('0.00'):
            result['warnings'].append('Invoice amount could not be extracted.')
        
        # Try to match child
        if parsed_data.get('child_reference') or parsed_data.get('child_name'):
            from .models import Child
            
            child_query = Child.objects.filter(user=user)
            if parsed_data.get('child_reference'):
                child_query = child_query.filter(reference_number__icontains=parsed_data['child_reference'])
            elif parsed_data.get('child_name'):
                child_query = child_query.filter(name__icontains=parsed_data['child_name'])
            
            child = child_query.first()
            if child:
                parsed_data['matched_child_id'] = child.pk
            else:
                result['warnings'].append('Could not match extracted child information to existing children.')
        
        result['success'] = True
        result['data'] = parsed_data
        
    except Exception as e:
        logger.error(f"Error processing uploaded invoice: {str(e)}")
        result['errors']['processing'] = f'Error processing PDF: {str(e)}'
    
    return result
