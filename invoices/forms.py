# Invoice-related forms for future development
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Invoice, Payment, Child, DaycareProvider


class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices with enhanced financial tracking"""
    
    class Meta:
        model = Invoice
        fields = [
            'child', 'invoice_reference', 'period_start', 'period_end',
            'issue_date', 'due_date', 'original_amount', 'discount_percentage',
            'discount_amount', 'previous_balance', 'week_amount_due', 
            'total_amount_due', 'fee_type', 'pdf_file'
        ]
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter children to only show user's children
            self.fields['child'].queryset = Child.objects.filter(user=user)
        
        # Make discount and calculated fields optional with default values
        self.fields['discount_percentage'].required = False
        self.fields['discount_amount'].required = False
        self.fields['previous_balance'].required = False
        self.fields['week_amount_due'].required = False
        self.fields['total_amount_due'].required = False
        
        # Set default values
        self.fields['discount_percentage'].initial = 0.00
        self.fields['discount_amount'].initial = 0.00
        self.fields['previous_balance'].initial = 0.00
        self.fields['week_amount_due'].initial = 0.00
        self.fields['total_amount_due'].initial = 0.00
        
        # Add help text for new fields
        self.fields['previous_balance'].help_text = "Previous unpaid balance from prior invoices"
        self.fields['week_amount_due'].help_text = "Amount due for this week only (calculated automatically)"
        self.fields['total_amount_due'].help_text = "Total amount including previous balance (calculated automatically)"
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('child', css_class='form-group col-md-6 mb-0'),
                Column('invoice_reference', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('period_start', css_class='form-group col-md-6 mb-0'),
                Column('period_end', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('issue_date', css_class='form-group col-md-6 mb-0'),
                Column('due_date', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('original_amount', css_class='form-group col-md-6 mb-0'),
                Column('discount_percentage', css_class='form-group col-md-3 mb-0'),
                Column('discount_amount', css_class='form-group col-md-3 mb-0'),
            ),
            Row(
                Column('previous_balance', css_class='form-group col-md-4 mb-0'),
                Column('week_amount_due', css_class='form-group col-md-4 mb-0'),
                Column('total_amount_due', css_class='form-group col-md-4 mb-0'),
            ),
            'fee_type',
            'pdf_file',
            Submit('submit', 'Save Invoice', css_class='btn btn-primary')
        )


class PaymentForm(forms.ModelForm):
    """Form for recording payments (Phase 2)"""
    
    class Meta:
        model = Payment
        fields = [
            'invoice', 'payment_date', 'amount_paid', 'payment_method',
            'reference_number', 'notes'
        ]
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter invoices to only show user's invoices
            self.fields['invoice'].queryset = Invoice.objects.filter(
                child__user=user
            ).select_related('child')
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('invoice', css_class='form-group col-md-6 mb-0'),
                Column('payment_date', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('amount_paid', css_class='form-group col-md-6 mb-0'),
                Column('payment_method', css_class='form-group col-md-6 mb-0'),
            ),
            'reference_number',
            'notes',
            Submit('submit', 'Record Payment', css_class='btn btn-success')
        )


class ChildForm(forms.ModelForm):
    """Form for managing children (Phase 2)"""
    
    class Meta:
        model = Child
        fields = [
            'name', 'reference_number', 'date_of_birth',
            'daycare_provider', 'is_active'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('reference_number', css_class='form-group col-md-6 mb-0'),
            ),
            Row(
                Column('date_of_birth', css_class='form-group col-md-6 mb-0'),
                Column('daycare_provider', css_class='form-group col-md-6 mb-0'),
            ),
            'is_active',
            Submit('submit', 'Save Child', css_class='btn btn-info')
        )
