from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView
from .models import Project, SalesOrderHeader
from .forms import WorkTimeJournalForm

class RegistrationObjectListView(View):
    #List of objects (Projects and sales orders) for time registration
    def get(self, request):
        return HttpResponse('result')
    pass

class WorkTimeJournalListView(ListView):
    def get(self, request):
        return HttpResponse('result')
    #Time registration for a selected object
    pass

class WorkTimeJournalView(View):
    def get(self, request, project_id):
        project = Project.objects.get(id=project_id)
        employee = request.user.employee
        form =  WorkTimeJournalForm(initial={'employee': employee})
        #form.employee = employee
        return render(request, 'salary/registration_journal.html', {'project': project, 'employee': employee, 'form': form})
    #Time registration for a selected object
    pass