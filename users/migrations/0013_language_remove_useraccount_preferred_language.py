# Generated by Django 5.0.6 on 2024-07-24 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_alter_address_postal_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(max_length=5)),
                ('language_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='preferred_language',
        ),
    ]