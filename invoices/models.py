from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from decimal import Decimal

User = get_user_model()


def default_list():
    """Return empty list for JSONField default"""
    return []


class DaycareProvider(models.Model):
    """Daycare provider information"""
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    bank_details = models.TextField(blank=True)
    
    # Future email automation fields
    email_addresses = models.JSONField(
        default=default_list,
        blank=True,
        help_text="Known email addresses for automatic invoice detection"
    )
    email_subject_patterns = models.JSONField(
        default=default_list,
        blank=True,
        help_text="Email subject patterns to identify invoices"
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Child(models.Model):
    """Child information for invoice tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    reference_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    daycare_provider = models.ForeignKey(DaycareProvider, on_delete=models.CASCADE, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.reference_number})"
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'reference_number', 'daycare_provider']


class Invoice(models.Model):
    """Invoice information and tracking"""
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='invoices')
    invoice_reference = models.CharField(max_length=50)
    
    # Invoice period
    period_start = models.DateField()
    period_end = models.DateField()
    issue_date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    
    # Financial details
    original_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Enhanced financial tracking
    previous_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Previous unpaid balance carried forward"
    )
    week_amount_due = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Amount due for this week only (excluding previous balance)"
    )
    total_amount_due = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Total amount due including previous balance"
    )
    
    # Legacy field - keeping for backward compatibility
    amount_due = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Legacy field - use total_amount_due instead"
    )
    
    # Status and tracking
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    fee_type = models.CharField(max_length=100, blank=True)
    
    # File handling
    pdf_file = models.FileField(upload_to='invoices/%Y/%m/', null=True, blank=True)
    
    # Future email automation fields
    extracted_from_email = models.BooleanField(default=False)
    email_message_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice {self.invoice_reference} - {self.child.name}"
    
    def clean(self):
        """Enhanced model validation"""
        errors = {}
        
        # Validate amount fields
        if self.amount_due and self.amount_due <= 0:
            errors['amount_due'] = 'Amount due must be greater than zero.'
        
        if self.original_amount and self.original_amount <= 0:
            errors['original_amount'] = 'Original amount must be greater than zero.'
        
        # Validate discount logic
        if self.discount_amount and self.original_amount:
            if self.discount_amount > self.original_amount:
                errors['discount_amount'] = 'Discount amount cannot exceed original amount.'
        
        if self.discount_percentage and (self.discount_percentage < 0 or self.discount_percentage > 100):
            errors['discount_percentage'] = 'Discount percentage must be between 0 and 100.'
        
        # Validate date logic
        if self.period_start and self.period_end and self.period_start >= self.period_end:
            errors['period_end'] = 'Period end date must be after start date.'
        
        if self.issue_date and self.due_date and self.due_date < self.issue_date:
            errors['due_date'] = 'Due date cannot be before issue date.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        """Override save to ensure validation and calculations"""
        # Auto-calculate week_amount_due if not provided
        if self.original_amount and not self.week_amount_due:
            discount = self.discount_amount or Decimal('0.00')
            self.week_amount_due = self.original_amount - discount
        
        # Auto-calculate total_amount_due if not provided
        if self.week_amount_due and not self.total_amount_due:
            previous = self.previous_balance or Decimal('0.00')
            self.total_amount_due = self.week_amount_due + previous
        
        # Keep legacy amount_due field in sync with total_amount_due
        if self.total_amount_due:
            self.amount_due = self.total_amount_due
        
        # Full clean validation
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def total_paid(self):
        """Calculate total amount paid for this invoice"""
        return self.payments.aggregate(
            total=models.Sum('amount_paid')
        )['total'] or Decimal('0.00')
    
    @property
    def outstanding_balance(self):
        """Calculate remaining balance (total)"""
        return self.total_amount_due - self.total_paid
    
    @property
    def week_outstanding_balance(self):
        """Calculate remaining balance for this week only"""
        total_paid = self.total_paid
        # First apply payments to previous balance, then to current week
        if total_paid >= self.previous_balance:
            week_paid = total_paid - self.previous_balance
            return max(Decimal('0.00'), self.week_amount_due - week_paid)
        else:
            return self.week_amount_due  # No payments applied to current week yet
    
    def update_payment_status(self):
        """Update payment status based on payments"""
        total_paid = self.total_paid
        if total_paid >= self.total_amount_due:
            self.payment_status = 'paid'
        elif total_paid > 0:
            self.payment_status = 'partial'
        else:
            self.payment_status = 'unpaid'
        self.save()
    
    class Meta:
        ordering = ['-issue_date']
        unique_together = ['child', 'invoice_reference']


class Payment(models.Model):
    """Payment records for invoices"""
    PAYMENT_METHOD_CHOICES = [
        ('direct_credit', 'Direct Credit'),
        ('cash', 'Cash'),
        ('eftpos', 'EFTPOS'),
        ('credit_card', 'Credit Card'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        """Payment validation"""
        errors = {}
        
        if self.amount_paid and self.amount_paid <= 0:
            errors['amount_paid'] = 'Payment amount must be greater than zero.'
        
        # Validate payment doesn't exceed invoice amount
        if self.invoice and self.amount_paid:
            existing_payments = Payment.objects.filter(
                invoice=self.invoice
            ).exclude(pk=self.pk).aggregate(
                total=models.Sum('amount_paid')
            )['total'] or Decimal('0.00')
            
            total_with_new = existing_payments + self.amount_paid
            if total_with_new > self.invoice.amount_due:
                overpayment = total_with_new - self.invoice.amount_due
                errors['amount_paid'] = f'Payment would result in overpayment of ${overpayment:.2f}.'
        
        if errors:
            raise ValidationError(errors)
    
    def save(self, *args, **kwargs):
        # Validate before saving
        self.full_clean()
        super().save(*args, **kwargs)
        # Update invoice payment status
        self.invoice.update_payment_status()
    
    def __str__(self):
        return f"Payment ${self.amount_paid} - {self.invoice.invoice_reference}"
    
    class Meta:
        ordering = ['-payment_date']
