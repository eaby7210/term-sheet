# Generated by Django 4.2.20 on 2025-05-05 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('model_name', models.CharField(max_length=50)),
                ('field_key', models.CharField(max_length=255)),
                ('placeholder', models.CharField(blank=True, max_length=255)),
                ('data_type', models.CharField(max_length=50)),
                ('parent_id', models.CharField(max_length=100)),
                ('location_id', models.CharField(max_length=100)),
                ('date_added', models.DateTimeField()),
            ],
        ),
    ]
