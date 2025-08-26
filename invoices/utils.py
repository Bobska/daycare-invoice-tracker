# Utility functions for invoice processing and data extraction
import re
from decimal import Decimal
from typing import Dict, Optional, List
from datetime import datetime, date
import PyPDF2
import logging
import bleach

# Optional magic import for file type detection
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logging.warning("python-magic not available. File type validation will be limited.")

logger = logging.getLogger(__name__)


def sanitize_extracted_text(text: str) -> str:
    """Sanitize text extracted from PDF to prevent XSS and injection"""
    if not text:
        return ""
    
    # 1. Remove potentially malicious patterns
    # Remove script tags, HTML, SQL injection patterns
    text = bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # 2. Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # 3. Limit text length to prevent memory issues
    if len(text) > 50000:  # 50KB limit
        text = text[:50000] + "... [truncated]"
    
    return text.strip()


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
        
        # DEBUG: Print extracted text to console
        print("=== EXTRACTED PDF TEXT ===")
        print(text)
        print("=== END EXTRACTED TEXT ===")
        
        logger.info(f"Successfully extracted text from PDF: {len(text)} characters")
        
        # Sanitize extracted text for security
        sanitized_text = sanitize_extracted_text(text)
        return sanitized_text
        
    except Exception as e:
        print(f"PDF extraction error: {str(e)}")
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
    # Sanitize input text first
    text = sanitize_extracted_text(text)
    
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
    
    # Extract child name and reference (case insensitive search on uppercase text)
    child_patterns_upper = [
        r'CHILD\s*NAME\s*:\s*([A-Z\s]+)',
        r'STUDENT\s*NAME\s*:\s*([A-Z\s]+)',
        r'CHILD\s*:\s*([A-Z\s]+)',
        r'FOR\s*:\s*([A-Z\s]+)',
    ]
    
    print(f"=== CHILD NAME EXTRACTION DEBUG ===")
    print(f"Original text: '{text}'")
    print(f"Uppercase text: '{text_upper}'")
    
    for pattern in child_patterns_upper:
        match = re.search(pattern, text_upper)
        if match:
            name_part = match.group(1).strip()
            # Convert back to title case for proper name formatting
            parsed_data['child_name'] = ' '.join(word.capitalize() for word in name_part.split())
            print(f"Found child_name: '{parsed_data['child_name']}' using pattern: {pattern}")
            break
    
    if not parsed_data['child_name']:
        print("No child name found")
    
    # Extract child reference number - More specific patterns
    ref_patterns = [
        r'CHILD\s*(?:REF|REFERENCE|ID|NO)\s*:\s*(\w+)',
        r'STUDENT\s*(?:REF|REFERENCE|ID|NO)\s*:\s*(\w+)',
        r'(?:REFERENCE|REF)\s*:\s*(\w+)',
        r'(?:ID|NO)\s*:\s*(\w+)',
    ]
    
    for pattern in ref_patterns:
        match = re.search(pattern, text_upper)
        if match:
            parsed_data['child_reference'] = match.group(1)
            print(f"Found child_reference: '{parsed_data['child_reference']}' using pattern: {pattern}")
            break
    
    if not parsed_data['child_reference']:
        print("No child reference found")
    
    print(f"=== END CHILD EXTRACTION ===")
    
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
    
    # Extract amounts - Enhanced patterns for better detection
    amount_patterns = {
        'original_amount': [
            r'SUBTOTAL\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'AMOUNT\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'TOTAL\s*(?:BEFORE|GROSS)\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ],
        'amount_due': [
            r'TOTAL\s*(?:DUE|AMOUNT)?\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'AMOUNT\s*DUE\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'FINAL\s*AMOUNT\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'DUE\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Simple "DUE: $32.90"
            r'BALANCE\s*DUE\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'OUTSTANDING\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ],
        'discount_amount': [
            r'DISCOUNT\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'REDUCTION\s*:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        ]
    }
    
    print(f"=== AMOUNT EXTRACTION DEBUG ===")
    
    for amount_key, patterns in amount_patterns.items():
        print(f"Extracting {amount_key}:")
        for pattern in patterns:
            match = re.search(pattern, text_upper)
            if match:
                try:
                    amount_str = match.group(1).replace(',', '')
                    parsed_data[amount_key] = Decimal(amount_str)
                    print(f"  Found {amount_key}: ${amount_str} using pattern: {pattern}")
                    break
                except Exception as e:
                    print(f"  Error parsing amount {amount_str}: {e}")
                    continue
        if parsed_data[amount_key] == Decimal('0.00'):
            print(f"  No {amount_key} found")
    
    # Fallback: Try to find ANY dollar amount as potential amount due
    if parsed_data['amount_due'] == Decimal('0.00'):
        print("Trying fallback dollar amount extraction...")
        fallback_pattern = r'\$(\d{1,3}(?:\.\d{2})?)'
        fallback_matches = re.findall(fallback_pattern, text)
        if fallback_matches:
            # Take the largest dollar amount found
            amounts = []
            for amount_str in fallback_matches:
                try:
                    amounts.append(Decimal(amount_str))
                except:
                    continue
            if amounts:
                parsed_data['amount_due'] = max(amounts)
                print(f"  Fallback found amount_due: ${parsed_data['amount_due']}")
    
    print(f"=== END AMOUNT EXTRACTION ===")
    
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
    Enhanced PDF validation with magic number checking and security features
    
    Args:
        file: Uploaded file object
        
    Returns:
        Dictionary with validation results (errors if any)
    """
    errors = {}
    
    try:
        # Reset file pointer
        file.seek(0)
        
        # 1. Check magic number (actual file content)
        header = file.read(8)
        if not header.startswith(b'%PDF-'):
            errors['file_type'] = 'File is not a valid PDF format.'
            return errors
        
        # 2. Use python-magic for additional validation (if available)
        if MAGIC_AVAILABLE:
            file.seek(0)
            try:
                file_type = magic.from_buffer(file.read(2048), mime=True)
                if file_type != 'application/pdf':
                    errors['file_type'] = 'File content does not match PDF format.'
                    return errors
            except Exception as e:
                # Fallback if magic fails - continue with other checks
                logger.warning(f"Magic number check failed: {str(e)}")
        else:
            # Fallback validation without magic - check file extension
            if not file.name.lower().endswith('.pdf'):
                errors['file_type'] = 'Only PDF files are allowed (file extension check).'
        
        # 3. Check file size (10MB limit)
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        if size > 10 * 1024 * 1024:
            errors['file_size'] = f'File too large: {size/(1024*1024):.1f}MB. Maximum: 10MB'
        
        if size == 0:
            errors['file_empty'] = 'File appears to be empty.'
            return errors
        
        # 4. Validate PDF structure
        file.seek(0)
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            if len(pdf_reader.pages) == 0:
                errors['pdf_invalid'] = 'PDF contains no readable pages.'
        except Exception as e:
            errors['pdf_corrupt'] = f'PDF file is corrupted or invalid: {str(e)}'
        
        # 5. Reset file pointer for further processing
        file.seek(0)
        
    except Exception as e:
        errors['file_error'] = f'Error validating file: {str(e)}'
    
    return errors
    
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
        
        # Try to match child - Enhanced matching strategy
        if parsed_data.get('child_reference') or parsed_data.get('child_name'):
            from .models import Child
            
            child_query = Child.objects.filter(user=user)
            child = None
            
            print(f"=== CHILD MATCHING DEBUG ===")
            print(f"Available children for user: {[child.name for child in child_query]}")
            print(f"Extracted child_reference: '{parsed_data.get('child_reference')}'")
            print(f"Extracted child_name: '{parsed_data.get('child_name')}'")
            
            # Strategy 1: Exact reference match
            if parsed_data.get('child_reference'):
                child = child_query.filter(reference_number=parsed_data['child_reference']).first()
                if child:
                    print(f"  Strategy 1 SUCCESS: Exact reference match - {child.name}")
            
            # Strategy 2: Partial reference match
            if not child and parsed_data.get('child_reference'):
                child = child_query.filter(reference_number__icontains=parsed_data['child_reference']).first()
                if child:
                    print(f"  Strategy 2 SUCCESS: Partial reference match - {child.name}")
            
            # Strategy 3: Name matching (partial)
            if not child and parsed_data.get('child_name'):
                child = child_query.filter(name__icontains=parsed_data['child_name']).first()
                if child:
                    print(f"  Strategy 3 SUCCESS: Name match - {child.name}")
            
            # Strategy 4: If only one child exists, suggest it
            if not child and child_query.count() == 1:
                child = child_query.first()
                if child:  # Additional safety check
                    result['warnings'].append(f'Automatically selected your only child: {child.name}')
                    print(f"  Strategy 4 SUCCESS: Only child auto-selected - {child.name}")
            
            if child:
                parsed_data['matched_child_id'] = child.pk
                print(f"  FINAL MATCH: {child.name} (ID: {child.pk})")
            else:
                result['warnings'].append('Could not match extracted child information to existing children.')
                print(f"  NO MATCH FOUND")
                
            print(f"=== END CHILD MATCHING ===")
        else:
            print("No child reference or name extracted from PDF")
        
        result['success'] = True
        result['data'] = parsed_data
        
    except Exception as e:
        logger.error(f"Error processing uploaded invoice: {str(e)}")
        result['errors']['processing'] = f'Error processing PDF: {str(e)}'
    
    return result
