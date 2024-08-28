from django.http import HttpResponse
from django.shortcuts import render, redirect
from gcp_app.gcp_utils import *
from gcp_app.gcp_json import *
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from google.api_core.exceptions import GoogleAPIError
from django.http import HttpResponseServerError



def index(request):
    return render(request, 'index.html', {'test':test})

#for billow
def gcp_total_cost(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    params = {
        'start_date': start_date,
        'end_date': end_date
    }
    gcp_app_cost = display_total_cost(params)
    return gcp_app_cost


def view_start_instance(request):
    project_id = request.POST.get('project_id')
    zone = request.POST.get('zone')
    instance_name = request.POST.get('instance_name')

    # Call the start_instance function and handle the response
    response = start_instance(project_id, zone, instance_name)

    # Return JSON response indicating success or failure
    return render(request, 'project_instances.html', {'response':response})


# View for stopping an instance
def view_stop_instance(request):
    if request.method == "POST":
        # Get the required parameters from the request
        project_id = request.POST.get("project_id")
        zone = request.POST.get("zone")
        instance_name = request.POST.get("instance_name")

        # Call the stop_instance function
        stop_instance(project_id, zone, instance_name)

        # Return a response indicating the success or failure of the stop request
        return JsonResponse({"success": True})



def get_project_instances(request):
    if request.method == 'POST':
        project_id = request.POST.get('project_id')
        return redirect('view_project_instances', project_id=project_id)
    else:
        return render(request, 'get_project_instances.html')



def view_gcp_project_instances(request, project_id):
    try:
        instances = list_all_instances(project_id)
        instance_dict = {instance.name: zone for zone, instances_list in instances.items() for instance in instances_list}
        print(instance_dict)
        return render(request, 'project_instances.html', {'instance_dict': instance_dict, 'instances': instances, 'project_id': project_id})
    except GoogleAPIError as e:
        error_message = str(e)
        return HttpResponseServerError(f"<script>alert('An error occurred: {error_message}');</script>")


def view_project_instances(request, project_id):
    try:
        instances = list_all_instances(project_id)
        instance_dict = {instance.name: zone for zone, instances_list in instances.items() for instance in instances_list}
        gcp_values = {
            'instance_dict': instance_dict,
            'instances': instances,
            'project_id':project_id
        }
        return gcp_values
    except GoogleAPIError as e:
        error_message = str(e)
        return HttpResponseServerError(f"<script>alert('An error occurred: {error_message}');</script>")