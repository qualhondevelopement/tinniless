# Generated by Django 5.0.6 on 2024-07-17 08:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_useraccount_business_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactnumber',
            name='business',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.business'),
        ),
        migrations.AlterField(
            model_name='contactnumber',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
