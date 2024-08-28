from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.consumption import ConsumptionManagementClient
from datetime import datetime, timedelta
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.network.models import NetworkInterface, NetworkInterfaceIPConfiguration, Subnet
from billow.models import *
from azure_app.models import *
import hashlib
from datetime import timedelta
from datetime import datetime as dt
from datetime import datetime
import time
from azure.core.exceptions import HttpResponseError




azure_obj = Cloud_Account.objects.get(cloud_name="Azure")

# Replace the values below with your own values
tenant_id = azure_obj.token
client_id = azure_obj.client_id
client_secret = azure_obj.secret_token
subscription_id = azure_obj.subscription_id

# Create a ClientSecretCredential object using the values above
credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

compute_client = ComputeManagementClient(
credential = credential,
subscription_id = subscription_id
)

cost_client = CostManagementClient(
    credential=credential
)


def get_cost(params):

    total_cost = 0
    date_format = '%Y-%m-%d'
    use_date = dt.strptime(params['start_date'][0:10], date_format)
    end_date = dt.strptime(params['end_date'][0:10], date_format)
    for items in Billing.objects.all() :
        get_date = use_date.strftime("%Y-%m-%d-%H-%M-%S")[0:10]
        use_date = use_date + timedelta(days=1)
        find_date = Billing_Snap_Index.objects.get(timestamp__startswith = get_date)
        account = Cloud_Account.objects.get(cloud_name = 'Azure')
        billing_date = Billing.objects.filter(billing_snap_index_obj = find_date)
        one_cost = billing_date.get(cloud_account = account).daily_cost

        total_cost += one_cost
        if use_date > end_date :
           break
    total_cost = (float(total_cost))
    return total_cost

def get_daily_cost():
    current_date = datetime.today()
    start_date = current_date - timedelta(hours=24)
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    current_date_str = current_date.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    max_retries = 10  # You can adjust the number of retries as needed
    retry_wait_time = 10  # Adjust the initial wait time as needed (in seconds)
    total_cost = None
    for attempt in range(max_retries):
        try:
            response = cost_client.query.usage(
            scope="/subscriptions/86b34741-53e3-49c5-928c-2c560c151aab/",
            parameters={
                "dataset": {
                    "aggregation": {"totalCost": {"function": "Sum", "name": "PreTaxCost"}},
                    "granularity": "None",
                    "grouping": [{"name": "SubscriptionId", "type": "Dimension"}],  # Modify grouping to SubscriptionId
                },
                "timeframe": "Custom",
                "timePeriod": {
                    "from": start_date_str,
                    "to": current_date_str,
                },
                "type": "Usage"
            },
        )
            total_cost = response.rows
            total_cost = total_cost[0][0]
            time.sleep(30)
            print(total_cost)
        except HttpResponseError as ex:
            total_cost = None
            print('got an exception, attempt {}'.format(attempt))
            if ex.status_code == 429:
                retry_after = int(ex.response.headers.get("retry-after", retry_wait_time))
                print(f"Received 429 error. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                retry_wait_time *= 2  # Exponential backoff
            else:
                raise  # If it's not a rate-limiting error, raise the exception
        finally:
            if total_cost:
                break

    return total_cost

def get_index():
    timestamp = django.utils.timezone.now()
    hash = hashlib.sha1()
    timestamp = (str(timestamp))
    encode_timestamp = timestamp.encode(encoding='UTF-8', errors ='strict')
    hash.update((encode_timestamp))
    New_Billing_Snap_Index = Billing_Snap_Index(
        timestamp=timestamp,
        hash_key=hash.hexdigest()
        )

    New_Billing_Snap_Index.save()
    print("hashing index created")
    return New_Billing_Snap_Index

def azure_daily_snapshot(params):
    total_cost = get_daily_cost()
    new_bill_save = Billing(
        cloud_account = Cloud_Account.objects.get(cloud_name = 'Azure'),
        daily_cost = total_cost,
        billing_snap_index_obj = params
    )
    new_bill_save.save()
    print("Azure daily cost saved to db")


def start_vm(resource_group_name, vm_name):
    compute_client.virtual_machines.begin_start(resource_group_name, vm_name)

def stop_vm(resource_group_name, vm_name):
    compute_client.virtual_machines.begin_deallocate(resource_group_name, vm_name)

def delete_vm(resource_group_name, vm_name):
    compute_client.virtual_machines.begin_delete(resource_group_name, vm_name)

def list_all_vms():
    vms = compute_client.virtual_machines.list_all()
    vm_details = []

    for vm in vms:
        vm_name = vm.name
        resource_group = vm.id.split('/')[4]
        instance_view = compute_client.virtual_machines.instance_view(resource_group, vm_name)
        if instance_view.statuses:
            for status in instance_view.statuses:
                if 'powerstate' in status.code.lower():
                    power_state = status.display_status
                    break
            else:
                power_state = "Unknown"
        else:
            power_state = "Unknown"

        vm_details.append({
            'name': vm_name,
            'id': resource_group,
            'status': power_state
        })

    return vm_details

def create_nic(nic_name, location, resource_group_name, virtual_network):

    network_client = NetworkManagementClient(credential, subscription_id)
    # Create a subnet object
    subnet = Subnet(id=f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/virtualNetworks/{virtual_network}/subnets/default")
    # Create an IP configuration object
    ip_config = NetworkInterfaceIPConfiguration(name=nic_name, subnet=subnet)
    # Create a network interface object
    network_interface = NetworkInterface(location = location, ip_configurations=[ip_config])
    # Create the network interface
    network_client.network_interfaces.begin_create_or_update(resource_group_name, nic_name, network_interface).result()


def create_instance_azure(params, request):
    create_nic(params["nic_name"], params["region"], params["resource_group"], params["virtual_network"])
    client = ComputeManagementClient(
        credential=credential,
        subscription_id = subscription_id
    )

    resource_group_name=params["resource_group"]
    nic_name=params["nic_name"]
    location=params["region"]
    vm_name=params["vm_name"]

    response = client.virtual_machines.begin_create_or_update(
        resource_group_name=resource_group_name,
        vm_name= vm_name,
        parameters={
            "location": location,
            "properties": {
                "hardwareProfile": {"vmSize": "Standard_B1ls"},
                "networkProfile": {
                    "networkInterfaces": [
                            {
                                "id": f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.Network/networkInterfaces/{nic_name}',
                                "properties": {"primary": True},
                            }
                        ]
                    },
                "osProfile": {
                        "adminPassword": "N3wP@55w0rd",
                        "adminUsername": 'emma',
                        "computerName": vm_name,
                    },
                "storageProfile": {
                    "imageReference": {
                        "offer": "UbuntuServer",
                        "publisher": "Canonical",
                        "sku": "18_04-lts-gen2",
                        "version": "latest",
                    },
                    "osDisk": {
                        "caching": "ReadWrite",
                        "createOption": "FromImage",
                        "managedDisk": {"storageAccountType": "StandardSSD_LRS"},
                        "diskSizeGB": 30,
                        "name": params["os_disk_name"],
                    },
                },
            },
        },
    ).result()

    os_disk_object = os_disk(
        disk_size = '30',
        storage_account_type = 'StandardSSD_LRS',
        disk_name = params["os_disk_name"],
    )

    os_disk_object.save()

    current_date_time = datetime.now()

    Instance_object = Azure_instance(
        instance_name = vm_name,
        network_interface_name = nic_name,
        location = location,
        status = 'running',
        resource_group_name = resource_group_name,
        date = current_date_time.strftime("%Y-%m-%d"),
        created_by = request.user,
        image_name = image.objects.get(offer="UbuntuServer"),
        os_disk_name = os_disk.objects.get(disk_name=params["os_disk_name"]),
        harware_name = hardware_profile.objects.get(hardware_name="Standard_B1ls"),

    )
    Instance_object.save()