from django.shortcuts import render
from datetime import datetime
from .azure_utils import get_cost

def Azure_total_cost(request):

    start_date_req = request.POST.get('start_date')
    end_date_req = request.POST.get('end_date')
    start_date_object = datetime.strptime(start_date_req, "%Y-%m-%d")
    end_date_object = datetime.strptime(end_date_req, "%Y-%m-%d")
    end_date = end_date_object.strftime("%Y-%m-%dT%H:%M:%SZ")
    start_date = start_date_object.strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {

        'start_date':start_date,
        'end_date':end_date,

    }

    print(params['start_date'])
    total_cost = get_cost(params)
    #total_cost = total_cost[0][0] ### why cant i do this in utils
   # total_cost = float(total_cost)


    return total_cost
