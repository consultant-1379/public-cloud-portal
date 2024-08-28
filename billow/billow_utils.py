from azure_app.models import *
from gcp_app.models import *
from aws_app.models import *
import hashlib



def get_index_snapshot():
    timestamp = django.utils.timezone.now()
    hash = hashlib.sha1()
    timestamp = (str(timestamp))
    encode_timestamp = timestamp.encode(encoding='UTF-8', errors ='strict')
    hash.update((encode_timestamp))
    New_sanpshot_Snap_Index = Instance_Snap_Index(
        timestamp=timestamp,
        hash_key=hash.hexdigest()
        )

    New_sanpshot_Snap_Index.save()
    print("hashing index created for snapshots")
    return New_sanpshot_Snap_Index


def azure_instance_snapshot(params):
    azure_instances = Azure_instance.objects.filter()
    for azure_instances in azure_instances:
        new_instance_snap = snap_azure_instance(
        instance_name = azure_instances.instance_name,
        network_interface_name = azure_instances.network_interface_name,
        location = azure_instances.location,
        status = azure_instances.status,
        resource_group_name = azure_instances.resource_group_name,
        date = azure_instances.date,
        created_by = azure_instances.created_by,
        os_disk_name = azure_instances.os_disk_name,
        image_name = azure_instances.image_name,
        harware_name = azure_instances.harware_name,
        azure_snap_index_obj = params

        )
    
        new_instance_snap.save() ## need to do gcp
        print("Azure instance snapshot saved")

    
def gcp_instance_snapshot(params):
    gcp_instances = Gcp_instance.objects.filter()
    for gcp_instance in gcp_instances:
        new_gcp_instance_snap = snap_gcp_instance(
        project = gcp_instance.project,
        zone = gcp_instance.zone,
        instance_name = gcp_instance.instance_name,
        machine_type = gcp_instance.machine_type,
        status = gcp_instance.status,
        date = gcp_instance.date,
        created_by = gcp_instance.created_by,
        gcp_snap_index_obj = params
        )
        new_gcp_instance_snap.save()
    print("Gcp instance snapshot saved")

    
    

def aws_instance_snapshot(params):
    aws_instances = aws_instance.objects.filter()
    for aws_instance_snap in aws_instances:
        new_aws_instance_snap = snap_aws_instance(
        instance_name = aws_instance_snap.instance_name,
        instance_id = aws_instance_snap.instance_id,
        instance_type = aws_instance_snap.instance_type,
        created_by = aws_instance_snap.created_by,
        date_created = aws_instance_snap.date_created,
        region = aws_instance_snap.region,
        status = aws_instance_snap.status,
        aws_snap_index_obj = params
        )
        new_aws_instance_snap.save()
    print("AWS instance snapshot saved")
    
