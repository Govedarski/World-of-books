# Generated by Django 4.0.3 on 2022-04-05 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_worldofbooksuser_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='worldofbooksuser',
            options={'ordering': ['username']},
        ),
    ]
