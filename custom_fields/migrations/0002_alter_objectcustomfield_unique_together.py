# Generated by Django 5.1.7 on 2025-03-19 14:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_fields', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='objectcustomfield',
            unique_together={('field_id', 'object_id')},
        ),
    ]
