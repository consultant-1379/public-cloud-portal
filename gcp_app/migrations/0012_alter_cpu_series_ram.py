# Generated by Django 4.2.1 on 2023-08-03 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gcp_app', '0001_squashed_0011_alter_gcp_instance_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cpu_series',
            name='ram',
            field=models.IntegerField(),
        ),
    ]
