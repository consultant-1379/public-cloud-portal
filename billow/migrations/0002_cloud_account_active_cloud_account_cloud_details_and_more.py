# Generated by Django 4.2.1 on 2023-06-01 13:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('billow', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloud_account',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cloud_account',
            name='cloud_details',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='billow.cloud_provider'),
        ),
        migrations.AddField(
            model_name='cloud_account',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='cloud_account',
            name='modified',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='cloud_account_team_name',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cloud_account_team_name',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='cloud_account_team_name',
            name='modified',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
