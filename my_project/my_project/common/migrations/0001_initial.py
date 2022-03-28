# Generated by Django 4.0.3 on 2022-03-28 09:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('library', '0005_delete_notification'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Change owner', 'Change Owner'), ('Liked', 'Liked'), ('Reviewed', 'Reviewed'), ('Wanted', 'Wanted'), ('Offered', 'Offered'), ('Deal', 'Deal')], max_length=12)),
                ('is_read', models.BooleanField(default=False)),
                ('received_date', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='library.book')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='receiver_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sender_messages', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['received_date'],
            },
        ),
    ]
