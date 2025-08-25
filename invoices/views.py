from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DetailView
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from decimal import Decimal
from .models import Invoice, Payment, Child, DaycareProvider
from .forms import InvoiceForm, PaymentForm, ChildForm
from .utils import process_uploaded_invoice


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
        queryset = Invoice.objects.filter(
            child__user=self.request.user
        ).select_related(
            'child', 'child__daycare_provider'
        ).order_by('-issue_date')
        
        # Filter by child if specified
        child_id = self.request.GET.get('child')
        if child_id:
            try:
                child_id = int(child_id)
                queryset = queryset.filter(child_id=child_id)
            except (ValueError, TypeError):
                pass
        
        # Filter by status if specified
        status = self.request.GET.get('status')
        if status and status in ['paid', 'partial', 'unpaid', 'overdue']:
            queryset = queryset.filter(payment_status=status)
            
        return queryset


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


# Phase 2 Implementation: CRUD Views

class InvoiceCreateView(LoginRequiredMixin, CreateView):
    """Create new invoice with PDF upload and parsing"""
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    success_url = reverse_lazy('invoices:invoice_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        invoice = form.save(commit=False)
        
        # Process PDF if uploaded
        if form.cleaned_data.get('pdf_file'):
            result = process_uploaded_invoice(form.cleaned_data['pdf_file'], self.request.user)
            
            if result['warnings']:
                for warning in result['warnings']:
                    messages.warning(self.request, warning)
            
            if result['errors']:
                for error in result['errors'].values():
                    messages.error(self.request, error)
                return self.form_invalid(form)
        
        messages.success(self.request, f'Invoice {invoice.invoice_reference} created successfully!')
        return super().form_valid(form)


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of an invoice with payments"""
    model = Invoice
    template_name = 'invoices/invoice_detail.html'
    context_object_name = 'invoice'
    
    def get_queryset(self):
        return Invoice.objects.filter(
            child__user=self.request.user
        ).select_related('child', 'child__daycare_provider').prefetch_related('payments')


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing invoice"""
    model = Invoice
    form_class = InvoiceForm
    template_name = 'invoices/invoice_form.html'
    
    def get_queryset(self):
        return Invoice.objects.filter(child__user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        messages.success(self.request, 'Invoice updated successfully!')
        return reverse('invoices:invoice_detail', kwargs={'pk': self.get_object().pk})


class PaymentCreateView(LoginRequiredMixin, CreateView):
    """Create payment for an invoice"""
    model = Payment
    form_class = PaymentForm
    template_name = 'invoices/payment_form.html'
    success_url = reverse_lazy('invoices:payment_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        
        # Pre-select invoice if provided in URL
        invoice_id = self.request.GET.get('invoice')
        if invoice_id:
            try:
                invoice = Invoice.objects.get(
                    pk=invoice_id, 
                    child__user=self.request.user
                )
                initial['invoice'] = invoice
                # Suggest remaining balance as payment amount
                if invoice.outstanding_balance > 0:
                    initial['amount_paid'] = invoice.outstanding_balance
            except Invoice.DoesNotExist:
                pass
        
        return initial
    
    def form_valid(self, form):
        messages.success(self.request, 'Payment recorded successfully!')
        return super().form_valid(form)


class PaymentDetailView(LoginRequiredMixin, DetailView):
    """View payment details"""
    model = Payment
    template_name = 'invoices/payment_detail.html'
    context_object_name = 'payment'

    def get_queryset(self):
        return Payment.objects.filter(
            invoice__child__user=self.request.user
        ).select_related('invoice', 'invoice__child', 'invoice__child__daycare_provider')


class PaymentUpdateView(LoginRequiredMixin, UpdateView):
    """Edit payment"""
    model = Payment
    form_class = PaymentForm
    template_name = 'invoices/payment_form.html'
    success_url = reverse_lazy('invoices:payment_list')

    def get_queryset(self):
        return Payment.objects.filter(
            invoice__child__user=self.request.user
        )

    def form_valid(self, form):
        messages.success(self.request, 'Payment updated successfully!')
        return super().form_valid(form)


class ChildCreateView(LoginRequiredMixin, CreateView):
    """Create new child"""
    model = Child
    form_class = ChildForm
    template_name = 'invoices/child_form.html'
    success_url = reverse_lazy('invoices:child_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Child {form.instance.name} added successfully!')
        return super().form_valid(form)


class ChildUpdateView(LoginRequiredMixin, UpdateView):
    """Edit existing child"""
    model = Child
    form_class = ChildForm
    template_name = 'invoices/child_form.html'
    
    def get_queryset(self):
        return Child.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Child information updated successfully!')
        return reverse('invoices:child_list')


# AJAX Views for Enhanced UX

@login_required
def invoice_upload_ajax(request):
    """AJAX endpoint for PDF upload and parsing"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    if 'pdf_file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    pdf_file = request.FILES['pdf_file']
    result = process_uploaded_invoice(pdf_file, request.user)
    
    return JsonResponse(result)


@login_required
def invoice_quick_stats(request):
    """AJAX endpoint for quick invoice statistics"""
    user_invoices = Invoice.objects.filter(child__user=request.user)
    
    stats = {
        'total_invoices': user_invoices.count(),
        'unpaid_count': user_invoices.filter(payment_status='unpaid').count(),
        'partial_count': user_invoices.filter(payment_status='partial').count(),
        'total_outstanding': str(sum(inv.outstanding_balance for inv in user_invoices)),
    }
    
    return JsonResponse(stats)


# Daycare Provider Management Views

class ProviderListView(LoginRequiredMixin, ListView):
    """List view for daycare providers"""
    model = DaycareProvider
    template_name = 'invoices/provider_list.html'
    context_object_name = 'providers'
    
    def get_queryset(self):
        # Show providers that have children associated with this user
        return DaycareProvider.objects.filter(
            children__user=self.request.user
        ).distinct().order_by('name')


class ProviderDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a daycare provider"""
    model = DaycareProvider
    template_name = 'invoices/provider_detail.html'
    context_object_name = 'provider'
    
    def get_queryset(self):
        # Only show providers that have children associated with this user
        return DaycareProvider.objects.filter(
            children__user=self.request.user
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provider = self.get_object()
        
        # Get user's children at this provider
        context['user_children'] = Child.objects.filter(
            user=self.request.user,
            daycare_provider=provider
        )
        
        # Get invoices for this provider
        context['invoices'] = Invoice.objects.filter(
            child__user=self.request.user,
            child__daycare_provider=provider
        ).select_related('child').order_by('-issue_date')[:10]
        
        return context
