# Generated by Django 4.2.1 on 2023-08-21 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billow', '0012_instance_snap_index'),
        ('aws_app', '0010_alter_snap_aws_instance_instance_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snap_aws_instance',
            name='aws_snap_index_obj',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billow.instance_snap_index'),
        ),
    ]
