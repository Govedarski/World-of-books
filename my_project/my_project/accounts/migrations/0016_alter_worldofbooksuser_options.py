# Generated by Django 4.0.3 on 2022-04-09 13:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_alter_worldofbooksuser_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='worldofbooksuser',
            options={'ordering': ('username',)},
        ),
    ]
