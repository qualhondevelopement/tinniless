# Generated by Django 5.0.6 on 2024-08-02 04:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0023_alter_useraccount_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='prefix',
            field=models.CharField(blank=True, default='Mr.', max_length=5, null=True),
        ),
    ]