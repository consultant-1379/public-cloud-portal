from __future__ import annotations
from billow.models import *
from gcp_app.models import *
from google.api_core.extended_operation import ExtendedOperation
from google.cloud import bigquery
from google.cloud import compute_v1
from google.oauth2 import service_account
from pathlib import Path
from collections import defaultdict
from collections.abc import Iterable
import datetime
import subprocess
from datetime import datetime, timedelta
import hashlib
from datetime import datetime as dt
from django.core.exceptions import PermissionDenied



gcp_obj_bigquery = Cloud_Account.objects.get(cloud_name="symbolic-wind-391716-GCP")

def get_daily_cost():

    # Path to the service account key file
    ROOT_DIR = Path("/")
    KEYFILE_PATH = ROOT_DIR / 'var' / 'tmp' / '{}_billow-user.json'.format(gcp_obj_bigquery.project_id)

    # Use the service account key file for authentication
    credentials = service_account.Credentials.from_service_account_file(KEYFILE_PATH)
    client = bigquery.Client(credentials=credentials)

    current_date = datetime.today()
    start_date = current_date - timedelta(hours=24)
    start_date_str = start_date.strftime('%Y-%m-%d')
    current_date_str = current_date.strftime('%Y-%m-%d')

    #this wont work now need to make a bigquery in symbolic
    # Construct the SQL query
    #from symbolic-wind-391716.symbolic_wind_391716."gcp_billing_export..." in quotes is the name gcp gives the new dataset
    query = """
    SELECT SUM(cost) AS total_cost
    FROM `symbolic-wind-391716.symbolic_wind_391716.gcp_billing_export_v1_01303E_0AA329_074C39`
    WHERE TIMESTAMP_TRUNC(_PARTITIONTIME, DAY) = TIMESTAMP("{}")
    """.format(start_date_str, current_date_str)

    # Execute the query
    query_job = client.query(query)

    # Fetch the query results
    result = query_job.result()

    # Process the result
    for row in result:
        total_cost = row[0]
    return total_cost

def display_total_cost(params):

    total_cost = 0
    date_format = '%Y-%m-%d'
    use_date = dt.strptime(params['start_date'][0:10], date_format)
    end_date = dt.strptime(params['end_date'][0:10], date_format)
    for items in Billing.objects.all() :
        get_date = use_date.strftime("%Y-%m-%d-%H-%M-%S")[0:10]
        use_date = use_date + timedelta(days=1)
        find_date = Billing_Snap_Index.objects.get(timestamp__startswith = get_date)
        account = Cloud_Account.objects.get(cloud_name = 'symbolic-wind-391716-GCP')
        billing_date = Billing.objects.filter(billing_snap_index_obj = find_date)
        one_cost = billing_date.get(cloud_account = account).daily_cost

        total_cost += one_cost
        if use_date > end_date :
           break
    total_cost = (float(total_cost))
    return total_cost



def wait_for_extended_operation(
    operation: ExtendedOperation, verbose_name: str = "operation", timeout: int = 300
) -> Any:
    """
    Waits for the extended (long-running) operation to complete.

    If the operation is successful, it will return its result.
    If the operation ends with an error, an exception will be raised.
    If there were any warnings during the execution of the operation
    they will be printed to sys.stderr.

    Args:
        operation: a long-running operation you want to wait on.
        verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
        timeout: how long (in seconds) to wait for operation to finish.
            If None, wait indefinitely.

    Returns:
        Whatever the operation.result() returns.

    Raises:
        This method will raise the exception received from `operation.exception()`
        or RuntimeError if there is no exception set, but there is an `error_code`
        set for the `operation`.

        In case of an operation taking longer than `timeout` seconds to complete,
        a `concurrent.futures.TimeoutError` will be raised.
    """
    result = operation.result(timeout=timeout)


    if operation.error_code:
        print(
            f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}",
            file=sys.stderr,
            flush=True,
        )
        print(f"Operation ID: {operation.name}", file=sys.stderr, flush=True)
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        print(f"Warnings during {verbose_name}:\n", file=sys.stderr, flush=True)
        for warning in operation.warnings:
            print(f" - {warning.code}: {warning.message}", file=sys.stderr, flush=True)

    return result


def start_instance(project_id, zone, instance_name, user) -> None:

    file_name = find_service_for_instance(project_id, instance_name, user)

    ROOT_DIR = Path("/")
    KEYFILE_PATH = ROOT_DIR / 'var' / 'tmp' / file_name

    credentials = service_account.Credentials.from_service_account_file(KEYFILE_PATH)
    instance_client = compute_v1.InstancesClient(credentials=credentials)
    i = 0
    while i < len(zone):
        if zone[i] == "/":
            zone = zone[i + 1:]
            break
        i = i + 1
    """
    Starts a stopped Google Compute Engine instance (with unencrypted disks).
    Args:
        project_id: project ID or project number of the Cloud project your instance belongs to.
        zone: name of the zone your instance belongs to.
        instance_name: name of the instance your want to start.
    """

    operation = instance_client.start(
        project=project_id, zone=zone, instance=instance_name
    )

    wait_for_extended_operation(operation, "instance start")


def stop_instance(project_id, zone, instance_name, user) -> None:

    file_name = find_service_for_instance(project_id, instance_name, user)
    ROOT_DIR = Path("/")
    KEYFILE_PATH = ROOT_DIR / 'var' / 'tmp' / file_name

    credentials = service_account.Credentials.from_service_account_file(KEYFILE_PATH)
    instance_client = compute_v1.InstancesClient(credentials=credentials)

    i = 0
    while i < len(zone):
        if zone[i] == "/":
            zone = zone[i + 1:]
            break
        i = i + 1
    """
    Stops a running Google Compute Engine instance.
    Args:
        project_id: project ID or project number of the Cloud project your instance belongs to.
        zone: name of the zone your instance belongs to.
        instance_name: name of the instance your want to stop.
    """

    operation = instance_client.stop(
        project=project_id, zone=zone, instance=instance_name
    )
    wait_for_extended_operation(operation, "instance stopping")


def delete_instance(project_id: str, zone: str, machine_name: str) -> None:
    """
    Send an instance deletion request to the Compute Engine API and wait for it to complete.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        zone: name of the zone you want to use. For example: “us-west3-b”
        machine_name: name of the machine you want to delete.
    """
    file_name = find_service_for_instance(project_id, instance_name, user)
    ROOT_DIR = Path("/")
    KEYFILE_PATH = ROOT_DIR / 'var' / 'tmp' / file_name

    credentials = service_account.Credentials.from_service_account_file(KEYFILE_PATH)
    instance_client = compute_v1.InstancesClient(credentials=credentials)

    i = 0
    while i < len(zone):
        if zone[i] == "/":
            zone = zone[i + 1:]
            break
        i = i + 1

    print(f"Deleting {machine_name} from {zone}...")
    operation = instance_client.delete(
        project=project_id, zone=zone, instance=machine_name
    )
    wait_for_extended_operation(operation, "instance deletion")
    print(f"Instance {machine_name} deleted.")



def list_all_instances(project_id: str) -> dict[str, Iterable[compute_v1.Instance]]:
    """
    Returns a dictionary of all instances present in a project, grouped by zone.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.

    Returns:
        A dictionary with zone as keys and lists of instances as values.
    """

    ROOT_DIR = Path("/")
    KEYFILE_PATH = ROOT_DIR / 'var' / 'tmp' / '{}_instances.json'.format(project_id)

    credentials = service_account.Credentials.from_service_account_file(KEYFILE_PATH)
    instance_client = compute_v1.InstancesClient(credentials=credentials)
    request = compute_v1.AggregatedListInstancesRequest()
    request.project = project_id
    request.max_results = 50

    agg_list = instance_client.aggregated_list(request=request)

    all_instances = {}
    instance_details = []
    for zone, response in agg_list:
        if response.instances:
            instances_list = response.instances
            instance_zone = zone[6:]
            for instance in instances_list:
                instance_name = instance.name
                instance_status = instance.status
                instance_machine = instance.machine_type
                for m in instance.network_interfaces:
                    instance_network = m.network

                instance_details.append({
                    'name': instance_name,
                    'id': project_id,
                    'status': instance_status,
                    'zone': instance_zone,
                    'machine_type': instance_machine,
                    'network': instance_network,
                })
    return instance_details

def gcp_daily_snapshot(params):
    total_cost = get_daily_cost()


    new_bill_save = Billing(
        cloud_account = Cloud_Account.objects.get(cloud_name = 'symbolic-wind-391716-GCP'),
        daily_cost = total_cost,
        billing_snap_index_obj = params
    )
    new_bill_save.save()
    print("Gcp daily cost saved to db")

def instance_info(project_id):
    info_list = list_all_instances(project_id)

    for n in info_list:
        # Check if the instance already exists in the database based on the 'instance_name'
        if not Gcp_instance.objects.filter(instance_name=n['name']).exists():
            instance_save = Gcp_instance(
                project=project_id,
                zone=n['zone'],
                instance_name=n['name'],
                machine_type=n['machine_type'],
                network_link=n['network'],
            )
            instance_save.save()
            print(f"Added instance '{n['name']}' to the database.")
        else:
            print(f"Instance '{n['name']}' already exists in the database. Skipped.")

    print("worked")

#get serivce account for the project_id passed (create_imstance)
def get_service_account(project_id):
    print(project_id)
    cloud_account = Cloud_Account.objects.filter(project_id=project_id)
    service_account = []
    for n in cloud_account:
        service_account.append(n.subscription_id)
    print(service_account)
    return service_account

#find service account for existing instance
def find_service_for_instance(project_id, instance_name, user):
    instance = Gcp_instance.objects.get(instance_name=instance_name)
    username = instance.created_by
    user = user.strip()
    username = str(username)
    print(username)
    print(project_id)
    print(instance_name)
    print("user:{}||".format(user))
    if username == user or user == "admin":
        user_id = User.objects.get(username=username).id
        program = Program.objects.get(program_poc_obj=user_id).program_name
        program_id = Program.objects.get(program_name=program).id
        team_name = Team.objects.get(program_obj=program_id).team_name
        cloud_provider = Cloud_Account_Team_Name.objects.filter(team_name__team_name=team_name)
        print(cloud_provider)
        for n in cloud_provider:
            account = Cloud_Account.objects.get(cloud_name = n)
            if project_id in account.cloud_name:
                account = account
                sub_id = account.subscription_id
        file_name = find_cred(project_id, sub_id)
        return file_name
    else:
        raise PermissionDenied("You do not have permission to access this service.")

# fin the right credential for that project_id
def find_cred(project_id, sub_id):
    search_path = Path("/var/tmp/")
    matching_files = []
    file_name = "{}_{}.json".format(project_id, sub_id)

    for file_path in search_path.glob(file_name):
        if file_path.is_file():
            matching_files.append(file_path)

    if matching_files:
        print("Matching files:")
        for file_path in matching_files:
            print(file_path)
            return file_name
    else:
        print(f"No files matching '{file_name}' found in the specified path.")

    return matching_files

def create_instance_gcp(
    project_id: str,
    zone: str,
    instance_name: str,
    disks: list[compute_v1.AttachedDisk] = None,
    machine_type: str = "n1-standard-1",
    network_link: str = "global/networks/default",
    subnetwork_link: str = None,
    internal_ip: str = None,
    external_access: bool = False,
    external_ipv4: str = None,
    accelerators: list[compute_v1.AcceleratorConfig] = None,
    preemptible: bool = False,
    spot: bool = False,
    instance_termination_action: str = "STOP",
    custom_hostname: str = None,
    delete_protection: bool = False,
) -> compute_v1.Instance:
    """
    Send an instance creation request to the Compute Engine API and wait for it to complete.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        zone: name of the zone to create the instance in. For example: "us-west3-b"
        instance_name: name of the new virtual machine (VM) instance.
        disks: a list of compute_v1.AttachedDisk objects describing the disks
            you want to attach to your new instance.
        machine_type: machine type of the VM being created. This value uses the
            following format: "zones/{zone}/machineTypes/{type_name}".
            For example: "zones/europe-west3-c/machineTypes/f1-micro"
        network_link: name of the network you want the new instance to use.
            For example: "global/networks/default" represents the network
            named "default", which is created automatically for each project.
        subnetwork_link: name of the subnetwork you want the new instance to use.
            This value uses the following format:
            "regions/{region}/subnetworks/{subnetwork_name}"
        internal_ip: internal IP address you want to assign to the new instance.
            By default, a free address from the pool of available internal IP addresses of
            used subnet will be used.
        external_access: boolean flag indicating if the instance should have an external IPv4
            address assigned.
        external_ipv4: external IPv4 address to be assigned to this instance. If you specify
            an external IP address, it must live in the same region as the zone of the instance.
            This setting requires `external_access` to be set to True to work.
        accelerators: a list of AcceleratorConfig objects describing the accelerators that will
            be attached to the new instance.
        preemptible: boolean value indicating if the new instance should be preemptible
            or not. Preemptible VMs have been deprecated and you should now use Spot VMs.
        spot: boolean value indicating if the new instance should be a Spot VM or not.
        instance_termination_action: What action should be taken once a Spot VM is terminated.
            Possible values: "STOP", "DELETE"
        custom_hostname: Custom hostname of the new VM instance.
            Custom hostnames must conform to RFC 1035 requirements for valid hostnames.
        delete_protection: boolean value indicating if the new virtual machine should be
            protected against deletion or not.
    Returns:
        Instance object.
    """
    """ROOT_DIR = Path("/")
    KEYFILE_PATH = ROOT_DIR / 'var' / 'tmp' / "symbolic-wind-391716_billow-user.json"

    credentials = service_account.Credentials.from_service_account_file(KEYFILE_PATH)"""

    sub_id_list = get_service_account(project_id)

    for sub_id in sub_id_list:
        ROOT_DIR = Path("/")
        KEYFILE_PATH = ROOT_DIR / 'var' / 'tmp' / "{}_{}.json".format(project_id, sub_id)
        credentials = service_account.Credentials.from_service_account_file(KEYFILE_PATH)
        compute_client = compute_v1.InstancesClient(credentials=credentials)

        INSTANCE_NAME = instance_name
        MACHINE_TYPE = "projects/{}/zones/{}/machineTypes/{}".format(project_id, zone, machine_type)
        SUBNETWORK = "projects/{}/regions/{}/subnetworks/default".format(project_id, zone[:-2])
        SOURCE_IMAGE = "projects/debian-cloud/global/images/family/debian-10"
        NETWORK_INTERFACE = {
            'subnetwork' : SUBNETWORK,
            'access_configs' : [
                {
                    'name' : 'External NAT'
                }
            ]
        }

        config = {
            'name' : INSTANCE_NAME,
            'machine_type': MACHINE_TYPE,
            'disks': [
                {
                    'boot': True,
                    'auto_delete': True,
                    'initialize_params':{
                        'source_image': SOURCE_IMAGE,
                    }
                }
            ],
            'network_interfaces': [NETWORK_INTERFACE]
        }
        try:
            operation = compute_client.insert(
                project= project_id,
                zone = zone,
                instance_resource = config
            )
            wait_for_extended_operation(operation, "instance created")

            print("created vm {}".format(INSTANCE_NAME))
            break
        except Exception as e:
            print("Failed to create instance with subscription ID {}: {}".format(sub_id, e))
    else:
        print("All available credentials failed. Unable to authenticate.")



def daily_instance_ram():
    gcp_instance = Gcp_instance.objects.all()
    ram_count = 0
    for instance in  gcp_instance:
        if instance.status == "Running":
            machine_type = Cpu_series.objects.get(series = instance.machine_type)
            ram_count = ram_count + machine_type.ram
    return ram_count


def daily_instance_cpu():
    gcp_instance = Gcp_instance.objects.all()
    cpu_count = 0
    for instance in  gcp_instance:
        if instance.status == "Running":
            machine_type = Cpu_series.objects.get(series = instance.machine_type)
            cpu_count = cpu_count + machine_type.cpu
    return cpu_count
