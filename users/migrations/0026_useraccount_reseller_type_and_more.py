# Generated by Django 5.0.6 on 2024-08-04 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0025_remove_useraccount_preferred_language_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='reseller_type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='user_type',
            field=models.CharField(choices=[('ADMIN', 'ADMIN'), ('PATIENT', 'PATIENT'), ('OPERATOR', 'OPERATOR'), ('RESELLER', 'RESELLER'), ('RETAILER', 'RETAILER')], default='PATIENT', max_length=25),
        ),
    ]