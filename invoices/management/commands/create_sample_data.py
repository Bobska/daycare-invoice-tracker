from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta
from invoices.models import DaycareProvider, Child, Invoice, Payment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing Phase 2 functionality'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Get or create a superuser (should exist from Phase 1)
        try:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(self.style.ERROR('No superuser found. Please create one first.'))
                return
        except Exception:
            self.stdout.write(self.style.ERROR('Error finding user. Please create a superuser first.'))
            return

        # Create daycare provider
        provider, created = DaycareProvider.objects.get_or_create(
            name="Sunshine Daycare Centre",
            defaults={
                'address': '123 Main Street, Cityville, ST 12345',
                'phone': '(555) 123-4567',
                'email': 'admin@sunshinedaycare.com',
                'license_number': 'DC-2024-001',
                'gst_number': '123456789',
                'bank_details': 'Account: 12345678, BSB: 123-456',
                'email_addresses': ['admin@sunshinedaycare.com', 'billing@sunshinedaycare.com'],
                'email_subject_patterns': ['Invoice', 'Statement', 'Bill'],
            }
        )
        if created:
            self.stdout.write(f'Created daycare provider: {provider.name}')
        else:
            self.stdout.write(f'Using existing daycare provider: {provider.name}')

        # Create children
        children_data = [
            {'name': 'Emma Johnson', 'reference_number': 'EMJ001', 'date_of_birth': date(2019, 3, 15)},
            {'name': 'Liam Smith', 'reference_number': 'LIS002', 'date_of_birth': date(2020, 7, 22)},
        ]

        children = []
        for child_data in children_data:
            child, created = Child.objects.get_or_create(
                user=user,
                reference_number=child_data['reference_number'],
                daycare_provider=provider,
                defaults={
                    'name': child_data['name'],
                    'date_of_birth': child_data['date_of_birth'],
                }
            )
            children.append(child)
            if created:
                self.stdout.write(f'Created child: {child.name}')
            else:
                self.stdout.write(f'Using existing child: {child.name}')

        # Create sample invoices
        today = date.today()
        invoices_data = [
            {
                'child': children[0],
                'invoice_reference': 'INV-2024-001',
                'period_start': date(2024, 8, 1),
                'period_end': date(2024, 8, 31),
                'issue_date': date(2024, 8, 1),
                'due_date': date(2024, 8, 15),
                'original_amount': Decimal('1200.00'),
                'discount_percentage': Decimal('10.00'),
                'discount_amount': Decimal('120.00'),
                'amount_due': Decimal('1080.00'),
                'fee_type': 'Monthly Daycare Fee',
            },
            {
                'child': children[1],
                'invoice_reference': 'INV-2024-002',
                'period_start': date(2024, 8, 1),
                'period_end': date(2024, 8, 31),
                'issue_date': date(2024, 8, 1),
                'due_date': date(2024, 8, 15),
                'original_amount': Decimal('950.00'),
                'discount_percentage': Decimal('0.00'),
                'discount_amount': Decimal('0.00'),
                'amount_due': Decimal('950.00'),
                'fee_type': 'Monthly Daycare Fee',
            },
            {
                'child': children[0],
                'invoice_reference': 'INV-2024-003',
                'period_start': date(2024, 7, 1),
                'period_end': date(2024, 7, 31),
                'issue_date': date(2024, 7, 1),
                'due_date': date(2024, 7, 15),
                'original_amount': Decimal('1200.00'),
                'discount_percentage': Decimal('5.00'),
                'discount_amount': Decimal('60.00'),
                'amount_due': Decimal('1140.00'),
                'fee_type': 'Monthly Daycare Fee',
            },
        ]

        invoices = []
        for invoice_data in invoices_data:
            invoice, created = Invoice.objects.get_or_create(
                child=invoice_data['child'],
                invoice_reference=invoice_data['invoice_reference'],
                defaults=invoice_data
            )
            invoices.append(invoice)
            if created:
                self.stdout.write(f'Created invoice: {invoice.invoice_reference} for {invoice.child.name}')
            else:
                self.stdout.write(f'Using existing invoice: {invoice.invoice_reference}')

        # Create sample payments
        payments_data = [
            {
                'invoice': invoices[0],  # Partial payment for INV-2024-001
                'payment_date': date(2024, 8, 10),
                'amount_paid': Decimal('500.00'),
                'payment_method': 'direct_credit',
                'reference_number': 'TXN-001-500',
                'notes': 'Partial payment - first installment',
            },
            {
                'invoice': invoices[1],  # Full payment for INV-2024-002
                'payment_date': date(2024, 8, 12),
                'amount_paid': Decimal('950.00'),
                'payment_method': 'credit_card',
                'reference_number': 'CC-2024-0812',
                'notes': 'Full payment via credit card',
            },
            {
                'invoice': invoices[2],  # Full payment for INV-2024-003 (older invoice)
                'payment_date': date(2024, 7, 14),
                'amount_paid': Decimal('1140.00'),
                'payment_method': 'direct_credit',
                'reference_number': 'TXN-003-1140',
                'notes': 'Full payment on time',
            },
        ]

        for payment_data in payments_data:
            payment, created = Payment.objects.get_or_create(
                invoice=payment_data['invoice'],
                payment_date=payment_data['payment_date'],
                amount_paid=payment_data['amount_paid'],
                defaults=payment_data
            )
            if created:
                self.stdout.write(f'Created payment: ${payment.amount_paid} for {payment.invoice.invoice_reference}')
            else:
                self.stdout.write(f'Using existing payment: ${payment.amount_paid} for {payment.invoice.invoice_reference}')

        self.stdout.write(self.style.SUCCESS('\nSample data creation complete!'))
        self.stdout.write('\nSummary:')
        self.stdout.write(f'- Daycare Providers: {DaycareProvider.objects.count()}')
        self.stdout.write(f'- Children: {Child.objects.filter(user=user).count()}')
        self.stdout.write(f'- Invoices: {Invoice.objects.filter(child__user=user).count()}')
        self.stdout.write(f'- Payments: {Payment.objects.filter(invoice__child__user=user).count()}')
        
        # Show invoice statuses
        self.stdout.write('\nInvoice Status Summary:')
        for invoice in Invoice.objects.filter(child__user=user):
            status = invoice.payment_status
            outstanding = invoice.outstanding_balance
            self.stdout.write(f'- {invoice.invoice_reference}: {status.title()} (Outstanding: ${outstanding})')
