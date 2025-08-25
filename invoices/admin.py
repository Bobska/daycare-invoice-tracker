from django.contrib import admin
from .models import DaycareProvider, Child, Invoice, Payment


@admin.register(DaycareProvider)
class DaycareProviderAdmin(admin.ModelAdmin):
    """Admin configuration for DaycareProvider model"""
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'address', 'phone', 'email']
        }),
        ('Business Details', {
            'fields': ['license_number', 'gst_number', 'bank_details']
        }),
        ('Email Automation (Future)', {
            'fields': ['email_addresses', 'email_subject_patterns'],
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    """Admin configuration for Child model"""
    list_display = ['name', 'reference_number', 'user', 'daycare_provider', 'is_active', 'created_at']
    list_filter = ['daycare_provider', 'is_active', 'created_at']
    search_fields = ['name', 'reference_number', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = [
        ('Child Information', {
            'fields': ['user', 'name', 'reference_number', 'date_of_birth']
        }),
        ('Daycare Details', {
            'fields': ['daycare_provider']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model"""
    list_display = ['invoice_reference', 'child', 'period_start', 'period_end', 'amount_due', 'payment_status', 'issue_date']
    list_filter = ['payment_status', 'child__daycare_provider', 'issue_date', 'extracted_from_email']
    search_fields = ['invoice_reference', 'child__name', 'child__reference_number']
    readonly_fields = ['total_paid', 'outstanding_balance', 'created_at', 'updated_at']
    date_hierarchy = 'issue_date'
    
    fieldsets = [
        ('Invoice Details', {
            'fields': ['child', 'invoice_reference', 'fee_type']
        }),
        ('Period & Dates', {
            'fields': ['period_start', 'period_end', 'issue_date', 'due_date']
        }),
        ('Financial Information', {
            'fields': ['original_amount', 'discount_percentage', 'discount_amount', 'amount_due']
        }),
        ('Payment Tracking', {
            'fields': ['payment_status', 'total_paid', 'outstanding_balance'],
            'classes': ['wide']
        }),
        ('File & Email', {
            'fields': ['pdf_file', 'extracted_from_email', 'email_message_id'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queries by selecting related objects"""
        return super().get_queryset(request).select_related('child', 'child__user', 'child__daycare_provider')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model"""
    list_display = ['invoice', 'payment_date', 'amount_paid', 'payment_method', 'reference_number']
    list_filter = ['payment_method', 'payment_date', 'invoice__child__daycare_provider']
    search_fields = ['invoice__invoice_reference', 'reference_number', 'invoice__child__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'payment_date'
    
    fieldsets = [
        ('Payment Details', {
            'fields': ['invoice', 'payment_date', 'amount_paid', 'payment_method']
        }),
        ('Reference & Notes', {
            'fields': ['reference_number', 'notes']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queries by selecting related objects"""
        return super().get_queryset(request).select_related('invoice', 'invoice__child')
