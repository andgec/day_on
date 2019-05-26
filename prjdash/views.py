from django.shortcuts import render, redirect
from django.db.models import Sum
from django.urls import reverse
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from receivables.models import Project
from shared.utils import get_contenttypes
from django.db import connection
from .forms import PDashProjectForm, PDashAssignEmployees
#from botocore.vendored.requests.api import request
from receivables.models import Project, WorkTimeJournal


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
                "receivables_project"."comment" as "project_comment", 
                "receivables_project"."active" as "project_active",
                "django_admin_log"."action_time" as "datetime_created"
            FROM "receivables_project"
            JOIN "django_admin_log" ON ("django_admin_log"."object_id" = "receivables_project"."id"::text)
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

        #print(context)
        return context

    '''
    def get_context(self, request):
        customers = Customer.objects.filter(active=True).order_by('name')
        customer_list = [c for c in customers]
       
        print(content_type_id_by_name[(Project._meta.app_label, Project._meta.model_name)])
       
        projects = Project.objects.filter(customer__active=True).extra(select = {
            'date_created': 'SELECT dal.action_time ' + 
                            'FROM django_admin_log dal ' + 
                            'WHERE dal.content_type_id = %s '  +
                            'AND dal.object_id = receivables_project.id '
                            }, select_params=(content_type_id_by_name[(Project._meta.app_label, Project._meta.model_name)],)
                        ).order_by('customer__name', 'id')
        print(projects.query)
        
        projects_by_cust_id = {}
        prev_cust_id = None
        for project in projects:
            if project.customer_id != prev_cust_id:
                projects_by_cust_id[project.customer_id] = []
            projects_by_cust_id[project.customer_id].append(project)
            prev_cust_id = project.customer_id
            
        #joining data
        customers = []
        for cust in customer_list:
            if cust.id in projects_by_cust_id:
                customers.append({'object': cust, 'projects': projects_by_cust_id[cust.id]})
            else:
                customers.append({'object': cust, 'projects': []})
        
        context = {
            'customers': customers,
        }
        return context
    '''   
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
            raise Exception('Record ID not provided.')

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

    def get(self, request, pk=None):
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
    #form_class = PDashAssignEmployees
    
    def __init__(self, **kwargs):
        self.content_type_id_by_name = get_contenttypes()
        super(ProjectDashboardPostedTimeReview, self).__init__(**kwargs)

    def get_context(self, request, pk):
        #form = self.form_class();
        form = None
        project = Project.objects.select_related('customer').get(id=pk)
        journal_lines = WorkTimeJournal.objects.filter(content_type = self.content_type_id_by_name[(Project._meta.app_label, Project._meta.model_name)],
                                                       object_id = pk)

        journal_totals = WorkTimeJournal.objects.filter(content_type = self.content_type_id_by_name[(Project._meta.app_label, Project._meta.model_name)],
                                                       object_id = pk).aggregate(Sum('work_time'),
                                                                                 Sum('distance'), 
                                                                                 Sum('toll_ring'), 
                                                                                 Sum('ferry'), 
                                                                                 Sum('diet'))
        context = {
                'project': project,
                'customer': project.customer,
                'form': form,
                'journal_lines': journal_lines,
                'journal_totals': journal_totals,
                }
        print(context)
        return context

    def get(self, request, pk=None):
        return render(request,
                      self.template,
                      self.get_context(request, pk)
                      )
    
