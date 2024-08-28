from boto3 import client, resource
from forex_python.converter import CurrencyRates
from billow.models import *
import hashlib
from datetime import timedelta
from datetime import datetime as dt
from aws_app.models import *


def get_aws_total_cost(params):

    total_cost = 0
    date_format = '%Y-%m-%d'
    use_date = dt.strptime(params['start_date'][0:10], date_format)
    end_date = dt.strptime(params['end_date'][0:10], date_format)
    for items in Billing.objects.all() :
        get_date = use_date.strftime("%Y-%m-%d-%H-%M-%S")[0:10]
        use_date = use_date + timedelta(days=1)
        find_date = Billing_Snap_Index.objects.get(timestamp__startswith = get_date)
        account = Cloud_Account.objects.get(cloud_name = 'AWS')
        billing_date = Billing.objects.filter(billing_snap_index_obj = find_date)
        one_cost = billing_date.get(cloud_account = account).daily_cost

        total_cost += one_cost
        if use_date > end_date :
           break
    total_cost = (float(total_cost))
    return total_cost

def get_aws_daily_cost():

    end_date = dt.today()
    start_date = end_date - timedelta(hours=24)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    aws_obj = Cloud_Account.objects.get(cloud_name="AWS")
    c = client('ce', aws_access_key_id=aws_obj.token, aws_secret_access_key=aws_obj.secret_token, region_name=aws_obj.project_id)

    cost_response = c.get_cost_and_usage(TimePeriod={'Start':start_date_str, 'End':end_date_str},
                                     Granularity='DAILY',
                                     Metrics=['UnblendedCost'])['ResultsByTime']

    daily_cost = 0
    for total in cost_response:
        unblended_cost = list(total.values())[1]
        for amount in list(unblended_cost.values()):
            daily_cost += float(list(amount.values())[0])

    return daily_cost

def get_aws_instances():
    aws_obj = Cloud_Account.objects.get(cloud_name="AWS")
    ec2 = client('ec2', aws_access_key_id=aws_obj.token, aws_secret_access_key=aws_obj.secret_token, region_name=aws_obj.project_id)

    reservations = ec2.describe_instances()['Reservations']

    vm_details = []

    for reservation in reservations:
            for instance in reservation['Instances']:
                aws_instance_id = instance['InstanceId']
                instance_status = instance['State']['Name']
                instance_name = instance.get('Tags', [{'Key': 'Name', 'Value': 'N/A'}])[0]['Value']

                vm_details.append({
                    'name': instance_name,
                    'id': aws_instance_id,
                    'status': instance_status
                })

    return vm_details

def start_instance_aws(instance_id):
    aws_obj = Cloud_Account.objects.get(cloud_name="AWS")
    ec2 = client('ec2', aws_access_key_id=aws_obj.token, aws_secret_access_key=aws_obj.secret_token, region_name=aws_obj.project_id)

    response = ec2.start_instances(InstanceIds = [instance_id])

def stop_instance_aws(instance_id):
    aws_obj = Cloud_Account.objects.get(cloud_name="AWS")
    ec2 = client('ec2', aws_access_key_id=aws_obj.token, aws_secret_access_key=aws_obj.secret_token, region_name=aws_obj.project_id)

    response = ec2.stop_instances(InstanceIds =[instance_id])


def delete_instance_aws(params):
    aws_obj = Cloud_Account.objects.get(cloud_name="AWS")
    ec2 = client('ec2', aws_access_key_id=aws_obj.token, aws_secret_access_key=aws_obj.secret_token, region_name=aws_obj.project_id)

    # Specify the instance ID
    instance_id = params

    # Terminate the EC2 instance
    response = ec2.terminate_instances(InstanceIds=[instance_id])

def aws_daily_snapshot(params):

    total_cost = get_aws_daily_cost()

    new_bill_save = Billing(
        cloud_account = Cloud_Account.objects.get(cloud_name = 'AWS'),
        daily_cost = total_cost,
        billing_snap_index_obj = params
    )
    new_bill_save.save()
    print("AWS daily cost saved to db")

def create_instance_aws(params):
    aws_obj = Cloud_Account.objects.get(cloud_name="AWS")
    ec2 = resource('ec2', aws_access_key_id=aws_obj.token, aws_secret_access_key=aws_obj.secret_token, region_name=params['region'])

    instance = ec2.create_instances(
        ImageId = params['image_id'],
        InstanceType = params['instance_type'],
        # Can only create one instance at a time for now
        MinCount = 1,
        MaxCount = 1,
        KeyName = params['key_name'],

        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': params['instance_name']
                    },
                ]
            },
        ],
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': int(params['storage']),
                    'VolumeType': 'standard'
                }
            }
        ]
    )
    #instance id of new instance
    return instance[0].id

def get_aws_cpu_ram():
    ram = 0
    cpu = 0

    for instance in aws_instance.objects.all():
        if instance.status == 'Running':
            ram += aws_instance_type.objects.filter(aws_instance__instance_type=instance.instance_type).values()[0]['ram']
            cpu += aws_instance_type.objects.filter(aws_instance__instance_type=instance.instance_type).values()[0]['cpu']
    print({'vCPU': cpu, 'Ram': float(ram)})
    return {'vCPU': cpu, 'Ram': float(ram)}