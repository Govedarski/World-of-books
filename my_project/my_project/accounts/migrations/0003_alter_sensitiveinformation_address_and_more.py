# Generated by Django 4.0.3 on 2022-03-25 10:20

import django.core.validators
from django.db import migrations, models
import my_project.common.helpers.custom_validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_remove_profile_city_sensitiveinformation_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensitiveinformation',
            name='address',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='sensitiveinformation',
            name='phone_number',
            field=models.CharField(blank=True, max_length=9, null=True, validators=[django.core.validators.MinLengthValidator(9), my_project.common.helpers.custom_validators.OnlyNumberValidator]),
        ),
    ]
