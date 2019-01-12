from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from receivables.models import Project, SalesOrderHeader, SalesOrderLine

@login_required(login_url='/accounts/login/')
def index(request):
    projects = Project.objects.filter(employees__in = [request.user.employee]).order_by('customer', 'name')
    return render(request, 'salary/registration_list.html', {'projects': projects})
    #return render_to_response('co_manager/index.html')