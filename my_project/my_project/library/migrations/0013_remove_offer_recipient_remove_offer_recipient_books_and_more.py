# Generated by Django 4.0.3 on 2022-03-31 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0012_alter_offer_recipient_books_alter_offer_sender_books'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offer',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='recipient_books',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='sender',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='sender_books',
        ),
    ]
