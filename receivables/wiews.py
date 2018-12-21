from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.urls import reverse
#from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
#from django.views.generic import ListView
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

#for validation check this source: https://stackoverflow.com/questions/7948750/custom-form-validation
class WorkTimeJournalView(LoginRequiredMixin, View):
    # Time registration for a selected object (project)
    login_url='/accounts/login/'
    
    form_class = WorkTimeJournalForm

    def get_context(self, request, project_id, modify_id, form):
        project = Project.objects.get(id=project_id)
        employee = request.user.employee
        jr_lines = WorkTimeJournal.objects.filter(created_date_time__gte=utils.start_of_today(),
                                                  created_date_time__lte=utils.end_of_today(),
                                                  employee = employee).order_by('work_time_from').prefetch_related('content_object')

        jr_totals = WorkTimeJournal.objects.filter(created_date_time__gte=utils.start_of_today(),
                                                  created_date_time__lte=utils.end_of_today(),
                                                  employee = employee).aggregate(Sum('work_time'),
                                                                                 Sum('distance'), 
                                                                                 Sum('toll_ring'), 
                                                                                 Sum('ferry'), 
                                                                                 Sum('diet'))
        return {'project': project,
                'employee': employee,
                'jr_lines': jr_lines,
                'jr_totals': jr_totals,
                'modify_id': int(modify_id),
                'form': form
                }

    def get(self, request, project_id, modify_id = 0):
        if modify_id == 0: 
            form = self.form_class()
        else:
            jr_line = WorkTimeJournal.objects.get(id=modify_id)
            form = self.form_class(instance=jr_line)
        
        return render(request, 
                      'salary/registration_journal.html',
                      self.get_context(request, project_id, modify_id, form) 
                      )

    def post(self, request, project_id, modify_id = 0, *args, **kwargs):
        project = Project.objects.get(id=project_id)
        employee = request.user.employee
        form = self.form_class(request.POST)

        if form.is_valid():
            if modify_id == 0:
                journal = form.save(commit=False)
                #print(form.cleaned_data)
            else:
                journal = WorkTimeJournal.objects.get(id=modify_id)
                form = self.form_class(request.POST, instance = journal)
                journal = form.save(commit=False)

            journal.employee = employee
            journal.content_type = ContentType.objects.get_for_model(Project)
            journal.content_object = project
            journal.save()
            
            #if save successfull, generate empty form for new record:            
            form = self.form_class(initial={'employee': employee})

            return redirect(reverse('tjournal', args = [project_id]))
        else:
        # !! Redirect to GET. Stay in POST only if form was not valid.
            return render(request, 
                          'salary/registration_journal.html', 
                          self.get_context(request, project_id, modify_id, form))
    