# Generated by Django 5.0.6 on 2024-08-02 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_alter_useraccount_preferred_time_zone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='gender',
            field=models.CharField(blank=True, choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHER', 'OTHER')], default='MALE', max_length=25, null=True),
        ),
    ]
