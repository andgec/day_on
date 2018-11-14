from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.views.generic import ListView
from .models import Project, SalesOrderHeader, WorkTimeJournal
from .forms import WorkTimeJournalForm
from shared import utils

'''
class RegistrationObjectListView(View):
    #List of objects (Projects and sales orders) for time registration
    def get(self, request):
        return HttpResponse('result')
    pass


class WorkTimeJournalListView(ListView):
    def get(self, request):
        return HttpResponse('result')
    # Time registration for a selected object
    pass
'''

class WorkTimeJournalView(View):
    # Time registration for a selected object (project)
    
    form_class = WorkTimeJournalForm

    def get_context(self, request, project_id, form):
        project = Project.objects.get(id=project_id)
        employee = request.user.employee
        jr_lines = WorkTimeJournal.objects.filter(created_date_time__gte=utils.start_of_today(),
                                                  created_date_time__lte=utils.end_of_today(),
                                                  employee = employee)
        return {'project': project,
                'employee': employee,
                'jr_lines': jr_lines,
                'form': form
                }

    def get(self, request, project_id):
        form = self.form_class()
        print(self.get_context(request, project_id, form))
        return render(request, 
                      'salary/registration_journal.html',
                      self.get_context(request, project_id, form) 
                      )

    def post(self, request, project_id, *args, **kwargs):
        project = Project.objects.get(id=project_id)
        employee = request.user.employee
        form = self.form_class(request.POST)

        if form.is_valid():
            #print(form.cleaned_data)
            journal = form.save(commit=False)
            journal.employee = employee
            journal.content_type = ContentType.objects.get_for_model(Project)
            journal.content_object = project
            journal.save()
            
            #if save successfull, generate empty form for new record:            
            form = self.form_class(initial={'employee': employee}) 
        
        return render(request, 
                      'salary/registration_journal.html', 
                      self.get_context(request, project_id, form))
    