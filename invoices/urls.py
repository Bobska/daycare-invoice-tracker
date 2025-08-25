from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Quick action shortcuts (for buttons)
    path('invoice/add/', views.InvoiceCreateView.as_view(), name='invoice_add'),
    path('payment/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('child/add/', views.ChildCreateView.as_view(), name='child_add'),
    
    # Invoice management
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice_edit'),
    
    # Payment management
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment_create'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('payments/<int:pk>/edit/', views.PaymentUpdateView.as_view(), name='payment_edit'),
    
    # Child management
    path('children/', views.ChildListView.as_view(), name='child_list'),
    path('children/create/', views.ChildCreateView.as_view(), name='child_create'),
    path('children/<int:pk>/edit/', views.ChildUpdateView.as_view(), name='child_edit'),
    
    # Provider management
    path('providers/', views.ProviderListView.as_view(), name='provider_list'),
    path('providers/<int:pk>/', views.ProviderDetailView.as_view(), name='provider_detail'),
    
    # AJAX endpoints
    path('ajax/invoice-upload/', views.invoice_upload_ajax, name='invoice_upload_ajax'),
    path('ajax/quick-stats/', views.invoice_quick_stats, name='invoice_quick_stats'),
]
