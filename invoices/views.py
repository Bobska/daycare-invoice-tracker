from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView
from django.db.models import Sum, Count, Q
from decimal import Decimal
from .models import Invoice, Payment, Child, DaycareProvider


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard view showing summary statistics"""
    template_name = 'invoices/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's children and related data
        user_children = Child.objects.filter(user=user)
        user_invoices = Invoice.objects.filter(child__user=user)
        user_payments = Payment.objects.filter(invoice__child__user=user)
        
        # Calculate statistics
        context['stats'] = {
            'total_children': user_children.count(),
            'total_invoices': user_invoices.count(),
            'total_payments': user_payments.count(),
            'total_amount_due': user_invoices.aggregate(
                total=Sum('amount_due')
            )['total'] or Decimal('0.00'),
            'total_paid': user_payments.aggregate(
                total=Sum('amount_paid')
            )['total'] or Decimal('0.00'),
            'unpaid_invoices': user_invoices.filter(payment_status='unpaid').count(),
            'overdue_invoices': user_invoices.filter(payment_status='overdue').count(),
        }
        
        # Calculate outstanding balance
        context['stats']['outstanding_balance'] = (
            context['stats']['total_amount_due'] - context['stats']['total_paid']
        )
        
        # Recent invoices
        context['recent_invoices'] = user_invoices.select_related(
            'child', 'child__daycare_provider'
        ).order_by('-created_at')[:5]
        
        # Recent payments
        context['recent_payments'] = user_payments.select_related(
            'invoice', 'invoice__child'
        ).order_by('-payment_date')[:5]
        
        return context


class InvoiceListView(LoginRequiredMixin, ListView):
    """List view for user's invoices (placeholder for Phase 2)"""
    model = Invoice
    template_name = 'invoices/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    
    def get_queryset(self):
        return Invoice.objects.filter(
            child__user=self.request.user
        ).select_related(
            'child', 'child__daycare_provider'
        ).order_by('-issue_date')


class PaymentListView(LoginRequiredMixin, ListView):
    """List view for user's payments (placeholder for Phase 2)"""
    model = Payment
    template_name = 'invoices/payment_list.html'
    context_object_name = 'payments'
    paginate_by = 20
    
    def get_queryset(self):
        return Payment.objects.filter(
            invoice__child__user=self.request.user
        ).select_related(
            'invoice', 'invoice__child'
        ).order_by('-payment_date')


class ChildListView(LoginRequiredMixin, ListView):
    """List view for user's children (placeholder for Phase 2)"""
    model = Child
    template_name = 'invoices/child_list.html'
    context_object_name = 'children'
    
    def get_queryset(self):
        return Child.objects.filter(
            user=self.request.user
        ).select_related('daycare_provider').order_by('name')
