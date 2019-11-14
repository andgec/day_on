import operator
import datetime
from calendar import monthrange
from functools import reduce
from django.db.models import Sum
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import View
from django.template.loader import get_template
from wkhtmltopdf.views import PDFTemplateResponse
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from babel.dates import format_date

from shared.utils import start_of_current_month, end_of_current_month, start_of_month, end_of_month, str2bool, date2str, write_log_message
from receivables.models import Project, WorkTimeJournal
from djauth.models import User
from conf.settings import TIMELIST_LINES_PER_PAGE
from dateutil.relativedelta import relativedelta


#URL:
#http://127.0.0.1:8000/admin/timelist_pdf/?project_ids=1,2,3,4,5,6,7,8,9,10&date_from=2018-10-20&date_to=2019-01-30
@method_decorator(staff_member_required, name='dispatch')
class TimelistPDFView(View):
    template = get_template('reports/pdf_timelist/pdf_timelist_html4.html')
    header_template = get_template('reports/pdf_timelist/pdf_header_html4.html')
    footer_template = get_template('reports/pdf_timelist/pdf_footer_html4_page_number_right.html')

    def get_context(self, request, project_id):
        company = request.user.company;
        project = Project.objects.get(pk=project_id)
        #print(company)
        context = {
            'company': company,
            'project': project,
            }
        context.update(self.get_journal_lines(request, project_id))
        return context
        
    
    def get_journal_lines(self, request, pk):
        project_id = pk
        #project_ids = request.GET.get('project_ids')
        filter_date_from = request.GET.get('date_from')
        filter_date_to = request.GET.get('date_to')
        contenttype_project = ContentType.objects.get(model='project')
        
        # Building the query according URL parameters:
        q_list = []

        '''
        if project_ids:
            project_ids_list = project_ids.split(',')
            q_list.append(Q(content_type=contenttype_project))
            q_list.append(Q(object_id__in=project_ids_list))
        '''
        if project_id:
            q_list.append(Q(content_type=contenttype_project))
            q_list.append(Q(object_id=project_id))
    
        if filter_date_from:
            q_list.append(Q(work_date__gte=filter_date_from))
        if filter_date_to:
            q_list.append(Q(work_date__lte=filter_date_to))
        
        #print(q_list)
        
        journal_lines = WorkTimeJournal.objects.filter(
            reduce(operator.and_, q_list) if len(q_list) > 1 else q_list[0]).order_by('content_type',
                                                                                      'object_id',
                                                                                      '-work_date',
                                                                                      'employee',
                                                                                      'work_time_from')
        
        jr_line_list = []
        pages = []
        line_count = 1
        page_no = 0
        page_date_from = datetime.MINYEAR
        page_date_to   = datetime.MINYEAR
        curr_work_date = datetime.MINYEAR
        prev_work_date = datetime.MINYEAR

        total_work_time     = 0
        total_overtime_50   = 0
        total_overtime_100  = 0
        total_distance      = 0
        total_diet          = 0
        total_transport     = 0

        for journal_line in journal_lines:
            
            jr_line_dict = model_to_dict(journal_line)

            jr_line_list.append(jr_line_dict)
            
            #print('work_date: %s, prev_work_date: %s' % (curr_work_date, prev_work_date))
            curr_work_date = journal_line.work_date
            
            if curr_work_date == prev_work_date:
                work_date_str = ''
            else:
                work_date_str = journal_line.work_date.strftime('%d.%m.%Y')
            
            prev_work_date = curr_work_date                
            
            jr_line_list[line_count-1].update({'work_date': work_date_str,
                                             'work_week_day': format_date(jr_line_dict['work_date'], 'EEE', locale='no').replace('.', '').title(),
                                             'item': journal_line.item.safe_translation_getter('name', language_code='nb'),
                                             'employee': journal_line.employee,
                                             'transport': (journal_line.ferry or 0) + (journal_line.toll_ring or 0),
                                             })


            if page_date_from == datetime.MINYEAR:
                page_date_from = journal_line.work_date

            if ((line_count % TIMELIST_LINES_PER_PAGE == 0) & (line_count > 0) & (line_count < journal_lines.count())) |\
                (len(pages) * TIMELIST_LINES_PER_PAGE + line_count == journal_lines.count()):
                page_no += 1

                page = {
                    'page_no': page_no,
                    'page_date_from': page_date_from,
                    'page_date_to': journal_line.work_date.strftime('%d.%m.%Y'),
                    'lines': jr_line_list,
                }
                
                pages.append(page)
                jr_line_list = []
                line_count = 0
                page_date_from = datetime.MINYEAR
                
            line_count += 1

            total_work_time     += journal_line.work_time
            total_overtime_50   += (journal_line.overtime_50 or 0)
            total_overtime_100  += (journal_line.overtime_100 or 0)
            total_distance      += (journal_line.distance or 0)
            total_diet          += (journal_line.diet or 0)
            total_transport     += (journal_line.ferry or 0) + (journal_line.toll_ring or 0)
            
        totals = {'total_work_time': total_work_time,
                  'total_overtime_50': total_overtime_50,
                  'total_overtime_100': total_overtime_100,
                  'total_distance': total_distance,
                  'total_diet': total_diet,
                  'total_transport': total_transport,
                  }
        
        if len(pages) == 0:
            pages.append({'Empty': 'No data'})
        
        context = {
            'date_from': pages[0]['lines'][0]['work_date'] if journal_lines.count() > 0 else filter_date_from,
            'date_to': journal_line.work_date.strftime('%d.%m.%Y') if journal_lines.count() > 0 else filter_date_to,
            'filter_date_from': filter_date_from,
            'filter_date_to': filter_date_to,
            'total_pages': page_no,
            'totals': totals,
            'pages': pages,
        }
        #print(journal_lines.query)
        return context


    def get(self, request, pk=None):
        context = self.get_context(request, pk)
        #print(context)
        response = PDFTemplateResponse(request = request,
                                       template = self.template,
                                       header_template = self.header_template,
                                       footer_template = self.footer_template,
                                       filename = "Timelist - %s.pdf" % context['project'].name,
                                       context = context,
                                       show_content_in_browser=True,
                                       cmd_options={'javascript-delay': 500,
                                                    'margin-top' : 20,
                                                    'orientation': 'Landscape',},
                                       )
        return response


class TimelistHTMLView(View):
    def get_context(self, request, project_id):
        company = request.user.company;
        print(company)
        context = {
            'company': company,
            }
        context.update(self.get_journal_lines(request, project_id))
        return context


    def get_journal_lines(self, request, project_id):
        #project_ids = request.GET.get('project_ids')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        contenttype_project = ContentType.objects.get(model='project')

        # Building the query according URL parameters:
        q_list = []

        '''
        if project_ids:
            project_ids_list = project_ids.split(',')
            q_list.append(Q(content_type=contenttype_project))
            q_list.append(Q(object_id__in=project_ids_list))
        '''
        if project_id:
            q_list.append(Q(content_type=contenttype_project))
            q_list.append(Q(object_id=project_id))

        if date_from:
            q_list.append(Q(work_date__gte=date_from))
        if date_to:
            q_list.append(Q(work_date__lte=date_to))

        print(q_list)

        journal_lines = WorkTimeJournal.objects.filter(
            reduce(operator.and_, q_list) if len(q_list) > 1 else q_list[0]).order_by('content_type',
                                                                                      'object_id',
                                                                                      '-work_date',
                                                                                      'employee',
                                                                                      'work_time_from').values()
        
        jr_line_list = []
        line_count = 0
        page_no = 0
        page_date_from = None
        page_date_to = None

        for journal_line in journal_lines:
            if (line_count % TIMELIST_LINES_PER_PAGE == 0) & (line_count > 0):
                jr_line_list[line_count-1].update({'page_break': 'LINE_OVERFLOW',
                                                 'page_no': page_no,
                                                 'page_date_from': page_date_from,
                                                 'page_date_to': journal_line['work_date'],
                                                 })
                page_no += 1
                line_count = 0

            jr_line_list.append(journal_line)
            line_count += 1

            if line_count % TIMELIST_LINES_PER_PAGE == 1:
                page_date_from = journal_line['work_date']

        
        context = {
            'line_list': jr_line_list,
            'total_pages': page_no,
            'date_from': jr_line_list[0]['work_date'],
            'date_to': jr_line_list[len(jr_line_list)-1]['work_date'],
            'filter_date_from': date_from,
            'filter_date_to': date_to,
        }
        
        print(journal_lines.query)
        return context
    
    def get(self, request, project_id, *args, **kwargs):
        template = get_template('reports/pdf_timelist_html4.html')
        context = self.get_context(request, project_id)
        html = template.render(context)
        return HttpResponse(html)


class TimeSummaryPostedLineDetailView(View):
    template = 'reports/time_summary/posted_time.html';

    ctp_proj = None

    def get_contenttype_project(self):
        if not self.ctp_proj:
            self.ctp_proj = ContentType.objects.get(model='project')
        return self.ctp_proj

    contenttype_project = property(get_contenttype_project)

    def write_log(self, user, employee, date_from, date_to, project_ids):
        write_log_message(user,
                          str({'employee': employee, 'from': date_from, 'to': date_to, 'projects': project_ids}),
                          self.__class__.__name__)

    def get_context(self, employee, date_from, date_to, project_ids):
        t_lines = WorkTimeJournal.objects.filter(
            employee=employee,
            work_date__gte=date_from,
            work_date__lte=date_to
            ).select_related('employee'
                             ).select_related('employee__user'
                                              ).select_related('item'
                                                               ).prefetch_related('item__translations'
                                                                 ).prefetch_related('content_object'
                                                                   ).prefetch_related('content_object__customer'
                                                                     ).order_by('work_date', 'work_time_from')
        if project_ids:
            t_lines = t_lines.filter(content_type=self.contenttype_project, object_id__in=project_ids.split(','))

        total_time  = 0;
        total_dist  = 0;
        total_toll  = 0;
        total_ferry = 0;
        total_diet  = 0;

        for line in t_lines:
            total_time += 0 if line.work_time is None else line.work_time;
            total_dist += 0 if line.distance is None else line.distance;
            total_toll += 0 if line.toll_ring is None else line.toll_ring;
            total_ferry += 0 if line.ferry is None else line.ferry;
            total_diet += 0 if line.diet is None else line.diet;

        context = {
            'filters': {
                    'date_from_str': date_from,
                    'date_to_str': date_to,
                    'date_from': datetime.datetime.strptime(date_from, "%Y-%m-%d").date(),
                    'date_to': datetime.datetime.strptime(date_to, "%Y-%m-%d").date(),
                    'one_day': date_from == date_to,
                },
            'totals': {
                    'time': None if total_time == 0 else total_time,
                    'distance': None if total_dist == 0 else total_dist,
                    'toll': None if total_toll == 0 else total_toll,
                    'ferry': None if total_ferry == 0 else total_ferry,
                    'diet': None if total_diet == 0 else total_diet,
                },
            'lines': t_lines,
            }

        return context

    def get(self, request, employee, date_from, date_to, project_ids=None):
        self.write_log(request.user, employee, date_from, date_to, project_ids)
        return render(request,
                      self.template,
                      self.get_context(employee, date_from, date_to, request.GET.get('projects')),
                      )


# ======================================================================================================
# Base class for time summary report (data acquisition and preprocessing)
# ======================================================================================================

@method_decorator(staff_member_required, name='dispatch')
class TimeSummaryBaseView(View):
    table_col_count = 0
    ctp_proj = None

    def get_context(self, request):
        context = self.get_report_lines(request)
        return context

    def __get_default_start_date(self):
        return start_of_current_month()

    def __get_default_end_date(self):
        return end_of_current_month()

    def __get_contenttype_project(self):
        if not self.ctp_proj:
            self.ctp_proj = ContentType.objects.get(model='project')
        return self.ctp_proj

    default_start_date = property(__get_default_start_date) 
    default_end_date = property(__get_default_end_date)
    contenttype_project = property(__get_contenttype_project)

    def _get_report_meta(self, **kwargs):
        #Abstract method to acquire eventual metadata for document rendering
        raise NotImplementedError("Method not implemented")

    def make_report_header(self, **kwargs):
        header = [
                {'name': 'employee',
                'type': 'str',
                'caption': _('Employee'),
                'meta': self._get_hdr_employee_meta(),
                },
                {'name': 'total_hours',
                'type': 'decimal',
                'caption': _('Total hours'),
                'meta': self._get_hdr_totalhrs_meta(),
                },
            ]
        self.make_day_header(header, **kwargs)

        return header

    def _get_hdr_employee_meta(self):
        raise NotImplementedError("Method not implemented")

    def _get_hdr_totalhrs_meta(self):
        raise NotImplementedError("Method not implemented")

    def _get_day_header_cell_meta(self, loopdate, date_from, date_to):
        raise NotImplementedError("Method not implemented")

    @staticmethod
    def get_month_col_count(date, date_from, date_to):
        span = monthrange(date.year, date.month)[1]
        if date.year == date_from.year and date.month == date_from.month:
            span = monthrange(date.year, date.month)[1] - date_from.day + 1
        if date.year == date_to.year and date.month == date_to.month:
            span = span - (monthrange(date.year, date.month)[1] - date_to.day) if span else date_to.day
        return span

    def make_day_header(self, header, **kwargs):
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        loopdate = date_from
        month = 0;
        col_count = 0;
        while loopdate <= date_to:
            header.append({'name': loopdate,
                           'type': 'date',
                           'caption': str(loopdate.day),
                           'caption_weekday': _(loopdate.strftime('%a')),
                           'caption_month': _(loopdate.strftime('%B')),
                           'meta': self._get_day_header_cell_meta(loopdate, date_from, date_to)
                          })

            # Calculating total table column count
            if month != loopdate.month:
                month = loopdate.month
                col_count += self.get_month_col_count(loopdate, date_from, date_to)

            loopdate = loopdate + datetime.timedelta(days=1)

        self.table_col_count = col_count + 3


    def get_employee_data(self, empl_ids, **kwargs):
        def filter_employees(empl_dict, empl_ids):
            return {empl_id: empl_dict[empl_id] for empl_id in empl_dict if empl_id in empl_ids}

        # Optimized version returns two employee lists:
        #   - a list for employee filter (full list of active employees);
        #   - a list for report without employees who do not have any hours registered for a given period.
        # This way only one call to the database is needed to retrieve both lists.

        #users = User.objects.only('first_name', 'last_name').filter(id__in=empl_ids, is_active = True).order_by('first_name', 'last_name')
        users = User.objects.only('first_name', 'last_name').filter(is_active = True).order_by('first_name', 'last_name')
        full_employee_data = {user.id: user.first_name + ' ' + user.last_name for user in users}
        employee_data = filter_employees(full_employee_data, empl_ids)
        employee_data[-1] = _('Total') #Adding line for totals
        return employee_data, full_employee_data


    def get_project_data(self):
        projects = Project.objects.only('customer__name', 'name').filter(visible = True).select_related('customer').order_by('customer__name', 'name')
        return projects

    def get_timelist_data(self, **kwargs):
        q_list = []

        q_list.append(Q(work_date__gte=kwargs.get('date_from')))
        q_list.append(Q(work_date__lte=kwargs.get('date_to')))

        employee_ids = kwargs.get('employee_ids')
        if employee_ids:
            q_list.append(Q(employee_id__in=employee_ids.split(',')))

        project_ids = kwargs.get('project_ids')
        if project_ids:
            project_ids_list = project_ids.split(',')
            q_list.append(Q(content_type=self.contenttype_project))
            q_list.append(Q(object_id__in=project_ids_list))

        if kwargs['split_by_project']:
            timelist_data = WorkTimeJournal.objects.filter(
                reduce(operator.and_, q_list)).values(
                    'employee_id', 'object_id', 'work_date').order_by(
                        'employee_id', 'object_id', 'work_date').annotate(
                            work_time = Sum('work_time'))
        else:
            timelist_data = WorkTimeJournal.objects.filter(
                reduce(operator.and_, q_list)).values(
                    'employee_id', 'work_date').order_by(
                        'employee_id', 'work_date').annotate(
                            work_time = Sum('work_time'))

        return timelist_data


    def get_distinct_empl_ids(self, timelist_data):
        # get distinct employee ids from timelist data
        empl_ids = []
        prev_empl_id = 0
        for line in timelist_data:
            if line['employee_id'] != prev_empl_id:
                empl_ids.append(line['employee_id'])
                prev_empl_id = line['employee_id']

        return empl_ids        

    def _get_cell_meta(self, col, even):
        """
        This method is intended to define metadata for different types of data cells
        (f.eks. CSS class for HTML page)
        """
        raise NotImplementedError("Method not implemented")


    def build_employee_time_matrix(self, header_data, employee_data, **kwargs):
        # makes an empty matrix with rows for employees and columns for dates
        time_matrix = {}
        if kwargs['split_by_project']:
            time_matrix = {'result': '-- not yet implemented --'}
        else:
            even = True;
            for employee_id in employee_data.keys():
                time_matrix_line = {}
                even = not even;
                for col in header_data:
                    time_matrix_line[col['name']] = {'data': 0, 'meta': self._get_cell_meta(col['name'], even)}

                time_matrix[employee_id] = time_matrix_line
        return time_matrix

    def fill_employee_time_matrix(self, time_matrix, header_data, employee_data, timelist_data, **kwargs):
        for employee_id in employee_data.keys():
            time_matrix[employee_id]['employee']['data'] = employee_data[employee_id]

        loop_empl_id = 0
        empl_total_work_time = 0

        for line in timelist_data:
            time_matrix[line['employee_id']][line['work_date']]['data'] = line['work_time']
            time_matrix[line['employee_id']][line['work_date']]['meta'] = self._get_day_cell_meta(line, time_matrix[line['employee_id']][line['work_date']]['meta'])

            if loop_empl_id == 0:
                loop_empl_id = line['employee_id']

            #calculating and adding total hours worked
            if loop_empl_id == line['employee_id']:
                empl_total_work_time += line['work_time']
            else:
                time_matrix[loop_empl_id]['total_hours']['data'] = empl_total_work_time
                time_matrix[loop_empl_id]['total_hours']['meta'] = self._get_total_cell_meta(loop_empl_id, time_matrix[loop_empl_id]['total_hours']['meta'], **kwargs)
                empl_total_work_time = line['work_time']
                loop_empl_id = line['employee_id']

            #adding totals
            time_matrix[-1]['total_hours']['data'] += line['work_time'];       #grand total
            time_matrix[-1][line['work_date']]['data'] += line['work_time'];   #day total

        #adding total hours worked for the last employee
        time_matrix[loop_empl_id]['total_hours']['data'] = empl_total_work_time
        time_matrix[loop_empl_id]['total_hours']['meta'] = self._get_total_cell_meta(loop_empl_id, time_matrix[loop_empl_id]['total_hours']['meta'], **kwargs)

        self._set_total_line_meta(time_matrix[-1])

        return time_matrix

    def _get_day_cell_meta(self, line, meta):
        raise NotImplementedError("Method not implemented")

    def _get_total_cell_meta(self, employee_id, meta, **kwargs):
        raise NotImplementedError("Method not implemented")

    def _set_total_line_meta(self, total_line):
        raise NotImplementedError("Method not implemented")

    def get_report_lines(self, request):
        filters = {
            #Adding default values and converting string dates to date data type.
            'date_from': datetime.datetime.strptime(
                request.GET.get('date-from', self.default_start_date.strftime("%Y-%m-%d")),
                "%Y-%m-%d").date(),
            'date_to': datetime.datetime.strptime(
                request.GET.get('date-to', self.default_end_date.strftime("%Y-%m-%d")),
                "%Y-%m-%d").date(),
            'project_ids': request.GET.get('projects'),
            'employee_ids': request.GET.get('employees'),
            'split_by_project': str2bool(request.GET.get('split-by-project')) if request.GET.get('split-by-project') else False,
        }

        time_matrix = None
        header_data = self.make_report_header(**filters)
        timelist_data = self.get_timelist_data(**filters)

        distinct_empl_ids = self.get_distinct_empl_ids(timelist_data)
        employee_data, select_empl_list = self.get_employee_data(distinct_empl_ids, **filters)

        if len(timelist_data) > 0:
            # distinct_empl_ids = self.get_distinct_empl_ids(timelist_data)
            # employee_data, select_empl_list = self.get_employee_data(distinct_empl_ids, **filters)

            time_matrix = self.build_employee_time_matrix(
                header_data,
                employee_data,
                **filters)

            time_matrix = self.fill_employee_time_matrix(
                time_matrix,
                header_data,
                employee_data,
                timelist_data,
                **filters)

        meta = self._get_report_meta(**filters)

        context = {
            'filters': filters,
            'meta': meta,
            'header': header_data,
            'timelist': time_matrix,
            'employees': select_empl_list,
            'projects': self.get_project_data(),
            'message': _('No timelist entries for given period.') if time_matrix is None else ''
        }

        self.write_log(request.user, filters)

        return context

    def write_log(self, user, filters):
        write_log_message(user,
                          str(filters),
                          self.__class__.__name__)

    def _render_doc(self, request):
        '''
        This method is intended to render the document in required format (HTML, PDF, XLSX, etc)
        '''
        raise NotImplementedError("Method not implemented")

    def get(self, request):
        return self._render_doc(request)


# ------ Time Summary report for HTML representation ------

class TimeSummaryHTMLView(TimeSummaryBaseView):
    template = 'reports/time_summary/time_summary.html'
    meta = {
            'css_cell_empty'        : 'cellEmpty',          #css class for empty cell (without any data)
            'css_cell_click'        : 'cellClick',          #css class for clickable cell (with working hours data)
            'css_cell_day'          : 'cellDay',            #css class for any day cell
            'css_cell_workday_odd'  : 'cellWrkDay-odd',     #css class for workday cell (odd line)
            'css_cell_workday_even' : 'cellWrkDay-even',    #css class for workday cell (even line)
            'css_cell_wknd_odd'     : 'cellWknd-odd',       #css class for weekend cell (odd line)
            'css_cell_wknd_even'    : 'cellWknd-even',      #css class for weekend cell (even line)
            'css_cell_totalhrs'     : 'cellTotalHrs',       #css class for total hours cell
            'css_cell_totalhrs_odd' : 'cellWrkDay-odd',     #css class for total-hours cell (odd line)
            'css_cell_totalhrs_even': 'cellWrkDay-even',    #css class for total-hours cell (even line)
            'css_cell_employee'     : 'cellEmployee',       #css class for employee cell
            'css_cell_employee_odd' : 'cellWrkDay-odd',     #css class for employee cell (odd line)
            'css_cell_employee_even': 'cellWrkDay-even',    #css class for employee cell (odd line)
            'css_cell_day_hdr'      : 'colDayHdr',          #css class for day column header
            'css_cell_totalhrs_hdr' : 'colTotalHoursHdr',   #css class for total-hours column header
            'css_cell_employee_hdr' : 'colEmployeeHdr',     #css class for employee column header
            'css_cell_day_footer'   : 'colDayFooter',       #css class for day and total column footer
            'css_cell_empl_footer'  : 'colEmplFooter',      #css class for employee column footer
            'js_on_click_data_cell' : 'onClick=showTLines(\'%(empl)s\',\'%(date_from)s\',\'%(date_to)s\')',
            'js_on_cell_click_func' : '<script> function showTLines(emplId, dFrom, dTo){window.location.href="%(urlbase)s" + "/" + emplId + "/" + dFrom + "/" + dTo%(projects)s} </script>',
        }

    def _render_doc(self, request):
        context = self.get_context(request)
        return render(request,
                      self.template,
                      context
                      )

    def _get_report_meta(self, **kwargs):
        def get_month_meta(date):
            return {
                'num': date.strftime("%m"),
                'name': _(date.strftime('%B')),
                'start': date2str(start_of_month(date)),
                'end': date2str(end_of_month(date)),
            }

        def get_js():
            return self.meta['js_on_cell_click_func'] % {
                'urlbase': reverse('report-time-summary-details'),
                'projects': ' + "?projects=' + kwargs.get('project_ids', '') + '"' if kwargs.get('project_ids') else '',
            }

        meta = {
            'date_filter_ctrls': {
                'this_month': get_month_meta(self.default_start_date),
                'prev_month': get_month_meta(self.default_start_date + relativedelta(months=-1)),
                'pprev_month': get_month_meta(self.default_start_date + relativedelta(months=-2)),
                'str_from': date2str(kwargs['date_from']),
                'str_to': date2str(kwargs['date_to']),
            },
            'js': {
                'cell_click': get_js(),
            },
            'table_header': {
                'whitebar_col_span': self.table_col_count,
            }
        }
        return meta

    def __get_css_class_for_data_cell(self, col, even):
        try:
            cssClass = self.meta['css_cell_day'] + ' '
            if col.isoweekday() in (6,7):
                if even:
                    cssClass += self.meta['css_cell_wknd_even']
                else:
                    cssClass += self.meta['css_cell_wknd_odd']
            else:
                if even:
                    cssClass += self.meta['css_cell_workday_even']
                else:
                    cssClass += self.meta['css_cell_workday_odd']
        except:
            if col == 'total_hours':
                cssClass = self.meta['css_cell_totalhrs'] + ' '
                if even:
                    cssClass += self.meta['css_cell_totalhrs_even']
                else:
                    cssClass += self.meta['css_cell_totalhrs_odd']
            elif col == 'employee':
                cssClass = self.meta['css_cell_employee'] + ' '
                if even:
                    cssClass += self.meta['css_cell_employee_even']
                else:
                    cssClass += self.meta['css_cell_employee_odd']
            else:
                cssClass = ''

        return cssClass


    def _get_hdr_employee_meta(self):
        return {'cssClass': self.meta['css_cell_employee_hdr'],}

    def _get_hdr_totalhrs_meta(self):
        return {'cssClass': self.meta['css_cell_totalhrs_hdr'],}

    def _get_day_header_cell_meta(self, loopdate, date_from, date_to):
        return {
            'month_col_span': self.get_month_col_count(loopdate, date_from, date_to), #calculating colspan for month header
            'cssClass': self.meta['css_cell_day_hdr'],
        }

    def _get_cell_meta(self, col, even):
        return {'cssClass': self.__get_css_class_for_data_cell(col, even)}

    def _get_day_cell_meta(self, line, meta):
        meta['onClick'] = self.meta['js_on_click_data_cell'] % {
                    'empl': str(line['employee_id']),
                    'date_from': line['work_date'].strftime("%Y-%m-%d"),
                    'date_to': line['work_date'].strftime("%Y-%m-%d"),
                    }

        if meta.get('cssClass'):
            meta['cssClass'] += ' ' + self.meta['css_cell_click'] if meta['cssClass'] != '' else self.meta['css_cell_click']
        else:
            meta['cssClass'] = self.meta['css_cell_click']

        return meta


    def _get_total_cell_meta(self, employee_id, meta, **kwargs):
        meta['onClick'] = self.meta['js_on_click_data_cell'] % {
                    'empl': employee_id,
                    'date_from': kwargs['date_from'].strftime("%Y-%m-%d"),
                    'date_to': kwargs['date_to'].strftime("%Y-%m-%d"),
                    }
        if meta.get('cssClass'):
            meta['cssClass'] += ' ' + self.meta['css_cell_click'] if meta['cssClass'] != '' else self.meta['css_cell_click']
        else:
            meta['cssClass'] = self.meta['css_cell_click']

        return meta

    def _set_total_line_meta(self, total_line):
        for col_name, col in total_line.items():
            if col_name != 'employee':
                col['meta']['cssClass'] += ' ' + self.meta['css_cell_day_footer']
            else:
                col['meta']['cssClass'] += ' ' + self.meta['css_cell_empl_footer']
