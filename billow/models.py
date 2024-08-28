from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils.timezone import localdate
import django
import logging

# Create your models here.
class Program(models.Model):
    program_name = models.CharField(max_length=64, unique=True)
    program_poc_obj = models.ForeignKey(User, blank=True, null=True, default=None, on_delete=models.PROTECT,
                                verbose_name="Program Point Of Contact")
    active = models.BooleanField(default=True)
    created = models.DateTimeField(editable=False, default=django.utils.timezone.now)
    modified = models.DateTimeField(default=django.utils.timezone.now)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = django.utils.timezone.now()
        self.modified = django.utils.timezone.now()
        return super(Program, self).save(*args, **kwargs)

    def __str__(self):
        return self.program_name


class Team(models.Model):
    team_name = models.CharField(max_length=64, unique=True)
    program_obj = models.ForeignKey(Program, on_delete=models.PROTECT, blank=True, null=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(editable=False, default=django.utils.timezone.now)
    modified = models.DateTimeField(default=django.utils.timezone.now)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = django.utils.timezone.now()
        self.modified = django.utils.timezone.now()
        return super(Team, self).save(*args, **kwargs)

    def __str__(self):
        return self.team_name


class Cloud_Provider(models.Model):
    cloud_name = models.CharField(max_length=64, unique=True)
    auth_url = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = django.utils.timezone.now()
        self.modified = django.utils.timezone.now()
        return super(Cloud_Provider, self).save(*args, **kwargs)

    def __str__(self):
        return self.cloud_name

class Cloud_Account(models.Model):
    # user added should have root permissions
    cloud_name = models.CharField(max_length=64, blank=True, null=True) ## maybe this needs to change to account name
    cloud_details = models.ForeignKey(Cloud_Provider, on_delete=models.PROTECT, blank=True, null=True) ## needs to change to cloud provider
    user_email = models.CharField(max_length=128, unique=True)
    username = models.CharField(max_length=64, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    token = models.CharField(max_length=128, blank=True, null=True)
    secret_token = models.CharField(max_length=1920, blank=True, null=True) #secret_token / client_token
    client_id = models.CharField(max_length=128, blank=True, null=True)
    subscription_id = models.CharField(max_length=256, blank=True, null=True)
    project_id = models.CharField(max_length=128, blank=True, null=True) #project/tenant id
    active = models.BooleanField(default=True, blank=True, null=True)
    created = models.DateTimeField(editable=False, default=django.utils.timezone.now)
    modified = models.DateTimeField(default=django.utils.timezone.now)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = django.utils.timezone.now()
        self.modified = django.utils.timezone.now()
        return super(Cloud_Account, self).save(*args, **kwargs)

    def __str__(self):
        return self.cloud_name

class Cloud_Account_Team_Name(models.Model):
    cloud_account = models.ForeignKey(Cloud_Account, on_delete=models.CASCADE)
    team_name = models.ForeignKey(Team, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(editable=False, default=django.utils.timezone.now)
    modified = models.DateTimeField(default=django.utils.timezone.now)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = django.utils.timezone.now()
        self.modified = django.utils.timezone.now()
        return super(Cloud_Account_Team_Name, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.cloud_account)

class Billing_Snap_Index(models.Model):
    timestamp = models.DateTimeField()
    hash_key = models.CharField(max_length=64, default=None)
    created = models.DateTimeField(editable=True, default=django.utils.timezone.now)
    modified = models.DateTimeField(default=django.utils.timezone.now)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = django.utils.timezone.now()
        self.modified = django.utils.timezone.now()
        return super(Billing_Snap_Index, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.timestamp)

class Instance_Snap_Index(models.Model):
    timestamp = models.DateTimeField()
    hash_key = models.CharField(max_length=64, default=None)
    created = models.DateTimeField(editable=True, default=django.utils.timezone.now)
    modified = models.DateTimeField(default=django.utils.timezone.now)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created = django.utils.timezone.now()
        self.modified = django.utils.timezone.now()
        return super(Instance_Snap_Index, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.timestamp)


class Billing(models.Model):
    cloud_account= models.ForeignKey(Cloud_Account, on_delete=models.CASCADE)
    daily_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    billing_snap_index_obj = models.ForeignKey(Billing_Snap_Index, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.cloud_account)
