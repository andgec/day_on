from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from salary.models import Employee
from shared.const import VIEW


class EmployeeView(LoginRequiredMixin, View):
    '''
        Employee list for staff management
    '''
    def get_context(self, request, id, a):
        #reading filters from GET parameters: request.GET.get('date-from', self.default_start_date.strftime("%Y-%m-%d")),
        employees = Employee.objects.select_related('user').filter(user__is_active=True, company=request.user.company).order_by('user__first_name', 'user__last_name')
        return {'employees': employees}


    def get(self, request, id = None, a = VIEW):
        # id = record id, a = action (view, edit, delete)
        if request.user.is_staff == False:
            return None # render "no permission" page
            # EXAMPLE: return render(request, 'no_permission.html' or 404
        return render(request,
                      'staff/v1/employees.html',
                      self.get_context(request, id, a)
                      )
    
    def post(self, request, id, *args, **kwargs):
        if request.user.is_staff == False:
            return None # render "no permission" page

