# Generated for performance optimizations

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0002_alter_daycareprovider_email_addresses_and_more'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_invoice_user_status ON invoices_invoice (child_id, payment_status);",
            "DROP INDEX IF EXISTS idx_invoice_user_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_invoice_issue_date ON invoices_invoice (issue_date DESC);",
            "DROP INDEX IF EXISTS idx_invoice_issue_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_payment_date ON invoices_payment (payment_date DESC);",
            "DROP INDEX IF EXISTS idx_payment_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_child_user ON invoices_child (user_id, name);",
            "DROP INDEX IF EXISTS idx_child_user;"
        ),
    ]
