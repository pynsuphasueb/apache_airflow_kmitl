# Generated by Django 3.0.3 on 2020-05-07 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0007_patient_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient_info',
            name='CAG',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='patient_info',
            name='CAG_confirm',
            field=models.IntegerField(default=0),
        ),
    ]
