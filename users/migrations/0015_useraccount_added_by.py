# Generated by Django 5.0.6 on 2024-07-24 07:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_useraccount_preferred_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='added_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='added_users', to=settings.AUTH_USER_MODEL),
        ),
    ]