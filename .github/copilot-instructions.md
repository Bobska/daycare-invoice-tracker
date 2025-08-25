# DayCare Invoice Tracker - Copilot Instructions

## Project Overview
This is a Django web application for managing daycare invoices, tracking payments, and maintaining records for multiple children. The system processes PDF invoices, extracts data automatically, and provides comprehensive payment tracking.

## Technology Stack
- **Backend**: Django 4.2+, Python 3.9+
- **Database**: SQLite (development), PostgreSQL (production ready)
- **Frontend**: Django templates with Bootstrap 4, vanilla JavaScript
- **File Processing**: PyPDF2 for PDF text extraction
- **Forms**: django-crispy-forms with Bootstrap styling
- **Future**: Email automation with IMAP/Celery integration planned

## Architecture & Code Style

### Django Best Practices
- Use class-based views where appropriate, function-based views for simple operations
- Always include `related_name` in ForeignKey relationships
- Use Django's built-in User model or extend AbstractUser (we use CustomUser)
- Implement `__str__` methods for all models
- Use Django's timezone-aware datetime handling
- Apply proper model validation and cleaning
- Use Django's messages framework for user feedback

### Model Design Patterns
- All models should include `created_at` and `updated_at` timestamps
- Use JSONField for flexible data storage (notification preferences, email patterns)
- Implement model methods for calculated properties (like `total_paid`, `outstanding_balance`)
- Use model managers for common querysets
- Include proper model Meta classes with ordering and unique constraints

### Code Organization
- Keep views focused and single-purpose
- Use utils.py for shared functions (PDF processing, data extraction)
- Create forms.py for all form handling
- Use descriptive variable names: `invoice_reference` not `ref`
- Group imports: Django imports, third-party imports, local imports
- Add comprehensive docstrings to all classes and methods

### Error Handling
- Always handle file upload errors gracefully
- Use Django's form validation for user input
- Log errors appropriately without exposing sensitive data
- Provide meaningful error messages to users
- Handle PDF extraction failures with fallback to manual entry

### Security Considerations
- Validate all file uploads (type, size, content)
- Use Django's CSRF protection
- Implement proper user authentication and authorization
- Sanitize user input, especially from PDF extraction
- Use environment variables for sensitive settings

## Model Relationships
```python
User (CustomUser)
├── Children (multiple per user)
    ├── Invoices (multiple per child)
        ├── Payments (multiple per invoice)

DaycareProvider
├── Children (multiple providers possible)
```

## Key Model Fields to Remember
- **Child**: user, name, reference_number, daycare_provider
- **Invoice**: child, invoice_reference, period_start/end, amounts, payment_status, pdf_file
- **Payment**: invoice, payment_date, amount_paid, payment_method
- **DaycareProvider**: name, contact info, email automation fields (future)

## File Structure Conventions
- Models: Keep related models in same file, use clear model names
- Views: Organize by functionality (dashboard, invoice management, payments)
- Templates: Use template inheritance, create reusable components
- Static files: Organize CSS/JS by functionality
- Media files: Store uploaded PDFs in date-organized folders

## Future Development Considerations
- Design models to support email automation (EmailAccount, ProcessedEmail models planned)
- Consider background task processing for PDF extraction
- Plan for multi-tenant architecture if needed
- Design API endpoints for potential mobile app integration

## Testing Approach
- Write model tests for all calculated properties and methods
- Test file upload functionality thoroughly
- Test PDF extraction with various invoice formats
- Include edge cases in payment calculation tests
- Test user authentication and authorization

## Performance Considerations
- Use select_related() and prefetch_related() for related data queries
- Implement pagination for invoice lists
- Optimize PDF processing to avoid blocking requests
- Consider caching for dashboard calculations

## Common Patterns for This Project

### Invoice Status Updates
When payments are made, always update invoice payment status:
```python
def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
    self.invoice.update_payment_status()
```

### Decimal Handling
Always use Decimal for financial calculations:
```python
from decimal import Decimal
amount = Decimal('25.50')
```

### Date Handling
Use timezone-aware dates:
```python
from django.utils import timezone
issue_date = timezone.now().date()
```

### File Upload Security
Always validate uploaded files:
```python
def validate_pdf_file(file):
    if not file.name.endswith('.pdf'):
        raise ValidationError('Only PDF files are allowed.')
```

## Response Guidelines
- Prioritize Django best practices and security
- Include comprehensive error handling
- Add helpful comments for complex business logic
- Use descriptive variable names that match the domain
- Follow the established model relationships
- Consider performance implications of database queries
- Plan for the future email automation features in model design