import operator
import datetime
from functools import reduce
from django.db import connection
from django.db.models import Sum
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

from shared.utils import dictfetchall, start_of_current_month, end_of_current_month
from receivables.models import Project, WorkTimeJournal
from djauth.models import User
from conf.settings import TIMELIST_LINES_PER_PAGE


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


@method_decorator(staff_member_required, name='dispatch')
class TimeSummaryXLSXView(View):
    template = get_template('reports/time_summary/time_summary.html')
    
    default_start_date = start_of_current_month()
    default_end_date = end_of_current_month()
    
    def get_context(self, request):
        context = self.get_report_lines(request)
        return context
        
    def run_sql_query(self, **kwargs):
        with connection.cursor() as cursor:
            #try
            cursor.execute(self.sql)
            #except
            result_dict = dictfetchall(cursor)
        return result_dict
    
    def make_report_header(self, **kwargs):
        header = {
            0: {'name': 'employee',
                'type': 'str',
                'caption': _('Employee')
                },
            1: {'name': 'total_hours',
                'type': 'decimal',
                'caption': _('Total hours')
                },
            2: {'name': 'remarks',
                'type': 'str',
                'caption': _('Remarks')
                }
            }
        self.make_day_header(header, **kwargs)
        
        return header

    def make_day_header(self, header, **kwargs):
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        loopdate = date_from
        while loopdate <= date_to:
            header[len(header)] = {'name': loopdate,
                                   'type': 'date',
                                   'caption': str(loopdate)
                                   }
            loopdate = loopdate + datetime.timedelta(days=1)
            
            
    def get_employee_data(self, empl_ids, **kwargs):
        users = User.objects.only('first_name', 'last_name').filter(id__in=empl_ids, is_active = True).order_by('id')
        employee_data = {user.id: user.first_name + ' ' + user.last_name for user in users}
        return employee_data
        
        
    def get_timelist_data(self, **kwargs):
        q_list = []

        q_list.append(Q(work_date__gte=kwargs.get('date_from')))
        q_list.append(Q(work_date__lte=kwargs.get('date_to')))

        project_ids = kwargs.get('project_ids')
        if project_ids:
            contenttype_project = ContentType.objects.get(model='project')
            project_ids_list = project_ids.split(',')
            q_list.append(Q(content_type=contenttype_project))
            q_list.append(Q(object_id__in=project_ids_list))
        
        if kwargs.get('split_by_project') == 'true':
            timelist_data = WorkTimeJournal.objects.filter(
                reduce(operator.and_, q_list)).values(
                    'object_id', 'employee_id', 'work_date').order_by(
                        'object_id', 'employee_id', 'work_date').annotate(
                            work_time = Sum('work_time'))
        else: 
            timelist_data = WorkTimeJournal.objects.filter(
                reduce(operator.and_, q_list)).values(
                    'employee_id', 'work_date').order_by(
                        'employee_id', 'work_date').annotate(
                            work_time = Sum('work_time'))

        return timelist_data
        

    def get_distinct_empl_ids(self, timelist_data):
        #get employee ids from 
        empl_ids = []
        prev_empl_id = 0

        for line in timelist_data:
            if line['employee_id'] != prev_empl_id:
                empl_ids.append(line['employee_id'])
                prev_empl_id = line['employee_id']
                
        empl_ids.append(line['employee_id'])
        print(empl_ids)
        return empl_ids        
        

    def build_employee_time_matrix(self, header_data, employee_data, **kwargs):
        # makes an empty matrix with rows for employees and columns for dates
        time_matrix = {}
        if kwargs.get('split_by_project') == 'true':
            pass
        else:
            for employee_id in employee_data.keys():
                time_matrix_line = {}
                for col in header_data.keys():
                    time_matrix_line[header_data[col]['name']] = ''
                    
                time_matrix[employee_id] = time_matrix_line
                    
        print(time_matrix)
        return time_matrix


    def fill_employee_time_matrix(self, time_matrix, header_data, employee_data, timelist_data, **kwargs):
        for employee_id in employee_data.keys():
            time_matrix[employee_id]['employee'] = employee_data[employee_id]
        
        loop_empl_id = 0
        empl_total_work_time = 0
        
        for line in timelist_data:
            time_matrix[line['employee_id']][line['work_date']] = line['work_time']
            
            if loop_empl_id == 0:
                loop_empl_id = line['employee_id']
                 
            #calculating and adding total hours worked
            if loop_empl_id == line['employee_id']:
                empl_total_work_time += line['work_time']
            else:
                time_matrix[loop_empl_id]['total_hours'] = empl_total_work_time
                empl_total_work_time = 0
                loop_empl_id = line['employee_id']
        
        #adding total hours worked for the last employee
        time_matrix[loop_empl_id]['total_hours'] = empl_total_work_time                
            
        return time_matrix
            
    def get_report_lines(self, request):
        filters = {
            #Addind default values and converting string dates to date data type.
            'date_from': datetime.datetime.strptime(
                request.GET.get('date_from', self.default_start_date.strftime("%Y-%m-%d")),
                "%Y-%m-%d").date(),
            'date_to': datetime.datetime.strptime(
                request.GET.get('date_to', self.default_end_date.strftime("%Y-%m-%d")),
                "%Y-%m-%d").date(),
            'project_ids': request.GET.get('projects'),
            'employee_id': request.GET.get('employee'),
            'split_by_project': request.GET.get('split_by_project'),
        }
        
        header_data = self.make_report_header(**filters)
        #print(header_data)
        timelist_data = self.get_timelist_data(**filters)
        
        distinct_empl_ids = self.get_distinct_empl_ids(timelist_data)
        #print(timelist_data)
        employee_data = self.get_employee_data(distinct_empl_ids, **filters)
        
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

        context = {
            'filters': filters,
            'header': header_data,
            'timelist': time_matrix 
        }
        
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context(request)
        html = self.template.render(context)
        return HttpResponse(html)
    
    
    #def get(self, request, *args, **kwagrs):
    #    return HttpResponse('Atsakymas gautas: ' + str(self.get_context(request)))
        
