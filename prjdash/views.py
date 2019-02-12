from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from receivables.models import Customer, Project
from shared.utils import content_type_id_by_name
from django.db import connection


class ProjectDashboardView(LoginRequiredMixin, View):
    template = 'prjdash/project_dash.html'

    proj_sql = ''' 
        SELECT
          "receivables_customer"."id" as "customer_id",
          "receivables_customer"."name" as "customer_name",
          Proj."project_id", 
          Proj."project_name", 
          Proj."project_description", 
          Proj."project_active",
          Proj."datetime_created"
        FROM "receivables_customer"
        LEFT OUTER JOIN 
            (
            SELECT  
                "receivables_project"."customer_id",
                "receivables_project"."id" as "project_id", 
                "receivables_project"."name" as "project_name",
                "receivables_project"."description" as "project_description", 
                "receivables_project"."active" as "project_active",
                "django_admin_log"."action_time" as "datetime_created"
            FROM "receivables_project"
            JOIN "django_admin_log" ON ("django_admin_log"."object_id" = "receivables_project"."id"::text)
            WHERE "django_admin_log"."content_type_id" = %s
            AND "django_admin_log"."action_flag" = 1
            ) Proj ON (Proj."customer_id" = "receivables_customer"."id")
        WHERE "receivables_customer"."active" = True
        ORDER BY "receivables_customer"."name" ASC,
                 Proj."project_id" ASC
        '''

    def dictfetchall(self, cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
    ]
        
    def build_resul_list(self, result_dicts):
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
                                 'description': line['project_description'],
                                 'active': line['project_active'],
                                 'datetime_created': line['datetime_created'],
                                 })
        # Adding projects for the last custmer
        customers[cust_count-1]['projects'] = projects
            
        return customers


    def get_context(self, request):
        with connection.cursor() as cursor:
            cursor.execute(self.proj_sql, [content_type_id_by_name[(Project._meta.app_label, Project._meta.model_name)]])
            result_dicts = self.dictfetchall(cursor)


        context = {'customers': self.build_resul_list(result_dicts)}
        
        return context;
    
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
    def get(self, request):
        return render(request,
                      self.template,
                      self.get_context(request)
                      )
        
        
    

'''----------------------------------------------
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator


@method_decorator(staff_member_required, name='dispatch')
class ExampleTemplateView(TemplateView):
'''