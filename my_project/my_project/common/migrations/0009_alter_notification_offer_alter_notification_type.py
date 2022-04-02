# Generated by Django 4.0.3 on 2022-03-31 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('offer', '0001_initial'),
        ('common', '0008_notification_offer_alter_notification_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='offer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='offer.offer'),
        ),
        migrations.AlterField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('Change owner', 'Change Owner'), ('Liked', 'Liked'), ('Disliked', 'Disliked'), ('Reviewed', 'Reviewed'), ('Offered', 'Offered'), ('Counter offered', 'C Offered'), ('Shared contacts', 'Contacts Shared')], max_length=15),
        ),
    ]
