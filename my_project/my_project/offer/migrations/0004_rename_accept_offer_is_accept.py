# Generated by Django 4.0.3 on 2022-04-01 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0003_rename_sender_accept_offer_accept_remove_offer_deal_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='offer',
            old_name='accept',
            new_name='is_accept',
        ),
    ]
