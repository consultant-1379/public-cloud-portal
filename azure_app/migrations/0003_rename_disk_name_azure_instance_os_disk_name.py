# Generated by Django 4.2.1 on 2023-08-09 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure_app', '0002_remove_azure_instance_os_disk_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='azure_instance',
            old_name='disk_name',
            new_name='os_disk_name',
        ),
    ]
