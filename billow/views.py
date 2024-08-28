from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.urls import reverse
from gcp_app.views import *
from aws_app.views import aws_total_cost
from azure_app.views import Azure_total_cost
from azure_app.azure_utils import *
from aws_app.aws_utils import *
from gcp_app.gcp_utils import *
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from google.api_core.exceptions import Conflict
#from . import forms
from django.views.generic import CreateView
import logging
from aws_app.models import *
from django.shortcuts import render
from decimal import Decimal
from datetime import date
from django.db.models import Sum
from gcp_app.models import *
from .models import Program, Team, Cloud_Account_Team_Name
# Create your views here.

logger = logging.getLogger(__name__)

def user_login(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        context = {"next" : "index_billow.html"}
        return redirect(next)
    else:
        context["result"] = "Your username/password appears to be invalid. Please try again"
        return render(request, "login.html", context)


def index_billow(request):
    return render(request, 'index_billow.html')

def billow_get_bill(request):
    return render(request, 'billow_get_bill.html')

@csrf_exempt
def billow_bill(request):
    user = request.user.username
    print(user)

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    dates = {
        'start_date': start_date,
        'end_date': end_date
    }
    try:
        if gcp_total_cost(request) == None:
            gcp_total = 0
        else:
            gcp_total = round(gcp_total_cost(request), 2)

        if aws_total_cost(request) == None:
            aws_total = 0
        else:
            aws_total = round(aws_total_cost(request), 2)

        if Azure_total_cost(request) == None:
            azure_total = 0
        else:
            azure_total = round(Azure_total_cost(request), 2)

        total_cost =  round(gcp_total + aws_total + azure_total, 2)

        costs = {
            'aws_total':aws_total, 'gcp_total':gcp_total, 'azure_total':azure_total, 'total_cost':total_cost,
        }

        username = request.user.username

        if username != 'admin':
            user_id = User.objects.get(username = username).id
            program = Program.objects.get(program_poc_obj = user_id).program_name
            program_id = Program.objects.get(program_name = program).id
            team_name = Team.objects.get(program_obj = program_id).team_name

            user_details = {'username':username, 'program':program, 'team':team_name}

            details = {
                'dates':dates, 'costs':costs, 'user_details':user_details,
            }
            logger.info(' By User {} || Bill Created between {} and {}' .format(user, start_date, end_date, ))
            return render(request, 'billow_bill.html', details)
        else:
            ENM_teams = Team.objects.filter(program_obj__program_name='ENM').values()
            EO_teams = Team.objects.filter(program_obj__program_name='EO').values()
            EIC_teams = Team.objects.filter(program_obj__program_name='EIC').values()

            teams = {'ENM_teams':ENM_teams, 'EO_teams':EO_teams, 'EIC_teams':EIC_teams}
            user_details = {'username': username, 'teams': teams}

            details = {
                'dates': dates,'costs': costs,'user_details':user_details,
            }
            logger.info(' By User {} || Bill Created between {} and {}' .format(user, start_date, end_date, ))
            return render(request, 'billow_bill.html', details)
    except Exception as e:
            messages.error(request, "Billng request failed Error: " + str(e))
            return render(request, 'billow_get_bill.html')






def create_instances(request):
    return render(request,'create_instances.html')

def create_gcp_instance_form(request):
    zones = Zone.objects.all().values()
    cpu_series = Cpu_series.objects.all().values()
    project_id = "local-shoreline-386208"
    details = {
        'zones': zones, 'cpu_series': cpu_series, 'project_id': project_id,
        }

    return render(request,'create_gcp_instance.html', details)


def create_gcp_instance(request):
    if request.method == 'POST':
        zone_name = request.POST.get('zone')
        cpu_series = request.POST.get('cpu_series')
        project_id = request.POST.get('project_id')
        instance_name = request.POST.get('instance_name')
        username = request.user.username
        if not Gcp_instance.objects.filter(instance_name = instance_name).exists():
            #try:
            create_instance_gcp(project_id, zone_name, instance_name, cpu_series)
            print("created")
            instance_save = Gcp_instance(
                    project=project_id,
                    zone = Zone.objects.get(zone = zone_name),
                    instance_name= instance_name,
                    machine_type= Cpu_series.objects.get(series = cpu_series),
                    created_by = User.objects.get(username = username )
                    )
            instance_save.save()
            messages.success(request, 'Instance created successfully!')
            return HttpResponseRedirect(reverse('billow:create_gcp_instance_form'))
            """except Exception as e:
                error_message = 'Failed to create instance. Please try again later or contact support.'
                messages.error(request, error_message)
            return HttpResponseRedirect(reverse('billow:create_gcp_instance_form'))"""
        else:
            error_message = f'Instance with name "{instance_name}" already exists. Please choose a different name.'
            messages.error(request, error_message)
            return HttpResponseRedirect(reverse('billow:create_gcp_instance_form'))
    return HttpResponseRedirect(reverse('billow:create_gcp_instance_form'))


def create_aws_instance_form(request):
    image_ids = aws_image.objects.all().values()
    instance_types = aws_instance_type.objects.all().values()
    key_names = aws_keyname.objects.all().values()

    details = {
        'image_ids': image_ids, 'instance_types': instance_types, 'key_names': key_names,
        }

    return render(request,'create_aws_instance.html', details)

def create_aws_instance(request):
    user = request.user.username
    if request.method == 'POST':
        image_id = request.POST.get('image_id')
        instance_type = request.POST.get('instance_type')
        key_name = request.POST.get('key_name')
        instance_name = request.POST.get('instance_name')
        storage = request.POST.get('storage')
        region = request.POST.get('region')

        params = {
            'image_id': image_id, 'instance_type': instance_type, 'key_name': key_name, 'instance_name': instance_name, 'storage': storage, 'region': region,
        }

        if not aws_instance.objects.filter(instance_name = instance_name).exists():
            try:
                instance_id = create_instance_aws(params)
                instance_save = aws_instance(
                    instance_name = instance_name,
                    instance_id = instance_id,
                    instance_type = aws_instance_type.objects.get(instance_type = instance_type),
                    created_by = user,
                    region = region,
                    )
                instance_save.save()
                logger.info(' By User {} || AWS instance: {} created ' .format(user, instance_name))
                messages.success(request, 'Instance created successfully!, It will appear in manage instances shortly')
            except Exception as e:
                logger.info(' By User {} || AWS instance: {} failed to be created ' .format(user, instance_name))
                messages.error(request, f'Failed to create instance, please ensure you filled all the required fields correctly' + str(e))
        else:
            logger.info(' By User {} || AWS instance: {} failed to be created ' .format(user, instance_name))
            messages.error(request, f'Failed to create instance, instance with this name already exists')

    return HttpResponseRedirect(reverse('billow:create_aws_instance_form'))

def create_azure_instance_form(request):
    return render(request,'create_azure_instance.html')

def create_azure_instance(request):
    user = request.user.username
    try:
        vm_name = request.POST.get('vm_name')
        os_disk_name = request.POST.get('os_disk_name')
        nic_name = request.POST.get('nic_name')
        region = request.POST.get('region')
        resource_group = request.POST.get('resource_group')
        virtual_network = request.POST.get('virtual_network')

        params = {
            'vm_name': vm_name, 'os_disk_name': os_disk_name,  'nic_name': nic_name,
            'region': region, 'resource_group': resource_group, 'virtual_network': virtual_network
        }

        create_instance_azure(params, request)
        logger.info(' By User {} || Azure instance: {} created ' .format(user, vm_name))
        messages.success(request, 'Instance created successfully!, It will appear in manage instances shortly')
    except Exception as e:
        logger.info(' By User {} || Azure instance: {} failed to be created ' .format(user, vm_name) )
        messages.error(request, f'Failed to create instance, please ensure you filled all the required fields correctly: ' + str(e))

    return HttpResponseRedirect(reverse('billow:create_azure_instance_form'))

def user_auth(username, program_name1):
    # user auth
    programs = Program.objects.all()
    program = None  # Assign a default value
    user_details = []

    if username != 'admin':
        user_id = User.objects.get(username=username).id
        program = Program.objects.get(program_poc_obj=user_id).program_name
        program_id = Program.objects.get(program_name=program).id
        team_name = Team.objects.get(program_obj=program_id).team_name
        cloud_account= Cloud_Account_Team_Name.objects.filter(team_name__team_name=team_name)
        #cloud_provider = Cloud_Account.objects.filter(cloud_name=cloud_account).cloud_details
        user_details.append({
            'username': username,
            'user_id': user_id,
            'program': program,
            'program_id': program_id,
            'team_name': team_name,
            #'cloud_account': cloud_account,
            #'cloud_provider': cloud_provider,
        })
        for accounts in cloud_account:
            project_id = Cloud_Account.objects.get(cloud_name=accounts).project_id
            sub_id = Cloud_Account.objects.get(cloud_name=accounts).subscription_id
            cloud_name = Cloud_Account.objects.get(cloud_name=accounts)
            cloud_provider = cloud_name.cloud_details
            user_details.append({
                'cloud_name': cloud_name,
                'cloud_provider': cloud_provider,
                'project_id':project_id,
                'sub_id':sub_id,
            })

    else:

        if program_name1:
            program_obj = Program.objects.get(program_name=program_name1)
            team_name = Team.objects.get(program_obj=program_obj).team_name
            cloud_account = Cloud_Account_Team_Name.objects.filter(team_name__team_name=team_name)
            #cloud_provider = Cloud_Account.objects.get(cloud_name=cloud_account).cloud_details
            user_details.append({
                'program_obj':program_obj,
                'team_name':team_name,
                'cloud_account': cloud_account,
                #'cloud_porvider':cloud_provider
            })
            for accounts in cloud_account:
                project_id = Cloud_Account.objects.get(cloud_name=accounts).project_id
                sub_id = Cloud_Account.objects.get(cloud_name=accounts).subscription_id
                cloud_name = Cloud_Account.objects.get(cloud_name=accounts)
                cloud_provider = cloud_name.cloud_details
                user_details.append({
                    'cloud_name': cloud_name,
                    'cloud_provider': cloud_provider,
                    'project_id':project_id,
                    'sub_id':sub_id,
                })
        else:
            team_name = None
            cloud_account = Cloud_Account_Team_Name.objects.all()
            cloud_provider = Cloud_Provider.objects.all()
            user_details.append({
                'username':username,
                'team_name':team_name,
                'cloud_account': cloud_account,
            })
            for clouds in cloud_provider:
                user_details.append({
                    'cloud_provider': clouds
                })
    return user_details

def organize_by_project_id(user_accounts):
    gcp_instances_by_project = {}
    for n in user_accounts:
            project_id = n['project_id']
            gcp_instances = Gcp_instance.objects.filter(project=project_id)
            for instance in gcp_instances:
                project_id = instance.project
                if project_id not in gcp_instances_by_project:
                    gcp_instances_by_project[project_id] = []
                gcp_instances_by_project[project_id].append(instance)
    return gcp_instances_by_project


def manage_instances(request):
    azure_instances = Azure_instance.objects.all() # AZURE
    aws_instances = aws_instance.objects.all() #AWS
    user = request.user.username #The user
    program_name1 = request.GET.get('program') # The program called from admin

    if user != "admin":
        user_detail = user_auth(user, program_name1)
        user_accounts = user_detail[1:]
        user_detail = user_detail[0]
        programs = Program.objects.all()
        gcp_instances_by_project = organize_by_project_id(user_accounts)
    else:
        if program_name1:
            user_detail = user_auth(user, program_name1)
            user_accounts = user_detail[1:]
            user_detail = user_detail[0]
            programs = Program.objects.all()
            gcp_instances_by_project = organize_by_project_id(user_accounts)
        else:
            gcp_instances = Gcp_instance.objects.all() # GCP
            user = request.user.username
            program_name1 = request.GET.get('program')
            user_detail = user_auth(user, program_name1)
            user_accounts = user_detail[1:]
            user_detail = user_detail[0]
            programs = Program.objects.all()

            #Organize instances by project_id
            gcp_instances_by_project = {}
            for instance in gcp_instances:
                project_id = instance.project
                if project_id not in gcp_instances_by_project:
                    gcp_instances_by_project[project_id] = []
                gcp_instances_by_project[project_id].append(instance)

    all_instance_info = {
        'aws': aws_instances,
        'azure': azure_instances,
        'gcp': gcp_instances_by_project  # Use the grouped dictionary here
    }

    return render(request, 'manage_instances.html', {
        'all_instance_info': all_instance_info,
        'user_details': user_detail,
        'user_accounts': user_accounts,
        'programs': programs
    })



def instance_action(request):
    user = request.user.username

    if request.method == 'POST':
        actions = request.POST.getlist('actions')
        if 'start_instance_gcp' in actions:
            project_id = request.POST.get('project_id')
            zone = request.POST.get('zone')
            instance_name = request.POST.get('instance_name')
            user = request.user.username
            instance = Gcp_instance.objects.get(instance_name = instance_name)
            instance.status = "Running"
            instance.save()
            start_instance(project_id, zone, instance_name, user)
            logger.info(' By User {} || GCP Instance Started {} ' .format(user, instance_name,))
            return HttpResponseRedirect(reverse('billow:manage_instances'))

        elif 'stop_instance_gcp' in actions:
            project_id = request.POST.get('project_id')
            zone = request.POST.get('zone')
            instance_name = request.POST.get('instance_name')
            user = request.user.username
            instance = Gcp_instance.objects.get(instance_name = instance_name)
            instance.status = "Stopped"
            instance.save()
            stop_instance(project_id, zone, instance_name, user)
            logger.info(' By User {} || GCP Instance Stopped {}' .format(user, instance_name,))
            return HttpResponseRedirect(reverse('billow:manage_instances'))

        elif 'delete_instance_gcp' in actions:
            project_id = request.POST.get('project_id')
            zone = request.POST.get('zone')
            instance_name = request.POST.get('instance_name')
            instance = Gcp_instance.objects.get(instance_name = instance_name).delete()
            delete_instance(project_id, zone, instance_name)
            logger.info(' By User {} || GCP Instance delete {}' .format(user, instance_name,))
            return HttpResponseRedirect(reverse('billow:manage_instances'))

        elif 'start_instance_azure' in actions:
            resource_group = request.POST.get('resource_group')
            instance_name = request.POST.get('instance_name')
            instance = Azure_instance.objects.get(instance_name= instance_name)
            instance.status = "Running"
            instance.save()
            start_vm(resource_group, instance_name)
            logger.info(' By User {} || Azure Instance Started {}' .format(user, instance_name,))
            return HttpResponseRedirect(reverse('billow:manage_instances'))

        elif 'stop_instance_azure' in actions:
            resource_group = request.POST.get('resource_group')
            instance_name = request.POST.get('instance_name')
            instance = Azure_instance.objects.get(instance_name= instance_name)
            instance.status = "Stopped"
            instance.save()
            stop_vm(resource_group, instance_name)
            logger.info(' By User {} || Azure Instance Stopped {}' .format(user, instance_name,))
            return HttpResponseRedirect(reverse('billow:manage_instances'))

        elif 'delete_instance_azure' in actions:
            resource_group = request.POST.get('resource_group')
            instance_name = request.POST.get('instance_name')
            instance = Azure_instance.objects.get(instance_name = instance_name).delete()
            delete_vm(resource_group, instance_name)
            logger.info(' By User {} || Azure Instance Deleted {}' .format(user, instance_name,))
            return HttpResponseRedirect(reverse('billow:manage_instances'))

        elif 'start_instance_aws' in actions:
            instance_id = request.POST.get('instance_id')
            if aws_instance.objects.filter(instance_id = instance_id).exists():
                try:
                    start_instance_aws(instance_id)
                    instance = aws_instance.objects.get(instance_id = instance_id)
                    instance.status = 'Running'
                    instance.save()
                    logger.info(' By User {} || AWS Instance Started {}' .format(user, instance_id,))
                    return HttpResponseRedirect(reverse('billow:manage_instances'))
                except Exception as e:
                    logger.info(' By User {} || AWS instance {} failed to start'.format(user, instance_id))
                    return HttpResponseRedirect(reverse('billow:manage_instances'))
            else:
                return HttpResponseRedirect(reverse('billow:manage_instances'))

        elif 'stop_instance_aws' in actions:
            instance_id = request.POST.get('instance_id')
            if aws_instance.objects.filter(instance_id = instance_id).exists():
                try:
                    stop_instance_aws(instance_id)
                    instance = aws_instance.objects.get(instance_id = instance_id)
                    instance.status = 'Stopped'
                    instance.save()
                    logger.info(' By User {} || AWS Instance Stopped {}' .format(user, instance_id,))
                    return HttpResponseRedirect(reverse('billow:manage_instances'))
                except Exception as e:
                    logger.info(' By User {} || AWS instance {} failed to stop'.format(user, instance_id))
                    return HttpResponseRedirect(reverse('billow:manage_instances'))
            else:
                return HttpResponseRedirect(reverse('billow:manage_instances'))

        elif 'delete_instance_aws' in actions:
            instance_id = request.POST.get('instance_id')
            if aws_instance.objects.filter(instance_id = instance_id).exists():
                try:
                    delete_instance_aws(instance_id)
                    instance = aws_instance.objects.get(instance_id = instance_id).delete()
                    logger.info(' By User {} || AWS Instance deleted {}' .format(user, instance_id,))
                    return HttpResponseRedirect(reverse('billow:manage_instances'))
                except Exception as e:
                    logger.info(' By User {} || AWS instance {} failed to be deleted'.format(user, instance_id))
                    return HttpResponseRedirect(reverse('billow:manage_instances'))
            else:
                return HttpResponseRedirect(reverse('billow:manage_instances'))

    return HttpResponseRedirect(reverse('billow:manage_instances'))

def start_all_instances(request):
    user = request.user.username

    # Start GCP instances
    gcp_instances = Gcp_instance.objects.all()
    for instance in gcp_instances:
        zone = str(Zone.objects.get(zone = instance.zone))
        instance_name = instance.instance_name
        instance.status = "Running"
        instance.save()
        start_instance(instance.project, zone, instance_name, user)
        logger.info('By User {} || GCP Instance Started {}'.format(user, instance.instance_name))

    # Start Azure instances
    azure_instances = Azure_instance.objects.all()
    for instance in azure_instances:
        resource_group = instance.resource_group_name
        instance_name = instance.instance_name
        instance.status = "Running"
        instance.save()
        start_vm(resource_group, instance_name)
        logger.info('By User {} || Azure Instance Started {}'.format(user, instance.instance_name))

    # Start AWS instances
    aws_instances = aws_instance.objects.all()
    for instance in aws_instances:
        instance_id = instance.instance_id
        if aws_instance.objects.filter(instance_id=instance_id).exists():
            try:
                start_instance_aws(instance_id)
                instance.status = 'Running'
                instance.save()
                logger.info('By User {} || AWS Instance Started {}'.format(user, instance_id))
            except Exception as e:
                logger.info('By User {} || AWS instance {} failed to start'.format(user, instance_id))

    return HttpResponseRedirect(reverse('billow:manage_instances'))

def stop_all_instances(request):
    user = request.user.username

    # Stop GCP instances
    gcp_instances = Gcp_instance.objects.all()
    for instance in gcp_instances:
        zone = str(Zone.objects.get(zone = instance.zone))
        instance_name = instance.instance_name
        instance.status = "Stopped"
        instance.save()
        stop_instance(instance.project, zone, instance_name, user)
        logger.info('By User {} || GCP Instance Stopped {}'.format(user, instance.instance_name))


    # Stop Azure instances
    azure_instances = Azure_instance.objects.all()
    for instance in azure_instances:
        resource_group = instance.resource_group_name
        instance_name = instance.instance_name
        instance.status = "Stopped"
        instance.save()
        stop_vm(resource_group, instance_name)
        logger.info('By User {} || Azure Instance Stopped {}'.format(user, instance.instance_name))

    # Stop AWS instances
    aws_instances = aws_instance.objects.all()
    for instance in aws_instances:
        instance_id = instance.instance_id
        if aws_instance.objects.filter(instance_id=instance_id).exists():
            try:
                stop_instance_aws(instance_id)
                instance.status = 'Stopped'
                instance.save()
                logger.info('By User {} || AWS Instance Stopped {}'.format(user, instance_id))
            except Exception as e:
                logger.info('By User {} || AWS instance {} failed to stop'.format(user, instance_id))

    return HttpResponseRedirect(reverse('billow:manage_instances'))

def graph_landing_page(request):
    return render(request, 'graph_landing_page.html')

def graph_cost(request):
    # Get start and end dates from the form input fields
    start_date_str = request.GET.get('start_date') or request.POST.get('startDate')
    end_date_str = request.GET.get('end_date') or request.POST.get('endDate')

    if start_date_str and end_date_str:
        # Convert start and end date strings to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Get billing snapshots within the selected date range
        billing_snapshots = Billing_Snap_Index.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)

        # Get billing objects for the selected snapshots
        billing_objects = Billing.objects.filter(billing_snap_index_obj__in=billing_snapshots)

        # Collect daily costs and dates for each cloud provider
        aws_costs = {}
        gcp_costs = {}
        azure_costs = {}

        for billing_object in billing_objects:
            day = billing_object.billing_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if billing_object.cloud_account.cloud_name == 'AWS':
                aws_costs[day] = billing_object.daily_cost
            elif billing_object.cloud_account.cloud_name == 'symbolic-wind-391716-GCP':
                gcp_costs[day] = billing_object.daily_cost
            elif billing_object.cloud_account.cloud_name == 'Azure':
                azure_costs[day] = billing_object.daily_cost

        # Create a list of days within the selected date range
        days_in_range = []
        current_date = start_date
        while current_date <= end_date:
            days_in_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        # Initialize cost lists for each cloud provider, filling missing days with 0 cost
        aws_cost_list = [aws_costs.get(day, 0) for day in days_in_range]
        gcp_cost_list = [gcp_costs.get(day, 0) for day in days_in_range]
        azure_cost_list = [azure_costs.get(day, 0) for day in days_in_range]

        context = {
            'days_in_range': days_in_range,
            'aws_cost_list': aws_cost_list,
            'gcp_cost_list': gcp_cost_list,
            'azure_cost_list': azure_cost_list,
            'start_date': start_date_str,
            'end_date': end_date_str,
        }

    else:
        # Default context when no dates are selected
        context = {
            'days_in_range': [0,0],  # You can provide some default values here
            'aws_cost_list': [0,0],
            'gcp_cost_list': [0,0],
            'azure_cost_list': [0,0],
            'start_date': start_date_str,
            'end_date': end_date_str,
        }

    return render(request, 'graphs.html', context)

def graph_resources(request):
    # Get start and end dates from the form input fields
    start_date_str = request.GET.get('start_date') or request.POST.get('startDate')
    end_date_str = request.GET.get('end_date') or request.POST.get('endDate')
    context = {}

    if start_date_str and end_date_str:
        # Convert start and end date strings to datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Get objects within date range
        instance_snapshots = Instance_Snap_Index.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)

        # Azure resources
        azure_instances_objects = snap_azure_instance.objects.filter(azure_snap_index_obj__in=instance_snapshots)
        azure_resources = {}

        azure_cpus = 0
        for azure_object in azure_instances_objects:
            day = azure_object.azure_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if azure_object.status.lower() == 'running':
                hardware_name = hardware_profile.objects.get(hardware_name=azure_object.harware_name)
                azure_cpus += hardware_name.cpu
                if day in azure_resources:
                    azure_resources[day] += azure_cpus
                else:
                    azure_resources[day] = azure_cpus
            azure_cpus = 0

        # AWS resources
        aws_instances_objects = snap_aws_instance.objects.filter(aws_snap_index_obj__in=instance_snapshots)
        aws_resources = {}

        aws_cpus = 0
        for aws_object in aws_instances_objects:
            day = aws_object.aws_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if aws_object.status.lower() == 'running':
                aws_cpus += aws_object.instance_type.cpu
                if day in aws_resources:
                    aws_resources[day] += aws_cpus
                else:
                    aws_resources[day] = aws_cpus
            aws_cpus= 0

        # GCP resources
        gcp_instances_objects = snap_gcp_instance.objects.filter(gcp_snap_index_obj__in=instance_snapshots)
        gcp_resources = {}

        gcp_cpus = 0
        for gcp_object in gcp_instances_objects:
            day = gcp_object.gcp_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if gcp_object.status.lower() == 'running':
                gcp_cpus += gcp_object.machine_type.cpu
                if day in gcp_resources:
                    gcp_resources[day] += gcp_cpus
                else:
                    gcp_resources[day] = gcp_cpus
            gcp_cpus= 0

        # Create a list of days within the selected date range
        days_in_range = []
        current_date = start_date
        while current_date <= end_date:
            days_in_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        azure_resource_list = [azure_resources.get(day, 0) for day in days_in_range]
        aws_resource_list = [aws_resources.get(day, 0) for day in days_in_range]
        gcp_resource_list = [gcp_resources.get(day, 0) for day in days_in_range]

        azure_ram = {}
        aws_ram = {}
        gcp_ram = {}

        for azure_object in azure_instances_objects:
            day = azure_object.azure_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if azure_object.status.lower() == 'running':
                hardware_name = hardware_profile.objects.get(hardware_name=azure_object.harware_name)
                if day in azure_ram:
                    azure_ram[day] += hardware_name.ram
                else:
                    azure_ram[day] = hardware_name.ram

        aws_instances_objects = snap_aws_instance.objects.filter(aws_snap_index_obj__in=instance_snapshots)

        for aws_object in aws_instances_objects:
            day = aws_object.aws_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if aws_object.status.lower() == 'running':
                if day in aws_ram:
                    aws_ram[day] += aws_object.instance_type.ram
                else:
                    aws_ram[day] = aws_object.instance_type.ram

        for gcp_object in gcp_instances_objects:
            day = gcp_object.gcp_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if gcp_object.status.lower() == 'running':
                if day in gcp_ram:
                    gcp_ram[day] += gcp_object.machine_type.ram
                else:
                    gcp_ram[day] = gcp_object.machine_type.ram

        azure_ram_list = [azure_ram.get(day, 0) for day in days_in_range]
        aws_ram_list = [aws_ram.get(day, 0) for day in days_in_range]
        gcp_ram_list = [gcp_ram.get(day, 0) for day in days_in_range]

        context = {
            'days_in_range': days_in_range,
            'azure_resources': azure_resource_list,
            'aws_resources': aws_resource_list,
            'gcp_resources': gcp_resource_list,
            'azure_ram': azure_ram_list,
            'aws_ram': aws_ram_list,
            'gcp_ram': gcp_ram_list,
            'start_date': start_date_str,
            'end_date': end_date_str,
        }

    else:
        # Default context when no dates are selected
        context = {
            'days_in_range': [0,0],
            'azure_resources': [0,0],
            'aws_resources': [0,0],
            'gcp_resources': [0,0],
            'azure_ram': [0,0],
            'aws_ram': [0,0],
            'gcp_ram': [0,0],
            'start_date': start_date_str,
            'end_date': end_date_str,
        }

    return render(request, 'graph_resources.html', context)

def project_inventory(request):
    # Retrieve all projects and related data
    user = request.user.username
    username = request.user.username

    dates = {

    }
    if username != 'admin':
            user_id = User.objects.get(username = username).id
            program = Program.objects.get(program_poc_obj = user_id).program_name
            program_id = Program.objects.get(program_name = program).id
            team_name = Team.objects.get(program_obj = program_id).team_name

            user_details = {'username':username, 'program':program, 'team':team_name}

            details = {
                'dates':dates, 'user_details':user_details,
            }
    else:
            ENM_teams = Team.objects.filter(program_obj__program_name='ENM').values()
            EO_teams = Team.objects.filter(program_obj__program_name='EO').values()
            EIC_teams = Team.objects.filter(program_obj__program_name='EIC').values()

            teams = {'ENM_teams':ENM_teams, 'EO_teams':EO_teams, 'EIC_teams':EIC_teams}
            user_details = {'username': username, 'teams': teams}

            details = {
                'dates': dates,'user_details':user_details,
            }

    projects = Program.objects.all()
    project_data = []

    for project in projects:
        # Get the associated team for the project
        try:
            team = Team.objects.get(program_obj=project)
            team_name = team.team_name
        except Team.DoesNotExist:
            team_name = "Not Assigned"

        # Get the associated cloud accounts for the team
        cloud_accounts = Cloud_Account_Team_Name.objects.filter(team_name=team)
        provider_data = []

        for cloud_account in cloud_accounts:
            provider = cloud_account.cloud_account.cloud_details.cloud_name
            provider_data.append({'team_name': team_name, 'cloud_provider': provider})

        project_data.append({
            'project_name': project.program_name,
            'team_name': team_name,
            'providers': provider_data,
        })

    azure_instances = Azure_instance.objects.all()  # AZURE
    aws_instances = aws_instance.objects.all()  # AWS
    user = request.user.username  # The user
    program_name1 = request.GET.get('program')  # The program called from admin

    if user != "admin":
        user_detail = user_auth(user, program_name1)
        user_accounts = user_detail[1:]
        user_detail = user_detail[0]
        programs = Program.objects.all()
        gcp_instances_by_project = organize_by_project_id(user_accounts)
    else:
        if program_name1:
            user_detail = user_auth(user, program_name1)
            user_accounts = user_detail[1:]
            user_detail = user_detail[0]
            programs = Program.objects.all()
            gcp_instances_by_project = organize_by_project_id(user_accounts)
        else:
            gcp_instances = Gcp_instance.objects.all()  # GCP
            user = request.user.username
            program_name1 = request.GET.get('program')
            user_detail = user_auth(user, program_name1)
            user_accounts = user_detail[1:]
            user_detail = user_detail[0]
            programs = Program.objects.all()

            # Organize instances by project_id
            gcp_instances_by_project = {}
            for instance in gcp_instances:
                project_id = instance.project
                if project_id not in gcp_instances_by_project:
                    gcp_instances_by_project[project_id] = []
                gcp_instances_by_project[project_id].append(instance)

            gcp_instances_by_project = list(Gcp_instance.objects.all())

        all_instance_info = {
        'aws': list(aws_instances),
        'azure': list(azure_instances),
        'gcp': gcp_instances_by_project,
    }

    # Flatten the structure
    flat_instance_info = {}
    for provider, instances in all_instance_info.items():
        flat_instance_info[provider] = instances

    context = {
        'project_data': project_data,
        'all_instance_info': flat_instance_info,
        'details': details,
    }
    print(context)
    return render(request, 'project_inventory.html', context)



def program_graph_cost(request, provider_name):
    if 'gcp' in provider_name.lower():
        provider_name ='symbolic-wind-391716-GCP'
    # Set the end date to the current date
    end_date = timezone.now()

    # Calculate the start date as the end date minus 20 days
    start_date = end_date - timedelta(days=20)

    # Get billing snapshots within the last 21 days
    billing_snapshots = Billing_Snap_Index.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)

    # Get billing objects for the selected snapshots and provider
    billing_objects = Billing.objects.filter(
        billing_snap_index_obj__in=billing_snapshots,
        cloud_account__cloud_name=provider_name
    )

    # Collect daily costs and dates
    costs = {}
    for billing_object in billing_objects:
        day = billing_object.billing_snap_index_obj.timestamp.strftime('%Y-%m-%d')
        costs[day] = billing_object.daily_cost

    # Create a list of days within the last 21 days
    days_in_range = [(end_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(20, -1, -1)]

    # Initialize cost list, filling missing days with 0 cost
    cost_list = [costs.get(day, 0) for day in days_in_range]
    if 'symbolic-wind-391716-GCP' in provider_name.lower():
        provider_name ='GCP'

    context = {
        'days_in_range': days_in_range,
        'cost_list': cost_list,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'provider_name': provider_name,
    }

    return render(request, 'program_graph_cost.html', context)

def program_resource_graph(request, provider_name):
    # Get end date from the form input fields
    end_date_str = request.GET.get('end_date') or request.POST.get('endDate')
    context = {}

    if end_date_str:
        # Convert end date string to datetime object
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Calculate start date as end date minus 21 days
        start_date = end_date - timedelta(days=21)

        # Get objects within date range
        instance_snapshots = Instance_Snap_Index.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)

        # Azure resources
        azure_instances_objects = snap_azure_instance.objects.filter(azure_snap_index_obj__in=instance_snapshots)
        azure_resources = {}

        azure_cpus = 0
        for azure_object in azure_instances_objects:
            day = azure_object.azure_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if azure_object.status.lower() == 'running':
                hardware_name = hardware_profile.objects.get(hardware_name=azure_object.harware_name)
                azure_cpus += hardware_name.cpu
                if day in azure_resources:
                    azure_resources[day] += azure_cpus
                else:
                    azure_resources[day] = azure_cpus
            azure_cpus = 0

        # AWS resources
        aws_instances_objects = snap_aws_instance.objects.filter(aws_snap_index_obj__in=instance_snapshots)
        aws_resources = {}

        aws_cpus = 0
        for aws_object in aws_instances_objects:
            day = aws_object.aws_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if aws_object.status.lower() == 'running':
                aws_cpus += aws_object.instance_type.cpu
                if day in aws_resources:
                    aws_resources[day] += aws_cpus
                else:
                    aws_resources[day] = aws_cpus
            aws_cpus= 0

        # GCP resources
        gcp_instances_objects = snap_gcp_instance.objects.filter(gcp_snap_index_obj__in=instance_snapshots)
        gcp_resources = {}

        gcp_cpus = 0
        for gcp_object in gcp_instances_objects:
            day = gcp_object.gcp_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if gcp_object.status.lower() == 'running':
                gcp_cpus += gcp_object.machine_type.cpu
                if day in gcp_resources:
                    gcp_resources[day] += gcp_cpus
                else:
                    gcp_resources[day] = gcp_cpus
            gcp_cpus= 0

        # Create a list of days within the selected date range
        days_in_range = []
        current_date = start_date
        while current_date <= end_date:
            days_in_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

        azure_resource_list = [azure_resources.get(day, 0) for day in days_in_range]
        aws_resource_list = [aws_resources.get(day, 0) for day in days_in_range]
        gcp_resource_list = [gcp_resources.get(day, 0) for day in days_in_range]

        azure_ram = {}
        aws_ram = {}
        gcp_ram = {}

        for azure_object in azure_instances_objects:
            day = azure_object.azure_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if azure_object.status.lower() == 'running':
                hardware_name = hardware_profile.objects.get(hardware_name=azure_object.harware_name)
                if day in azure_ram:
                    azure_ram[day] += hardware_name.ram
                else:
                    azure_ram[day] = hardware_name.ram

        aws_instances_objects = snap_aws_instance.objects.filter(aws_snap_index_obj__in=instance_snapshots)

        for aws_object in aws_instances_objects:
            day = aws_object.aws_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if aws_object.status.lower() == 'running':
                if day in aws_ram:
                    aws_ram[day] += aws_object.instance_type.ram
                else:
                    aws_ram[day] = aws_object.instance_type.ram

        for gcp_object in gcp_instances_objects:
            day = gcp_object.gcp_snap_index_obj.timestamp.strftime('%Y-%m-%d')
            if gcp_object.status.lower() == 'running':
                if day in gcp_ram:
                    gcp_ram[day] += gcp_object.machine_type.ram
                else:
                    gcp_ram[day] = gcp_object.machine_type.ram

        azure_ram_list = [azure_ram.get(day, 0) for day in days_in_range]
        aws_ram_list = [aws_ram.get(day, 0) for day in days_in_range]
        gcp_ram_list = [gcp_ram.get(day, 0) for day in days_in_range]

        if provider_name.lower() =='aws':
            context = {
                'days_in_range': days_in_range,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'provider_cpus': aws_resource_list,
                'provider_ram':aws_ram_list,
                'end_date': end_date_str,
                'provider_name': provider_name,
            }
        elif provider_name.lower() == 'azure':
            context = {
                'days_in_range': days_in_range,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'provider_cpus': azure_resource_list,
                'provider_ram':azure_ram_list,
                'end_date': end_date_str,
                'provider_name': provider_name,
            }
        else: context = {
                    'days_in_range': days_in_range,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'provider_cpus': gcp_resource_list,
                    'provider_ram':gcp_ram_list,
                    'end_date': end_date_str,
                    'provider_name': provider_name,
                }
        print(context)
        return render(request, 'program_resource_graph.html', context)

    else:
        # Default context when no dates are selected
        context = {
            'days_in_range': [0, 0],
            'cpu_resources': [0, 0],
            'ram_resources': [0, 0],
            'start_date': '',
            'end_date': '',
            'provider_name': provider_name,
        }

        return render(request, 'program_resource_graph.html', context)