# Generated by Django 4.2.20 on 2025-05-14 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('term_sheet', '0014_alter_preapproval_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opportunity',
            name='updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
