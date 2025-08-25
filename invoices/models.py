from django.db import models
from django.contrib.auth import get_user_model
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
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    
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
    
    @property
    def total_paid(self):
        """Calculate total amount paid for this invoice"""
        return self.payments.aggregate(
            total=models.Sum('amount_paid')
        )['total'] or Decimal('0.00')
    
    @property
    def outstanding_balance(self):
        """Calculate remaining balance"""
        return self.amount_due - self.total_paid
    
    def update_payment_status(self):
        """Update payment status based on payments"""
        total_paid = self.total_paid
        if total_paid >= self.amount_due:
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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice payment status
        self.invoice.update_payment_status()
    
    def __str__(self):
        return f"Payment ${self.amount_paid} - {self.invoice.invoice_reference}"
    
    class Meta:
        ordering = ['-payment_date']
