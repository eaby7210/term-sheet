# Generated by Django 4.2.20 on 2025-05-05 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('term_sheet', '0004_alter_termdata_interest_rate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='termdata',
            name='after_repaired_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='annual_flood_insurance',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='annual_hoa_dues',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='annual_insurance',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='annual_taxes',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='as_is_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='cash_to_from_borrower',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='current_dscr',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='fair_market_rent',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='fico_score',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='interest_rate',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='lender_fee',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='loan_amount',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='loan_to_value',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='monthly_payment',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='origination_cost',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='prepayment_penalty',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='processing_fee',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='termdata',
            name='rehab_cost',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
