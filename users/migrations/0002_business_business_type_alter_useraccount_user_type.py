# Generated by Django 5.0.6 on 2024-07-08 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='business_type',
            field=models.CharField(choices=[('CLINIC', 'CLINIC'), ('RESELLER', 'RESELLER')], default='CLINIC', max_length=25),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='user_type',
            field=models.CharField(choices=[('ADMIN', 'ADMIN'), ('PATIENT', 'PATIENT'), ('OPERATOR', 'OPERATOR'), ('RESELLER', 'RESELLER')], default='PATIENT', max_length=25),
        ),
    ]