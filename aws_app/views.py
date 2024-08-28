from aws_app.aws_utils import get_aws_total_cost

def aws_total_cost(request):

    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    params = {
        'start_date': start_date,
        'end_date': end_date
    }

    return get_aws_total_cost(params)
