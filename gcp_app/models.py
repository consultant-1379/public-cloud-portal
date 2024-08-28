from django.db import models
from django.conf import settings

# Create your models here.
from django.db import models
from django.utils import timezone
from billow.models import *

# Create your models here.
class Zone(models.Model):
    zone = models.CharField(max_length=64)

    def __str__(self):
        return self.zone

class Cpu_series(models.Model):
    cpu = models.IntegerField()
    ram = models.IntegerField()
    series = models.CharField(max_length=64)

    def __str__(self):
        return self.series


class Gcp_instance(models.Model):
    project = models.CharField(max_length=64, default=False)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    instance_name = models.CharField(max_length=64, default=False)
    machine_type = models.ForeignKey(Cpu_series, on_delete=models.CASCADE)
    status = models.CharField(max_length=64, default="Running")
    date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.instance_name

class snap_gcp_instance(models.Model):
    project = models.CharField(max_length=64, default=False)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    instance_name = models.CharField(max_length=64, default=False)
    machine_type = models.ForeignKey(Cpu_series, on_delete=models.CASCADE)
    status = models.CharField(max_length=64, default="Running")
    date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True)
    gcp_snap_index_obj = models.ForeignKey(Instance_Snap_Index, on_delete=models.CASCADE)


    def __str__(self):
        return self.instance_name
