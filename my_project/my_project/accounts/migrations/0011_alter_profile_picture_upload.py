# Generated by Django 4.0.3 on 2022-04-05 10:34

import cloudinary.models
from django.db import migrations

import my_project.common.helpers.custom_validators


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_profile_picture_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture_upload',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, validators=[my_project.common.helpers.custom_validators.MaxSizeInMBValidator(2)], verbose_name='Image'),
        ),
    ]