# Generated by Django 4.2.1 on 2023-07-06 10:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('billow', '0010_remove_billing_total_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing_snap_index',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
