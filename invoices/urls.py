from django.urls import path
from . import views

app_name = 'invoices'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Placeholder URLs for future development
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('children/', views.ChildListView.as_view(), name='child_list'),
]
