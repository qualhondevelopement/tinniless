# Generated by Django 5.0.6 on 2024-07-08 13:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_medicalrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='preferred_language',
            field=models.CharField(choices=[('EN', 'English'), ('ES', 'Spanish')], default='EN', max_length=10),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='business',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='business_user', to='users.business'),
        ),
    ]