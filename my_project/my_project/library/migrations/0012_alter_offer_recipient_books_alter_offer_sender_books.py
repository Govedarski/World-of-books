# Generated by Django 4.0.3 on 2022-03-30 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0011_rename_wanted_books_offer_recipient_books_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='recipient_books',
            field=models.ManyToManyField(related_name='wanted', to='library.book'),
        ),
        migrations.AlterField(
            model_name='offer',
            name='sender_books',
            field=models.ManyToManyField(related_name='offered', to='library.book'),
        ),
    ]