# Generated by Django 3.0.3 on 2020-04-21 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0005_auto_20200420_1625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patients',
            name='gender',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='patient_info',
        ),
    ]