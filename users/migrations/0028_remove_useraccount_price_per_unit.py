# Generated by Django 5.0.6 on 2024-08-07 12:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_useraccount_price_mapping_alter_contactnumber_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraccount',
            name='price_per_unit',
        ),
    ]
