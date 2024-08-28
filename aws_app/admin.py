from django.contrib import admin
from aws_app.models import *

# Register your models here.
admin.site.register(aws_image)
admin.site.register(aws_instance_type)
admin.site.register(aws_keyname)
admin.site.register(aws_instance)