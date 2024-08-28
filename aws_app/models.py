from django.db import models
from django.utils import timezone
from billow.models import *
from django.conf import settings

class aws_image(models.Model):
    image_name = models.CharField(max_length=64)
    image_ID = models.CharField(max_length=64)

    def __str__(self):
        return self.image_name

class aws_instance_type(models.Model):
    instance_type = models.CharField(max_length=64)
    ram = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    cpu = models.IntegerField()

    def __str__(self):
        return self.instance_type

class aws_keyname(models.Model):
    keyname = models.CharField(max_length=64)

    def __str__(self):
        return self.keyname

class aws_instance(models.Model):
    instance_name = models.CharField(max_length=64, unique=True)
    instance_id = models.CharField(max_length=64)
    instance_type = models.ForeignKey(aws_instance_type, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=64)
    date_created = models.DateField(default=timezone.now)
    region = models.CharField(max_length=64)
    status = models.CharField(max_length=64, default="Running")

    def __str__(self):
        return self.instance_name

class snap_aws_instance(models.Model):
    instance_name = models.CharField(max_length=64)
    instance_id = models.CharField(max_length=64)
    instance_type = models.ForeignKey(aws_instance_type, on_delete=models.CASCADE)
    created_by = models.CharField(max_length=64)
    date_created = models.DateField(default=timezone.now)
    region = models.CharField(max_length=64)
    status = models.CharField(max_length=64, default="Running")
    aws_snap_index_obj = models.ForeignKey(Instance_Snap_Index, on_delete=models.CASCADE)

    def __str__(self):
        return self.instance_name