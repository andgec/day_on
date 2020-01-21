from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.db.models import Sum
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.utils.decorators import method_decorator
from django.views import View
from receivables.models import Project
from shared.utils import get_contenttypes
from django.db import connection
from .forms import PDashProjectForm, PDashAssignEmployees, ProjectDashTimeReviewForm
#from botocore.vendored.requests.api import request
from receivables.models import WorkTimeJournal
from inventory.models import Item


class RecState:
    VIEW    = 0
    NEW     = 1
    EDIT    = 2
    DELETE  = 3
    OPEN    = 4
    CLOSE   = 5
    
    pk_states = (EDIT, DELETE, OPEN, CLOSE) 


@method_decorator(staff_member_required, name='dispatch')
class ProjectDashboardView(View):
    template = 'prjdash/project_dash.html'
    form_class = PDashProjectForm
    state = RecState.VIEW
    project = None
    customer_id = None
    content_type_id_by_name = None
    
    proj_sql = ''' 
        SELECT
          "receivables_customer"."id" as "customer_id",
          "receivables_customer"."name" as "customer_name",
          Proj."project_id", 
          Proj."project_name",
          Proj."project_category",
          Proj."project_comment",
          Proj."project_active",
          Proj."datetime_created"
        FROM "receivables_customer"
        LEFT OUTER JOIN 
            (
            SELECT  
                "receivables_project"."customer_id",
                "receivables_project"."id" as "project_id", 
                "receivables_project"."name" as "project_name",
                pc."name" as "project_category",
                "receivables_project"."comment" as "project_comment", 
                "receivables_project"."active" as "project_active",
                "django_admin_log"."action_time" as "datetime_created"
            FROM "receivables_project"
            JOIN "django_admin_log" ON ("django_admin_log"."object_id" = "receivables_project"."id"::text)
            LEFT OUTER JOIN "receivables_projectcategory" pc ON (pc."id" = "receivables_project"."category_id")
            WHERE "django_admin_log"."content_type_id" = %s
            AND "django_admin_log"."action_flag" = 1
            ) Proj ON (Proj."customer_id" = "receivables_customer"."id")
        WHERE "receivables_customer"."active" = True
        ORDER BY "receivables_customer"."name" ASC,
                 Proj."project_id" DESC
        '''
    def __init__(self, **kwargs):
        self.content_type_id_by_name = get_contenttypes()        
        super(ProjectDashboardView, self).__init__(**kwargs)

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    def build_result_list(self, result_dicts):
        customers = []
        projects = []
        cust_count = 0;
        prev_cust_id = None
        
        for line in result_dicts:
            if line['customer_id'] != prev_cust_id:
                customers.append({'id': line['customer_id'],
                                  'name': line['customer_name'],
                                  })

                #adding projects for the previous customer
                if cust_count > 0:
                    customers[cust_count-1]['projects'] = projects

                projects = []
                cust_count += 1

            prev_cust_id = line['customer_id']

            if line['project_id']:
                projects.append({'id': line['project_id'],
                                 'name': line['project_name'],
                                 'category': line['project_category'],
                                 'comment': line['project_comment'],
                                 'active': line['project_active'],
                                 'datetime_created': line['datetime_created'].strftime("%Y-%m-%d"),
                                 })
        # Adding projects for the last customer
        if cust_count > 0:
            customers[cust_count-1]['projects'] = projects
            
        return customers


    def get_context(self, request, pk, form = None):
        with connection.cursor() as cursor:
            cursor.execute(self.proj_sql, [self.content_type_id_by_name[(Project._meta.app_label, Project._meta.model_name)]])
            result_dicts = self.dictfetchall(cursor)

        form = self.form_class(instance = self.project if self.state == RecState.EDIT else None)

        context = {'edit': self.state == RecState.EDIT,
                   'focus': {'customer_id': int(self.customer_id) if self.customer_id else None,
                             'project_id': int(pk) if pk else None,
                            },
                   'form': form,
                   'customers': self.build_result_list(result_dicts),
                  }

        return context

    def setstate(self, request, pk, mode):
        state_decoder = {
            '': RecState.VIEW,
            #  'edit': RecState.EDIT,
            'close': RecState.CLOSE,
            'open': RecState.OPEN,
        }
        
        if mode == 'edit':
            self.state = RecState.EDIT
        elif request.method == 'POST':
            self.state = RecState.NEW 
        elif request.method == 'GET':
            self.state = state_decoder.get(request.GET.get('action', ''))
        
        if self.state in RecState.pk_states and pk:
            self.project = Project.objects.get(id=pk)
            self.customer_id = self.project.customer_id
        elif pk:
            self.customer_id = Project.objects.get(id=pk).customer_id
            self.project = None
        else:
            self.customer_id = None
            self.project = None
    
    def process(self, request, pk):
        project = self.project
        if self.state in RecState.pk_states and not pk:
            raise Exception(_('Record ID not provided.'))

        if self.state == RecState.CLOSE:
            project.active = False
            project.save()
            
        elif self.state == RecState.OPEN:
            project.active = True
            project.save()
            

    def get(self, request, pk=None, mode=None):
        self.setstate(request, pk, mode)
        self.process(request, pk)
        return render(request,
                      self.template,
                      self.get_context(request, pk)
                      )
        
    def post(self, request, pk=None, mode=None):
        self.setstate(request, pk, mode)
        form = self.form_class(request.POST, instance=self.project, request=request)
        if form.is_valid():
            project = form.save(commit=True)
            return redirect(reverse('pdash')+str(project.pk))
        else:
            return render(request,
                          self.template,
                          self.get_context(request, pk=pk, form=form)
                          )


@method_decorator(staff_member_required, name='dispatch')
class ProjectDashboardAssignEmployeesView(View):
    template = 'prjdash/assign_employees.html'
    form_class = PDashAssignEmployees

    def get_context(self, request, project):
        form = self.form_class(request=request, project=project)
        context = {
                'form': form,
                'customer': project.customer,
                'project': project
                }
        return context

    def get(self, request, pk=None, mode=None):
        if pk:
            project = project = Project.objects.select_related('customer').get(id=pk)
        return render(request,
                      self.template,
                      self.get_context(request, project)
                      )

    def post(self, request, pk=None):
        if pk:
            project = project = Project.objects.select_related('customer').get(id=pk)
        form = self.form_class(request.POST, request=request, project=project)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('pdash')+str(pk))
        else:
            return render(request,
                          self.template,
                          self.get_context(request, pk)
                          )

        
@method_decorator(staff_member_required, name='dispatch')
class ProjectDashboardPostedTimeReview(View):
    template = 'prjdash/posted_time_review.html'
    content_type_id_by_name = None
    form_class = ProjectDashTimeReviewForm
    model = WorkTimeJournal
    state = RecState.VIEW
    jr_line = None
        
    def __init__(self, **kwargs):
        self.content_type_id_by_name = get_contenttypes()
        super(ProjectDashboardPostedTimeReview, self).__init__(**kwargs)

    def get_context(self, request, project_id, pk=None, mode=None, form=None):
        if not form:
            form = self.form_class(instance = self.jr_line if self.state == RecState.EDIT else None)
        project = Project.objects.select_related('customer').get(id=project_id)
        items = Item.objects.select_related('item_group'
                                            ).prefetch_related('translations'
                                            ).prefetch_related('item_group__translations'
                                            ).only('item_group'
                                            ).order_by('item_group__id', 'id')
        # Putting tasks(or items) into list of tuples and then sorting them by group and name
        items = [(item.item_group.name, item.name, item.id) for item in items]
        items.sort(key = lambda val: (val[0].lower(), val[1].lower(), val[2]))

        journal_raw = self.model.objects.filter(content_type = self.content_type_id_by_name[(Project._meta.app_label, Project._meta.model_name)],
                                                  object_id = project_id
                                                ).select_related('item'
                                                ).select_related('employee'
                                                ).select_related('employee__user'
                                                ).order_by('-work_date', 'employee_id', 'work_time_from')

        log_raw = LogEntry.objects.filter(content_type=ContentType.objects.get_for_model(WorkTimeJournal).pk,
                                          object_id__in=[jr_raw_line.id for jr_raw_line in journal_raw]
                                          ).select_related('user').order_by('id')

        journal_lines = self.get_journal_lines(journal_raw, log_raw) #Adding log information

        journal_totals = self.model.objects.filter(content_type = self.content_type_id_by_name[(Project._meta.app_label, Project._meta.model_name)],
                                                   object_id = project_id).aggregate(Sum('work_time'),
                                                                                 Sum('distance'), 
                                                                                 Sum('toll_ring'), 
                                                                                 Sum('ferry'), 
                                                                                 Sum('diet'))
        context = {
                'mode': mode,
                'pk': int(pk) if pk is not None else None,
                'project': project,
                'customer': project.customer,
                'items': items,
                'form': form,
                'journal_lines': journal_lines,
                'journal_totals': journal_totals,
                }
        return context

    def get_journal_lines(self, jr_raw, log_raw):
        LOG_LINE = 0
        LOG_TITLE = 1

        def get_log_text(line, ltype=LOG_LINE):
            params = {
                'user': line.user.first_name + ' ' + line.user.last_name,
                'time': line.action_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            if line.action_flag == ADDITION:
                if ltype == LOG_LINE:
                    return _('%(time)s created by %(user)s') % params
                elif ltype == LOG_TITLE:
                    return _('This record was added by %(user)s') % params
            elif line.action_flag == CHANGE:
                if ltype == LOG_LINE:
                    return _('%(time)s modified by %(user)s') % params
                elif ltype == LOG_TITLE:
                    return _('This record was modified by administrator') % params

        log_entries = {}
        for log_line in log_raw:
            log_act = log_entries.get(int(log_line.object_id), None)
            if log_act is None or (log_act.get('action', None) == CHANGE and log_line.action_flag == ADDITION):
                log_entries[int(log_line.object_id)] = {
                              'action': log_line.action_flag,
                              'user': log_line.user.first_name + ' ' + log_line.user.last_name,
                              'time': log_line.action_time.strftime("%Y-%m-%d %H:%M:%S"),
                              #'full_history': False,
                              'title': get_log_text(log_line, LOG_TITLE) ,
                              'lines': []
                            }

        for log_line in log_raw:
            lentry = log_entries[int(log_line.object_id)]
            lentry['lines'].append(get_log_text(log_line))
            #lentry['full_history'] = len(lentry['lines']) > 1

        for jr_line in jr_raw:
            log_entry = log_entries.get(jr_line.id, None)
            jr_line.log = log_entry

        return jr_raw


    def get(self, request, project_id=None, pk=None, mode='view'):
        self.setstate(request, pk, mode)
        self.process(request, pk)

        return render(request,
                      self.template,
                      self.get_context(request, project_id, pk, mode)
                      )

    def post(self, request, project_id=None, pk=None, mode=None):
        self.setstate(request, pk, mode)

        '''
        if self.state == RecState.EDIT:
            request.POST = request.POST.copy() #Enabling mutability
            request.POST['employee'] = self.jr_line.employee
        '''

        form = self.form_class(request.POST, instance=self.jr_line, request=request)

        project = Project.objects.get(id=project_id)
        if form.is_valid():
            jr_line = form.save(commit=False)
            jr_line.content_type = ContentType.objects.get_for_model(Project)
            jr_line.content_object = project
            try:
                jr_line.save()
            finally:
                form.save(commit=True) #this only writes a log action, not the record itself
            # Redirect to GET.
            return redirect('pdash-time-review', project_id=project_id)
        else:
            return render(request,
                          self.template,
                          self.get_context(request, project_id, pk, mode, form)
                          )
    
    
    def setstate(self, request, pk, mode):
        state_decoder = {
            'view': RecState.VIEW,
            'edit': RecState.EDIT,
            'delete': RecState.DELETE,
        }
       
        self.state = state_decoder.get(mode)
        
        if self.state in RecState.pk_states and pk:
            try:
                self.jr_line = self.model.objects.get(id=pk)
            except:
                self.jr_line = None
        else:
            self.jr_line = None
    
    def process(self, request, pk):
        jr_line = self.jr_line
        if self.state in RecState.pk_states and not pk:
            raise Exception(_('Record ID not provided.'))

        if self.state == RecState.DELETE:
            if jr_line:
                jr_line.delete()
        
