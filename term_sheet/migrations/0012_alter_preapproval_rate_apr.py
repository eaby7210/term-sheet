# Generated by Django 4.2.20 on 2025-05-07 22:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('term_sheet', '0011_alter_preapproval_loan_term_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preapproval',
            name='rate_apr',
            field=models.DecimalField(decimal_places=4, max_digits=12),
        ),
    ]
