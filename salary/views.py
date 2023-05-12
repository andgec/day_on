import datetime
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from salary.models import Employee
from shared.const import VIEW, EDIT
from shared.views import StaffRequiredMixin
from general.models import CalendarHeader, CalendarLine, HOLIDAY, ILLNESS, ILLSELF, ABSENCE
from .forms import HolidayLineForm, IllnessLineForm, IllselfLineForm, AbsenceLineForm

class EmployeeView(LoginRequiredMixin, StaffRequiredMixin, View):
    '''
        Employee list for staff management
    '''
    holiday_owner_type = None

    def __init__(self):
        self.holiday_owner_type = ContentType.objects.get_for_model(Employee)
        super().__init__()

    def get_context(self, request, id, a):
        #reading filters from GET parameters: request.GET.get('date-from', self.default_start_date.strftime("%Y-%m-%d")),
        company = request.user.company
        now = datetime.datetime.now()

        employees = Employee.objects.select_related('user').filter(user__is_active=True, company=request.user.company).order_by('user__first_name', 'user__last_name')
        for employee in employees:
            holidays = CalendarLine.objects.select_related('calendar').filter(
                calendar__company = company,
                calendar__owner_type_id = self.holiday_owner_type,
                calendar__owner_id = employee.user_id,
                calendar__type_id = HOLIDAY,
                dtto__gte = now,
                ).order_by('dtfr', 'dtto')[:1]
            employee.holidays = holidays
        return {'employees': employees}

    def get(self, request, id = None, a = VIEW):
        # id = record id, a = action (view, edit, delete)
        if request.user.is_staff == False:
            return None # render "no permission" page
            # EXAMPLE: return render(request, 'no_permission.html' or 404
        return render(request,
                      'staff/v1/staff.html',
                      self.get_context(request, id, a)
                      )
    
    def post(self, request, id, *args, **kwargs):
        if request.user.is_staff == False:
            return None # render "no permission" page


class EmployeeCalendarView(LoginRequiredMixin, StaffRequiredMixin, View):
    '''
        Generic Employee calendar view.
        Used in child view classes for holidays, illnesses, absences, etc.
    '''

    template = 'staff/v1/calendar/empl_cal.html'
    owner_type = None; # Value is set on initialization and transferred to the form to prevent reading it from a database on each read/write
    company = None
    verbose_name = ''
    verbose_name_plural = ''
    verbose_long_name_plural = ''

    def __init__(self):
        self.owner_type = ContentType.objects.get_for_model(Employee)
        if self.verbose_long_name_plural == '':
            self.verbose_long_name_plural = self.verbose_name_plural
        super().__init__()

    def _init_from_request(self, request):
        self.company = request.user.company

    def _get_context(self, request, form, id, employee, a = VIEW):
        #TODO
        #Naujam įrašui nebūtina iš DB traukti ContentTypeId, kas dabar yra daroma. Tik saugant įrašą to reikia. Perdaryti view (ar formą?) taip, kad
        #formos CalendarLine inicializavimo metu nenuskaitytu ContentType.

        records = CalendarLine.objects.select_related('calendar').filter(
            calendar__type = self.cal_type,
            calendar__company = self.company,
            calendar__owner_type_id = self.owner_type,
            calendar__owner_id = employee,
            ).order_by('dtfr', 'dtto')

        employee_inst = Employee.objects.get(user_id=employee)

        meta = {
            'url_alias': self.url_alias,
            'verbose_name': self.verbose_name,
            'verbose_name_plural': self.verbose_name_plural,
            'verbose_long_name_plural': self.verbose_long_name_plural
        }

        return {
            'employee': employee,
            'empl_name': employee_inst.full_name,
            'meta': meta,
            'form': form,
            'records': records,
        }

    def dispatch(self, request, employee=None, *args, **kwargs):
        '''
            Deletion is handled through the post request.
            if POST request variable "_method" has value "delete" then execution is routed to the "delete" method.
        '''
        self._init_from_request(request)
        method = self.request.POST.get('_method', '').lower()
        if method == 'delete':
            return self.delete(request, employee, *args, **kwargs)
        return super().dispatch(request, employee, *args, **kwargs)

    def get(self, request, employee=None, *args, **kwargs):
        form = self.form_class(
            data=None,
            owner=employee,
            company=self.company,
            owner_type=self.owner_type
            )
        return render(request, self.template, self._get_context(request, form, id, employee))

    def post(self, request, employee, id=None, *args, **kwargs):
        rec_id = self.request.POST.get('id', None)
        if rec_id and rec_id != 'null' and rec_id != 'None' and rec_id is not None:
            '''
                Modify record
            '''
            rec_id = int(rec_id)
            rec = CalendarLine.objects.get(id=rec_id)
            form = self.form_class(
                request.POST,
                instance=rec,
                id=id,
                owner=employee,
                company=self.company,
                owner_type=self.owner_type
                )
        else:
            '''
                New record
            '''
            form = self.form_class(
                request.POST,
                id=id,
                owner=employee,
                company=self.company,
                owner_type=self.owner_type
                )
        if form.is_valid():
            instance = form.save(True)
            return redirect(reverse(self.url_alias, args = [employee]))
        return render(request, self.template, self._get_context(request, form, id, employee))

    def delete(self, request, employee, *args, **kwargs):
        ids = self.request.POST.get('_ids', '')
        id_list = [int(id) for id in ids.split(',')]
        CalendarLine.objects.filter(id__in=id_list).delete()
        return redirect(reverse(self.url_alias, args = [employee]))


class HolidayView(EmployeeCalendarView):
    '''
        Employee Holiday list and employee holiday calender record creation/modification
    '''
    form_class = HolidayLineForm
    url_alias = 'empl_holidays'
    cal_type = HOLIDAY
    verbose_name = _('holiday')
    verbose_name_plural = _('holidays')
    verbose_long_name_plural = _('holidays and days off')


class IllnessView(EmployeeCalendarView):
    '''
        Employee Ilness list and employee illness calender record creation/modification
    '''
    form_class = IllnessLineForm
    url_alias = 'empl_illness'
    cal_type = ILLNESS
    verbose_name = _('illness')
    verbose_name_plural = _('illnesses')
    verbose_long_name_plural = _('doctor-declared illnesses')


class IllselfView(EmployeeCalendarView):
    '''
        Employee self-declared illness list and employee holiday calender record creation/modification
    '''
    form_class = IllselfLineForm
    url_alias = 'empl_illself'
    cal_type = ILLSELF
    verbose_name = _('illness')
    verbose_name_plural = _('illnesses')
    verbose_long_name_plural = _('self-notified illnesses')


class AbsenceView(EmployeeCalendarView):
    '''
        Employee Holiday list and employee holiday calender record creation/modification
    '''
    form_class = AbsenceLineForm
    url_alias = 'empl_absence'
    cal_type = ABSENCE
    verbose_name = _('absence')
    verbose_name_plural = _('absences')
