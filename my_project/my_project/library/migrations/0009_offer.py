# Generated by Django 4.0.3 on 2022-03-30 11:41

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library', '0008_alter_book_options_alter_book_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True)),
                ('books_given', models.ManyToManyField(related_name='offered_to', to='library.book')),
                ('books_wanted', models.ManyToManyField(related_name='wanted_by', to='library.book')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='receiver_offer', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sender_offer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
