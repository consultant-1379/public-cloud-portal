# Generated by Django 4.2.1 on 2023-08-04 10:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='hardware_profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hardware_name', models.CharField(max_length=64)),
                ('cpu', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('ram', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer', models.CharField(max_length=64)),
                ('publsiher', models.CharField(max_length=64)),
                ('sku', models.CharField(max_length=64)),
                ('version', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='os_disk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disk_size', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('storage_account_type', models.CharField(max_length=64)),
                ('disk_name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Azure_instance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('instance_name', models.CharField(max_length=64)),
                ('network_interface_name', models.CharField(max_length=64)),
                ('location', models.CharField(max_length=64)),
                ('status', models.CharField(max_length=64)),
                ('resource_group_name', models.CharField(max_length=64)),
                ('os_disk_name', models.CharField(max_length=64)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('created_by', models.CharField(max_length=64)),
                ('disk_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='azure_app.os_disk')),
                ('harware_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='azure_app.hardware_profile')),
                ('image_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='azure_app.image')),
            ],
        ),
    ]
