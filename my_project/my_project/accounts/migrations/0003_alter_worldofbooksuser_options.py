# Generated by Django 4.0.3 on 2022-03-30 11:21

from django.db import migrations
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_profile_first_name_alter_profile_last_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='worldofbooksuser',
            options={'ordering': [django.db.models.functions.text.Lower('username')]},
        ),
    ]