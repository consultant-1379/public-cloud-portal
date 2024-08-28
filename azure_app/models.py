from django.db import models
from django.utils import timezone
from billow.models import *
from django.conf import settings

class image(models.Model):
    offer = models.CharField(max_length=64)
    publsiher = models.CharField(max_length=64)
    sku = models.CharField(max_length=64)
    version = models.CharField(max_length=64)

    def __str__(self):
        return self.offer

class os_disk(models.Model):
    disk_size =  models.DecimalField(max_digits=10, decimal_places=2, null=True)
    storage_account_type = models.CharField(max_length=64)
    disk_name =  models.CharField(max_length=64)

    def __str__(self):
        return self.disk_name

class hardware_profile(models.Model):
    hardware_name = models.CharField(max_length=64)
    cpu = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    ram = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return self.hardware_name

class Azure_instance(models.Model):
    instance_name = models.CharField(max_length=64)
    network_interface_name = models.CharField(max_length=64)
    location = models.CharField(max_length=64)
    status = models.CharField(max_length=64) ## manage_instance
    resource_group_name = models.CharField(max_length=64)
    date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True)
    os_disk_name = models.ForeignKey(os_disk, on_delete=models.CASCADE)
    image_name = models.ForeignKey(image, on_delete=models.CASCADE)
    harware_name = models.ForeignKey(hardware_profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.instance_name


class snap_azure_instance(models.Model):
    instance_name = models.CharField(max_length=64)
    network_interface_name = models.CharField(max_length=64)
    location = models.CharField(max_length=64)
    status = models.CharField(max_length=64) ## manage_instance
    resource_group_name = models.CharField(max_length=64)
    date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True)
    os_disk_name = models.ForeignKey(os_disk, on_delete=models.CASCADE)
    image_name = models.ForeignKey(image, on_delete=models.CASCADE)
    harware_name = models.ForeignKey(hardware_profile, on_delete=models.CASCADE)
    azure_snap_index_obj = models.ForeignKey(Instance_Snap_Index, on_delete=models.CASCADE)

    def __str__(self):
        return self.instance_name

