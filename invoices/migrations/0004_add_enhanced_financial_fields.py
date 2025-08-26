# Migration to add enhanced financial tracking fields

from django.db import migrations, models
from decimal import Decimal

class Migration(migrations.Migration):
    
    dependencies = [
        ('invoices', '0003_add_performance_indexes'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='invoice',
            name='previous_balance',
            field=models.DecimalField(
                decimal_places=2, 
                default=Decimal('0.00'), 
                max_digits=10,
                help_text="Previous unpaid balance carried forward"
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='week_amount_due',
            field=models.DecimalField(
                decimal_places=2, 
                default=Decimal('0.00'), 
                max_digits=10,
                help_text="Amount due for this week only (excluding previous balance)"
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='total_amount_due',
            field=models.DecimalField(
                decimal_places=2, 
                default=Decimal('0.00'), 
                max_digits=10,
                help_text="Total amount due including previous balance"
            ),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='amount_due',
            field=models.DecimalField(
                decimal_places=2, 
                max_digits=10,
                help_text="Legacy field - use total_amount_due instead"
            ),
        ),
    ]
