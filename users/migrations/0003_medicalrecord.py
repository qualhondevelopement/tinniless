# Generated by Django 5.0.6 on 2024-07-08 13:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_business_business_type_alter_useraccount_user_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('treatment_type', models.CharField(choices=[('SOUND_TREATMENT', 'SOUND_TREATMENT'), ('RF_RIGHT', 'RF_RIGHT'), ('RF_LEFT', 'RF_LEFT')], default='SOUND_TREATMENT', max_length=25)),
                ('tinnitus_start_date', models.DateField(blank=True, null=True)),
                ('ears', models.CharField(choices=[('LEFT_EAR', 'LEFT_EAR'), ('RIGHT_EAR', 'RIGHT_EAR'), ('BOTH_EAR', 'BOTH_EAR')], default='BOTH_EAR', max_length=25)),
                ('tinnitus_type', models.CharField(choices=[('SUBJECTIVE_TINNITUS', 'SUBJECTIVE_TINNITUS'), ('OBJECTIVE_TINNITUS', 'OBJECTIVE_TINNITUS'), ('TONAL_TINNITUS', 'TONAL_TINNITUS'), ('PULSATILE_TINNITUS', 'PULSATILE_TINNITUS'), ('MUSCULAR_TINNITUS', 'MUSCULAR_TINNITUS'), ('NEUROLOGICAL_TINNITUS', 'NEUROLOGICAL_TINNITUS'), ('SOMATIC_TINNITUS', 'SOMATIC_TINNITUS'), ('SENSORINEURAL_TINNITUS', 'SENSORINEURAL_TINNITUS')], default='SUBJECTIVE_TINNITUS', max_length=50)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_record', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]