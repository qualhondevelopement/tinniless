# Generated by Django 5.0.6 on 2024-07-17 07:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_remove_medicalrecord_treatment_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicalrecord',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='middle_name',
            field=models.CharField(default='', max_length=25),
        ),
        migrations.AddField(
            model_name='usertreatmentmapping',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='full_name',
            field=models.CharField(max_length=90),
        ),
    ]
