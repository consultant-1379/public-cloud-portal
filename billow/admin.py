from django.contrib import admin
from .models import *
from azure_app.models import *
from gcp_app.models import *
from aws_app.models import *

# Register your models here.
admin.site.register(Team)
admin.site.register(Cloud_Provider)
admin.site.register(Program)
admin.site.register(Cloud_Account)
admin.site.register(Cloud_Account_Team_Name)
admin.site.register(image)
admin.site.register(os_disk)
admin.site.register(hardware_profile)
admin.site.register(Azure_instance)

class Billing_Admin(admin.ModelAdmin):
    list_display = [ "billing_snap_index_obj", "cloud_account", "daily_cost"]
    ordering = ("-billing_snap_index_obj__timestamp",)

class Billing_Ind_Admin(admin.ModelAdmin):
    list_display = ["id", "timestamp", "hash_key", "created",]
    ordering = ("-timestamp",)

admin.site.register(Billing_Snap_Index, Billing_Ind_Admin)
admin.site.register(Billing, Billing_Admin)
admin.site.register(snap_azure_instance)
admin.site.register(snap_gcp_instance)
admin.site.register(snap_aws_instance)
admin.site.register(Instance_Snap_Index)



