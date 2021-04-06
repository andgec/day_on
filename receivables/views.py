from datetime import datetime, date as date_, timedelta
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Max
from django.utils.translation import ugettext_lazy as _
from .models import Project, WorkTimeJournal
from .forms import WorkTimeJournalForm, WorkTimeJournalForm_V2
from general.utils import get_fields_visible


@login_required(login_url='/accounts/login/')
def work_time_journal_proj_list_view(request): # Legacy view
    projects = Project.objects.filter(company = request.user.company, employees__in = [request.user.employee], active = True).order_by('customer__name', 'name').select_related('customer')
    return render(request, 'salary/v1/registration_list.html', {'title': _('Time registration'), 'projects': projects})


class WorkTimeJournalView(LoginRequiredMixin, View): #Legacy view
    # Time registration for a selected object (project)
    login_url='/accounts/login/'
    
    form_class = WorkTimeJournalForm

    def get_context(self, request, project_id, date, jrline_id, action, form):
        company = request.user.company
        employee = request.user.employee
        project = Project.objects.get(id=project_id)
        jr_lines = WorkTimeJournal.objects.filter(company = company,
                                                  work_date = date,
                                                  employee = employee).order_by('work_time_from').prefetch_related('content_object')

        jr_totals = WorkTimeJournal.objects.filter(company = company,
                                                   work_date = date,
                                                   employee = employee).aggregate(Sum('work_time'),
                                                                                  Sum('distance'), 
                                                                                  Sum('toll_ring'), 
                                                                                  Sum('ferry'), 
                                                                                  Sum('diet'),
                                                                                  Sum('parking'),
                                                                                  )
        return {'title': _('Time registration'),
                'date': date,
                'project': project,
                'employee': employee,
                'jr_lines': jr_lines,
                'jr_totals': jr_totals,
                'modify_id': int(jrline_id) if action == 'edit' else 0, #!! messy, rebuild template to fully use 'action' variable.
                'action': action,
                'open': self.get_open(date),
                'form': form
                }

    def get(self, request, project_id, date, jrline_id = 0, action='edit'):
        company = request.user.company

        if jrline_id == 0:
            action = 'view'
        else:
            try:
                jrline = WorkTimeJournal.objects.get(id=jrline_id)
            except:
                action = 'view'
                jrline = None

        if action == 'view':
            form = self.form_class(company=company)
        elif action == 'delete':
            form = self.form_class(company=company)
            jrline.delete();
        elif action == 'edit':
            form = self.form_class(instance=jrline, company=company)

        return render(request, 
                      'salary/v1/registration_journal.html',
                      self.get_context(request, project_id, date, jrline_id, action, form)
                      )

    def post(self, request, project_id, date, jrline_id = 0, *args, **kwargs):
        company = request.user.company
        work_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        if jrline_id == 0:
            journal = None
        else:
            try:
                journal = WorkTimeJournal.objects.get(id=jrline_id)
            except:
                journal = None
            
        request.POST = request.POST.copy()
        
        #Adding date to request data to pass form validation
        request.POST['work_date_day'] = work_date.day
        request.POST['work_date_month'] = work_date.month
        request.POST['work_date_year'] = work_date.year
        request.POST['employee'] = request.user.employee
        
        form =  self.form_class(request.POST, instance = journal, company = company)
        
        project = Project.objects.get(id=project_id)
        employee = request.user.employee
        if form.is_valid():
            journal = form.save(commit=False)
            journal.company = company
            journal.employee = employee 
            journal.content_type = ContentType.objects.get_for_model(Project)
            journal.content_object = project
            journal.work_date = work_date
            journal.save()
            # Redirect to GET. 
            return redirect(reverse('tjournal', args = [project_id, date]))
        else:
            # Stay in POST only if form was not valid.
            return render(request, 
                          'salary/v1/registration_journal.html',
                          self.get_context(request, project_id, date, jrline_id, 'edit', form))

    def get_open(self, work_date):
        today = date_.today()
        last_sunday = today + timedelta(days = -today.weekday() - 1)
        return datetime.strptime(work_date, '%Y-%m-%d').date() > last_sunday


class WorkTimeJournalView_V2(LoginRequiredMixin, View):
    # Time registration for a selected object (project)
    login_url='/accounts/login/'

    form_class = WorkTimeJournalForm_V2

    work_day_start = {
        'hour': 7,
        'minute': 0,
        }

    def get_context(self, request, date, jrline_id, action, form):
        date = date_.today().strftime('%Y-%m-%d') if date is None else date
        employee = request.user.employee
        company = request.user.company
        jr_lines = WorkTimeJournal.objects.filter(company = company,
                                                  work_date = date,
                                                  employee = employee).order_by('work_time_from').prefetch_related('content_object')

        jr_totals = WorkTimeJournal.objects.filter(company = company,
                                                   work_date = date,
                                                   employee = employee).aggregate(Sum('work_time'),
                                                                                  Sum('distance'),
                                                                                  Sum('toll_ring'),
                                                                                  Sum('ferry'),
                                                                                  Sum('diet'),
                                                                                  Sum('parking'),
                                                                                  Max('work_time_to'))
        if jr_lines.count() > 0:
            hour = jr_totals['work_time_to__max'].hour
            minute = jr_totals['work_time_to__max'].minute
        else:
            hour = self.work_day_start['hour']
            minute = self.work_day_start['minute']

        return {'title': _('Time registration'),
                'date': date,
                'employee': employee,
                'jr_lines': jr_lines,
                'jr_totals': jr_totals,
                'modify_id': int(jrline_id) if action == 'edit' else 0, #!! messy, rebuild template to fully use 'action' variable.
                'action': action,
                'open': self.get_open(date) or request.user.is_superuser,
                'form': form,
                'prj_dropdown': Project.objects.filter(company = company,
                                                       employees__in = [request.user.employee],
                                                       active = True,
                                                       customer__active = True,
                                                       ).order_by('name'),
                'time_dropdown': {'hr': str(hour).zfill(2), 'min': str(minute).zfill(2)},
                'fvisible': get_fields_visible(company),
                }

    def get(self, request, date = None, jrline_id = 0, action='edit'):
        company = request.user.company

        if jrline_id == 0:
            action = 'view'
        else:
            try:
                jrline = WorkTimeJournal.objects.get(id=jrline_id)
            except:
                action = 'view'
                jrline = None

        if action == 'view':
            form = self.form_class(company=company)
        elif action == 'delete':
            form = self.form_class(company=company)
            jrline.delete();
        elif action == 'edit':
            form = self.form_class(instance=jrline, company=company)

        return render(request,
                      'salary/v2/registration_journal.html',
                      self.get_context(request, date, jrline_id, action, form)
                      )

    def post(self, request, date = None, jrline_id = 0, *args, **kwargs):
        company = request.user.company

        work_date = datetime.strptime(date, '%Y-%m-%d').date() if date else date_.today()
        work_date_str = work_date.strftime('%Y-%m-%d')
        if jrline_id == 0:
            journal = None
        else:
            try:
                journal = WorkTimeJournal.objects.get(id=jrline_id)
            except:
                journal = None

        request.POST = request.POST.copy()

        #Adding date and employee to request data to pass form validation
        request.POST['work_date_day'] = work_date.day
        request.POST['work_date_month'] = work_date.month
        request.POST['work_date_year'] = work_date.year
        request.POST['employee'] = request.user.employee

        form =  self.form_class(request.POST, instance = journal, company=company)

        employee = request.user.employee
        if form.is_valid():
            journal = form.save(commit=False)
            journal.company = request.user.company
            journal.employee = employee
            journal.content_type = ContentType.objects.get_for_model(Project)
            journal.work_date = work_date
            journal.save()
            # Redirect to GET.
            return redirect(reverse('tjr-v2', args = [work_date_str]))
        else:
            # Stay in POST only if form was not valid.
            return render(request, 
                          'salary/v2/registration_journal.html',
                          self.get_context(request, work_date_str, jrline_id, 'edit', form))

    def get_open(self, work_date):
        today = date_.today()
        last_sunday = today + timedelta(days = -today.weekday() - 1)
        return datetime.strptime(work_date, '%Y-%m-%d').date() > last_sunday
