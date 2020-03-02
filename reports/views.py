#import io
import operator
import datetime
import copy
import xlsxwriter
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

from shared.utils import uniq4list, start_of_current_month, end_of_current_month, start_of_month, end_of_month, str2bool, date2str, write_log_message
from receivables.models import Project, WorkTimeJournal
from djauth.models import User
from conf.settings import TIMELIST_LINES_PER_PAGE
from dateutil.relativedelta import relativedelta


@method_decorator(staff_member_required, name='dispatch')
class TimelistPDFView(View):
    template = get_template('reports/pdf_timelist/pdf_timelist_html4.html')
    header_template = get_template('reports/pdf_timelist/pdf_header_html4.html')
    footer_template = get_template('reports/pdf_timelist/pdf_footer_html4_page_number_right.html')

    def get_context(self, request, project_id):
        company = request.user.company;
        project = Project.objects.get(pk=project_id)
        context = {
            'company': company,
            'project': project,
            'dynamic_logo':  str2bool(str(request.GET.get('dynamic-logo', False))) or company.fax_no == '0123456789' # TEMPORARY for testing if logo from company works
            }
        context.update(self.get_journal_lines(request, project_id))
        return context


    def get_journal_lines(self, request, pk):
        project_id = pk
        #project_ids = request.GET.get('project_ids')
        item_ids = request.GET.get('item-ids')
        filter_date_from = request.GET.get('date-from')
        filter_date_to = request.GET.get('date-to')
        contenttype_project = ContentType.objects.get(model='project')

        # Building the query according URL parameters:
        q_list = [Q(company = request.user.company)]

        '''
        if project_ids:
            project_ids_list = project_ids.split(',')
            q_list.append(Q(content_type=contenttype_project))
            q_list.append(Q(object_id__in=project_ids_list))
        '''
        if item_ids:
            item_ids_list = item_ids.split(',')
            q_list.append(Q(item_id__in=item_ids_list))

        if project_id:
            q_list.append(Q(content_type=contenttype_project))
            q_list.append(Q(object_id=project_id))

        if filter_date_from:
            q_list.append(Q(work_date__gte=filter_date_from))
        if filter_date_to:
            q_list.append(Q(work_date__lte=filter_date_to))

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
        return context

    def get(self, request, pk=None):
        context = self.get_context(request, pk)
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

    def get_context(self, request, employee, date_from, date_to, project_ids):
        t_lines = WorkTimeJournal.objects.filter(
            company = request.user.company,
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
            'title': _('Time summary'),
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
                      self.get_context(request, employee, date_from, date_to, request.GET.get('projects')),
                      )


# ======================================================================================================
# Base class for time summary report (data acquisition and preprocessing)
# ======================================================================================================

@method_decorator(staff_member_required, name='dispatch')
class TimeSummaryBaseView(View):
    table_col_count = 3
    ctp_proj = None

    def _get_context(self, request):
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

    def __get_report_col_count(self, **kwargs):
        col_count = 2
        col_count += ((kwargs['date_to']-kwargs['date_from']).days + 1 if kwargs['split_by_dates'] else 0)
        col_count += (1 if kwargs.get('split_by_project') else 0)
        return col_count

    def make_report_header(self, **kwargs):
        col_count = self.__get_report_col_count(**kwargs)

        header = [
                {'name': 'employee',
                'type': 'str',
                'caption': _('Employee'),
                'meta': self._get_hdr_employee_meta(col_count),
                },
            ]
        if kwargs.get('split_by_project', None):
            self.table_col_count += 1
            header.append(
                    {'name': 'project',
                    'type': 'str',
                    'caption': _('Project'),
                    'meta': self._get_hdr_project_meta(col_count),
                    },
                )
            if kwargs.get('show_proj_cat', None):
                self.table_col_count += 1
                header.append(
                    {'name': 'projcat',
                    'type': 'str',
                    'caption': _('Project category'),
                    'meta': self._get_hdr_projcat_meta(col_count),
                    }
                )
        header.append(
                {'name': 'total_hours',
                'type': 'decimal',
                'caption': _('Total hours'),
                'meta': self._get_hdr_totalhrs_meta(col_count, last_col = not kwargs.get('split_by_dates', True)),
                },
            )
        self.make_day_header(header, **kwargs)
        return header

    def _get_hdr_employee_meta(self, col_count):
        raise NotImplementedError("Method not implemented")

    def _get_hdr_project_meta(self, col_count):
        raise NotImplementedError("Method not implemented")

    def _get_hdr_projcat_meta(self, col_count):
        raise NotImplementedError("Method not implemented")

    def _get_hdr_totalhrs_meta(self, col_count, last_col = False):
        raise NotImplementedError("Method not implemented")

    def _get_day_header_cell_meta(self, loopdate, date_from, date_to, last_col = False):
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
        if not kwargs.get('split_by_dates', True):
            return
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        loopdate = date_from
        month = 0;
        day_col_count = 0;
        while loopdate <= date_to:
            header.append({'name': loopdate,
                           'type': 'date',
                           'caption': str(loopdate.day),
                           'caption_weekday': _(loopdate.strftime('%a')),
                           'caption_month': _(loopdate.strftime('%B')),
                           'meta': self._get_day_header_cell_meta(loopdate, date_from, date_to, last_col = loopdate == date_to)
                          })

            # Calculating total table column count
            if month != loopdate.month:
                month = loopdate.month
                day_col_count += self.get_month_col_count(loopdate, date_from, date_to)

            loopdate = loopdate + datetime.timedelta(days=1)
        self.table_col_count += day_col_count


    def get_employee_data(self, empl_ids, **kwargs):
        def filter_employees(empl_dict, empl_ids):
            return {empl_id: empl_dict[empl_id] for empl_id in empl_dict if empl_id in empl_ids}

        # Optimized version returns two employee lists:
        #   - a list for employee filter (full list of active employees);
        #   - a list for report without employees who do not have any hours registered for a given period.
        # This way only one call to the database is needed to retrieve both lists.

        users = User.objects.only('first_name', 'last_name'
                                  ).filter(Q(company=kwargs['company'])
                                  ).filter(Q(is_active = True) | Q(id__in = empl_ids)
                                  ).order_by('first_name', 'last_name', 'username')
        full_employee_data = {user.id: user.name_or_username() for user in users}
        employee_data = filter_employees(full_employee_data, empl_ids)
        #employee_data[-1] = _('Total') #Adding line for totals
        return employee_data, full_employee_data


    def get_project_data(self, timelist_data, **kwargs):
        # Returns two datasets:
        #    - a dictionary with project list in which employee worked in given time period;
        #    - a queryset with all visible projects + invisible projects in which any employee worked in given time period.
        # Must show projects which are hidden (visible=False) but included in the report.
        proj_ids = uniq4list([timelist_line['object_id'] for timelist_line in timelist_data])
        full_project_data = Project.objects.only('customer__name', 'name', 'category__name'
                                ).filter(Q(company = kwargs['company'])
                                ).filter(Q(visible = True) | Q(id__in=proj_ids)
                                ).select_related('customer'
                                ).select_related('category'
                                ).order_by('customer__name', 'name')
        project_data = {}

        if kwargs.get('split_by_project', False):
            full_project_dict = {project.id: {'name': project.name + ' (' + project.description + ')' if project.description else project.name,
                                              'cat_name': project.category.name if project.category else '',
                                              } for project in full_project_data
                                }

            for line in timelist_data:
                if project_data.get(line['employee_id']):
                    if line['object_id'] not in project_data[line['employee_id']]:
                        project_data[line['employee_id']][line['object_id']] = full_project_dict[line['object_id']]
                else:
                    project_data[line['employee_id']] = {line['object_id']: full_project_dict[line['object_id']]}

        return project_data, full_project_data


    def get_timelist_data(self, **kwargs):
        q_list = [Q(company=kwargs['company'])]

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

        timelist_data = WorkTimeJournal.objects.filter(
            reduce(operator.and_, q_list)).values(
                'employee_id', 'object_id', 'work_date').order_by(
                    'employee_id', 'object_id', 'work_date').annotate(
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

    def _get_cell_meta(self, col, even, col_count, new_section = False, last_col = False):
        """
        This method is intended to define metadata for different types of data cells
        (f.eks. CSS class for HTML page)
        """
        raise NotImplementedError("Method not implemented")


    def build_employee_time_matrix(self, header_data, employee_data, project_data, **kwargs):
        # makes an empty matrix with rows for employees (and projects if requested) and columns for dates (if requested)
        time_matrix = {}
        even = True;
        prev_empl_id = 0
        col_count = self.__get_report_col_count(**kwargs)
        if kwargs.get('split_by_project', False):
            for employee_id in employee_data.keys():
                for project_id in project_data[employee_id]:
                    col_num = 0
                    is_next_empl = prev_empl_id != employee_id
                    time_matrix_line = {}
                    even = not even;
                    for col in header_data:
                        col_num += 1
                        is_last_col = col_num == len(header_data)
                        time_matrix_line[col['name']] = {'data': is_next_empl if col['name'] == 'employee' else 0,
                                                         'meta': self._get_cell_meta(col['name'], even, col_count, is_next_empl, is_last_col)
                                                        }
                    time_matrix[(employee_id,project_id)] = time_matrix_line

                    if is_next_empl:
                        prev_empl_id = employee_id
        else:
            for employee_id in employee_data.keys():
                time_matrix_line = {}
                col_num = 0
                even = not even;
                for col in header_data:
                    col_num += 1
                    is_last_col = col_num == len(header_data)
                    time_matrix_line[col['name']] = {'data': 0,
                                                     'meta': self._get_cell_meta(col['name'], even, col_count, last_col = is_last_col),
                                                    }

                time_matrix[(employee_id,0)] = time_matrix_line

        # Adding a line for totals:
        time_matrix_line = copy.deepcopy(time_matrix_line)  # Copying last line
        time_matrix_line['employee']['data'] = _('Total')   # Changing name to be "Totals"
        col_num = 0
        for col in time_matrix_line:
            col_num += 1
            is_last_col = col_num == len(header_data)
            time_matrix_line[col]['meta'] = self._get_cell_meta(col, not even, col_count, True, is_last_col) # Writing correct metadata

        time_matrix[(-1,-1)] = time_matrix_line

        return time_matrix

    def fill_employee_time_matrix(self, time_matrix, header_data, employee_data, project_data, timelist_data, **kwargs):
        if kwargs.get('split_by_project', False):
            for employee_id in employee_data.keys():
                for project_id, project_textdata in project_data[employee_id].items():
                    if time_matrix[(employee_id, project_id)]['employee']['data']:
                        time_matrix[(employee_id, project_id)]['employee']['data'] = employee_data[employee_id]
                    time_matrix[(employee_id, project_id)]['project']['data'] = project_textdata['name']
                    time_matrix[(employee_id, project_id)]['projcat']['data'] = project_textdata['cat_name']
        else:
            for employee_id in employee_data.keys():
                time_matrix[(employee_id, 0)]['employee']['data'] = employee_data[employee_id]

        loop_id = (0,0)
        line_total_work_time = 0

        for line in timelist_data:
            eid = line['employee_id']
            pid = line['object_id'] if kwargs.get('split_by_project', None) else 0

            if kwargs.get('split_by_dates', True):
                time_matrix[(eid, pid)][line['work_date']]['data'] += line['work_time']
                time_matrix[(eid, pid)][line['work_date']]['meta'] = self._get_day_cell_meta(line, (eid, pid), time_matrix[(eid, pid)][line['work_date']]['meta'])

            if loop_id == (0,0):
                loop_id = (eid, pid)

            #calculating and adding total hours worked
            if loop_id == (eid, pid):
                line_total_work_time += line['work_time']
            else:
                time_matrix[loop_id]['total_hours']['data'] = line_total_work_time
                time_matrix[loop_id]['total_hours']['meta'] = self._get_total_cell_meta(loop_id, time_matrix[loop_id]['total_hours']['meta'], **kwargs)
                line_total_work_time = line['work_time']
                loop_id = (eid, pid)

            #adding totals
            time_matrix[(-1,-1)]['total_hours']['data'] += line['work_time'];           #grand total
            if kwargs.get('split_by_dates', True):
                time_matrix[(-1,-1)][line['work_date']]['data'] += line['work_time'];   #day total

        #adding total hours worked for the last employee
        time_matrix[loop_id]['total_hours']['data'] = line_total_work_time
        time_matrix[loop_id]['total_hours']['meta'] = self._get_total_cell_meta(loop_id, time_matrix[loop_id]['total_hours']['meta'], **kwargs)

        self._set_total_line_meta(time_matrix[(-1,-1)])

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
            'split_by_dates': str2bool(request.GET.get('split-by-dates')) if request.GET.get('split-by-dates') else True,
            'show_proj_cat': str2bool(request.GET.get('show-proj-cat')) if request.GET.get('show-proj-cat') else True,
            'company': request.user.company,
        }

        time_matrix = None
        header_data = self.make_report_header(**filters)
        timelist_data = self.get_timelist_data(**filters)

        distinct_empl_ids = self.get_distinct_empl_ids(timelist_data)
        employee_data, select_empl_list = self.get_employee_data(distinct_empl_ids, **filters)
        project_data, select_proj_list = self.get_project_data(timelist_data, **filters)

        if len(timelist_data) > 0:
            # distinct_empl_ids = self.get_distinct_empl_ids(timelist_data)
            # employee_data, select_empl_list = self.get_employee_data(distinct_empl_ids, **filters)

            time_matrix = self.build_employee_time_matrix(
                header_data,
                employee_data,
                project_data,
                **filters)

            time_matrix = self.fill_employee_time_matrix(
                time_matrix,
                header_data,
                employee_data,
                project_data,
                timelist_data,
                **filters)

        meta = self._get_report_meta(**filters)

        context = {
            'title': _('Time summary'),
            'filters': filters,
            'meta': meta,
            'header': header_data,
            'timelist': time_matrix,
            'employees': select_empl_list,
            'projects': select_proj_list,
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
            'css_cell_projcat'      : 'cellProjCat',        #css class for project category cell
            'css_cell_projcat_odd'  : 'cellWrkDay-odd',     #css class for project category cell (odd line)
            'css_cell_projcat_even' : 'cellWrkDay-even',    #css class for project category cell (even line)
            'css_cell_totalhrs'     : 'cellTotalHrs',       #css class for total hours cell
            'css_cell_totalhrs_odd' : 'cellWrkDay-odd',     #css class for total-hours cell (odd line)
            'css_cell_totalhrs_even': 'cellWrkDay-even',    #css class for total-hours cell (even line)
            'css_cell_employee'     : 'cellEmployee',       #css class for employee cell
            'css_cell_employee_odd' : 'cellWrkDay-odd',     #css class for employee cell (odd line)
            'css_cell_employee_even': 'cellWrkDay-even',    #css class for employee cell (odd line)
            'css_cell_project'      : 'cellProject',        #css class for project cell
            'css_cell_project_wide' : 'cellProjectWide',    #css class for project cell (wide)
            'css_cell_day_hdr'      : 'colDayHdr',          #css class for day column header
            'css_cell_employee_hdr' : 'colEmployeeHdr',     #css class for employee column header
            'css_cell_project_hdr'  : 'colProjectHdr',      #css class for project column header
            'css_cell_projcat_hdr'  : 'colProjCatHdr',      #css class for project category column header
            'css_cell_totalhrs_hdr' : 'colTotalHoursHdr',   #css class for total-hours column header
            'css_cell_day_footer'   : 'colDayFooter',       #css class for day and total column footer
            'css_cell_empl_footer'  : 'colEmplFooter',      #css class for employee column footer
            'css_cell_section_divider': 'cellSectionDivider', #css class for visual division of the report into sections
            'js_on_click_data_cell' : 'onClick=showTLines(\'%(empl)s\',\'%(proj)s\',\'%(date_from)s\',\'%(date_to)s\')',
            'js_on_cell_click_func' : '''<script>
                                            function showTLines(emplId, projId, dFrom, dTo){
                                                if (projId == 0) {
                                                    window.location.href="%(urlbase)s" + "/" + emplId + "/" + dFrom + "/" + dTo%(projects)s
                                                }
                                                else {
                                                    window.location.href="%(urlbase)s" + "/" + emplId + "/" + dFrom + "/" + dTo + "?projects=" + projId
                                                }
                                            }
                                        </script>''',
        }

    def _render_doc(self, request):
        context = self._get_context(request)
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

    def __get_css_class_for_data_cell(self, col, even, col_count, new_section):
        def get_css_for_section_divider(new_section):
            return ' ' + self.meta['css_cell_section_divider'] + ' ' if new_section else ' '
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
            elif col == 'projcat':
                cssClass = self.meta['css_cell_projcat'] + ' '
                if even:
                    cssClass += self.meta['css_cell_projcat_even']
                else:
                    cssClass += self.meta['css_cell_projcat_odd']
            elif col == 'project':
                cssClass = self.meta['css_cell_project'] + ' ' if col_count > 20 else self.meta['css_cell_project_wide'] + ' '
            else:
                cssClass = ''
        return cssClass + get_css_for_section_divider(new_section)

    def _get_hdr_employee_meta(self, col_count):
        return {'cssClass': self.meta['css_cell_employee_hdr'],}

    def _get_hdr_project_meta(self, col_count):
        return {'cssClass': self.meta['css_cell_project_hdr'],}

    def _get_hdr_projcat_meta(self, col_count):
        return {'cssClass': self.meta['css_cell_projcat_hdr'],}

    def _get_hdr_totalhrs_meta(self, col_count, last_col = False):
        return {'cssClass': self.meta['css_cell_totalhrs_hdr'],}

    def _get_day_header_cell_meta(self, loopdate, date_from, date_to, last_col = False):
        return {
            'month_col_span': self.get_month_col_count(loopdate, date_from, date_to), #calculating colspan for month header
            'cssClass': self.meta['css_cell_day_hdr'],
        }

    def _get_cell_meta(self, col, even, col_count, new_section = False, last_col = False):
        return {'cssClass': self.__get_css_class_for_data_cell(col, even, col_count, new_section)}

    def _get_day_cell_meta(self, line, line_id, meta):
        meta['onClick'] = self.meta['js_on_click_data_cell'] % {
                    'empl': line_id[0],
                    'proj': line_id[1],
                    'date_from': line['work_date'].strftime("%Y-%m-%d"),
                    'date_to': line['work_date'].strftime("%Y-%m-%d"),
                    }

        if meta.get('cssClass'):
            meta['cssClass'] += ' ' + self.meta['css_cell_click'] if meta['cssClass'] != '' else self.meta['css_cell_click']
        else:
            meta['cssClass'] = self.meta['css_cell_click']

        return meta


    def _get_total_cell_meta(self, line_id, meta, **kwargs):
        meta['onClick'] = self.meta['js_on_click_data_cell'] % {
                    'empl': line_id[0],
                    'proj': line_id[1],
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



# ------ Time Summary report for XLSX representation ------
class TimeSummaryXLSXView(TimeSummaryBaseView):
    meta = {
        'start_row': 1,
        'start_col': 1,
    }

    xlsx_style_dict = {
        'bold'              : {'type'   : 'bool',
                               'value'  : {'bold': 1},
                               },
        'dtype'             : {'type'   : 'enum',
                               'decimal': {'num_format': '#,##0.00_)'},
                               },
        'section-divider'   : {'type'   : 'bool',
                               'value'  : {'top': 2, 'top_color': '#B0B0B0'},
                               },
        'align'             : {'type'   : 'enum',
                               'left'   : {'align': 'left'},
                               'right'  : {'align': 'right'},
                               'center' : {'align': 'center'},
                               },
        'valign'            : {'type'   : 'enum',
                               'top'    : {'valign': 'top'},
                               'bottom' : {'valign': 'bottom'},
                               'middle' : {'valign': 'vcenter'},
                               'wrap'   : {'valign': 'vjustify'},
                               },
        'bgcolor'           : {'type'       : 'enum',
                               'hdr-wknd'   : {'bg_color': '#79AEC8'},
                               'hdr'        : {'bg_color': '#DDDDDD'},
                               'odd'        : {'bg_color': '#FFFFFF'},
                               'even'       : {'bg_color': '#f2f2f2'},
                               'wknd-odd'   : {'bg_color': '#E7EFF2'},
                               'wknd-even'  : {'bg_color': '#CFDFE6'},
                               'white'      : {'bg_color': '#FFFFFF'},
                               },
        'font'              : {'type'       : 'enum',
                               'default'    : {'font_color': '#333333',
                                               'font_size': 10,
                                               },
                                'monthday'  : {'font_color': '#333333',
                                               'font_size': 12,
                                               'bold': True
                                               },
                                'weekday'   : {'font_color': '#777777',
                                               'font_size': 9,
                                               'bold': True
                                               },
                               },
        'border'            : {'type'       : 'enum',
                               'odd'        : {'right': 1, 'bottom': 1, 'right_color': '#DDDDDD', 'bottom_color': '#EEEEEE'},
                               'even'       : {'right': 1, 'bottom': 1, 'right_color': '#CCCCCC', 'bottom_color': '#EEEEEE'},
                               'wknd-odd'   : {'right': 1, 'bottom': 1, 'right_color': '#CCCCCC', 'bottom_color': '#c6d9e2'},
                               'wknd-even'  : {'right': 1, 'bottom': 1, 'right_color': '#AAAAAA', 'bottom_color': '#c6d9e2'},
                               'hdr-inner'  : {'right': 1, 'right_color': '#AAAAAA'},
                               'wknd-hdr-inner': {'right': 1, 'right_color': '#777777'},
                               },
        'table-border'      : {'type'       : 'enum',
                               'left'       : {'left': 2, 'left_color': '#B0B0B0'},
                               'right'      : {'right': 2, 'right_color': '#B0B0B0'},
                               'top'        : {'top': 2, 'top_color': '#B0B0B0'},
                               'bottom'     : {'bottom': 2, 'bottom_color': '#B0B0B0'},
                               },
        'month-hdr'         : {'type'   : 'bool',
                               'value'  : {'bold': True,
                                           'align': 'center',
                                           'valign': 'vcenter',
                                           'left': 8,
                                           'top': 8,
                                           'right': 8,
                                           'left_color':'#B0B0B0',
                                           'top_color':'#B0B0B0',
                                           'right_color':'#B0B0B0',
                                           'font_color': '#B0B0B0',
                                           'font_size': 14,
                                           }
                               },
        'width'             : {'type'   : 'pseudo'}, # applied to a column
        'height'            : {'type'   : 'pseudo'}, # applied to a row
        'upper'             : {'type'   : 'pseudo'}, # applied directly to a string before writing it to XLSX
        'indent'            : {'type'   : 'pseudo'}, # applied to a string before writing
        'wrap'              : {'type'   : 'pseudo'}, # applied to a string before writing
        }

    def get_file_name(self):
        return 'time_summary_test.xlsx'

    def _render_doc(self, request):
        context = self._get_context(request)
        return self.__get_xlsx(request, context)

    def __get_xlsx_format_props(self, dcell):
        xlsx_format = {}
        for fkey, fvalue in dcell['meta'].items():
            style_item = self.xlsx_style_dict.get(fkey, None)
            if style_item:
                if style_item['type'] == 'pseudo': # pseudo properties are not applied to a cell
                    pass
                elif style_item['type'] == 'bool':
                    if fvalue and style_item['value']:
                        xlsx_format.update(style_item['value'])
                elif style_item['type'] == 'enum':
                    if isinstance(fvalue, tuple):
                        for fval in fvalue:
                            if style_item.get(fval):
                                xlsx_format.update(style_item[fval])
                    else:
                        if style_item.get(fvalue):
                            xlsx_format.update(style_item[fvalue])
        return xlsx_format

    def __apply_indent_and_wrap(self, text, indentation, wrap, align = 'left'):
        res_text = ''
        indent = ' ' * indentation if indentation else ''
        if wrap:
            words = text.split()
            word_num = 0
            if align in ('left', 'center', None):
                for word in words:
                    last = word_num == len(words) - 1
                    res_text += indent + word + ('\n' if not last else '')
                    word_num += 1

            elif align == 'right':
                for word in words:
                    last = word_num == len(words) - 1
                    res_text += word + indent + ('\n' if not last else '')
                    word_num += 1
        else:
            if align in ('left', 'center', None):
                res_text = indent + text
            elif align == 'right':
                res_text = text + indent

        return res_text

    def __get_xlsx(self, request, context):
        # get xlsx format object by dictionary cell metadata
        def get_xlsx_format(workbook, format_dict, dcell):
            xlsx_format_props = self.__get_xlsx_format_props(dcell);
            #print(xlsx_format_props)
            xlsx_format = format_dict.get(str(xlsx_format_props), None)
            if not xlsx_format:
                xlsx_format = workbook.add_format(xlsx_format_props)
                format_dict[str(xlsx_format_props)] = xlsx_format
            return xlsx_format

        def row_write_style(worksheet, row, col_count, cell_format):
            for col in range(col_count):
                worksheet.write_blank(row, col, None, cell_format)

        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=time_summary.xlsx"

        book = xlsxwriter.Workbook(response, {'in_memory': True})
        sheet = book.add_worksheet(str(_('Time summary')))

        # Return "report empty" message if no content
        if not context['timelist']:
            sheet.set_row(1, 25)
            cell_format = book.add_format({'bold': True, 'font_size': 18})
            sheet.write_string(1, 1, str(context['message']), cell_format)
            book.close()
            return response

        sheet.set_zoom(75)          if context['filters']['split_by_dates'] else sheet.set_zoom(100)
        sheet.set_print_scale(30)   if context['filters']['split_by_dates'] else sheet.set_print_scale(75)
        sheet.set_paper(9) # A4
        sheet.set_landscape()       if context['filters']['split_by_dates'] else sheet.set_portrait()
        sheet.set_margins(0.3,0.3,0.3,0.3) # Inches

        # dictionary for actual cell format objects in xlsx workbook
        fd = {}

        if self.meta['start_col'] > 0:
            sheet.set_column(0, self.meta['start_col'] - 1, 2)

        white_row_format = get_xlsx_format(book, fd, {'meta':{'bgcolor': 'white'}})

        for row in range(self.meta['start_row']):
            row_write_style(sheet, row, self.meta['start_col'] + len(context['header']), white_row_format)
        # ------------------
        # write month header
        # ------------------
        row = self.meta['start_row']
        col = self.meta['start_col']

        if context['filters']['split_by_dates']:
            row_write_style(sheet, row, self.meta['start_col'] + len(context['header']), white_row_format)
            curr_month = 0
            month_format = get_xlsx_format(book, fd, {'meta':{'month-hdr': True}})
            for cell in context['header']:
                row_height = cell['meta'].get('height-month', None)
                if row_height:
                    sheet.set_row(row, row_height)
                span = cell['meta'].get('month_col_span')
                if span:
                    if curr_month != cell['name'].month:
                        curr_month = cell['name'].month
                        sheet.merge_range(row, col, row, col + span - 1, str(cell['caption_month']), month_format)
                col += 1
            row += 1

        # -----------------
        # write main header
        # -----------------
        col = self.meta['start_col']

        for cell in context['header']:
            #print(cell)
            col_width = cell['meta'].get('width', None)
            if col_width:
                sheet.set_column(col, col, col_width)
            row_height = cell['meta'].get('height', None)
            if row_height:
                sheet.set_row(row, row_height)

            # applying "upper(case) format option:
            cell_data = str(cell['caption']).upper() if cell['meta'].get('upper') else str(cell['caption'])
            cell_data = str(self.__apply_indent_and_wrap(
                                cell_data,
                                cell['meta'].get('indent'),
                                cell['meta'].get('wrap'),
                                cell['meta'].get('align', 'left'))
                            )

            weekday_data = cell.get('caption_weekday')
            if weekday_data:
                string_segments = [get_xlsx_format(book, fd, {'meta':{'font': 'monthday'}}), cell_data]
                string_segments.append(get_xlsx_format(book, fd, {'meta':{'font': 'weekday'}}))
                string_segments.append('\n' + str(weekday_data))
                sheet.write_rich_string(row, col,  *string_segments, get_xlsx_format(book, fd, cell))
            else:
                sheet.write_string(row, col, cell_data, get_xlsx_format(book, fd, cell))

            col += 1

        # ------------
        # write data
        # ------------
        for row_data in context['timelist'].values():
            row += 1
            col = self.meta['start_col']
            for cell in row_data.values():
                row_height = cell['meta'].get('height', None)
                if row_height:
                    sheet.set_row(row, row_height)
                if cell['data']:
                    if cell['meta'].get('dtype', None) == 'decimal':
                        sheet.write_number(row, col, cell['data'], get_xlsx_format(book, fd, cell))
                    else:
                        # applying "upper(case) format option:
                        cell_data = str(cell['data']).upper() if cell['meta'].get('upper') else str(cell['data'])
                        cell_data = str(self.__apply_indent_and_wrap(
                                            cell_data,
                                            cell['meta'].get('indent'),
                                            cell['meta'].get('wrap'),
                                            cell['meta'].get('align', 'left'))
                                        )
                        sheet.write_string(row, col, str(cell_data), get_xlsx_format(book, fd, cell))
                else:
                    sheet.write_blank(row, col, None, get_xlsx_format(book, fd, cell))

                col += 1;

        book.close()
        return response

    def _get_report_meta(self, **kwargs):
        return {}

    def _get_hdr_employee_meta(self, col_count):
        return {
            'bold': True,
            'valign': 'middle',
            'width': 20,
            'height': 45,
            'height-month': 35, # Month header line height
            'upper': True,
            'table-border': ('left', 'top', 'bottom'),
            'border': 'hdr-inner',
            'bgcolor': 'hdr',
            'font': 'default',
            'indent': 1,
            }

    def _get_hdr_projcat_meta(self, col_count):
        return {
            'bold': True,
            'width': 11,
            'align': 'left',
            'valign': 'middle',
            'upper': True,
            'border': 'hdr-inner',
            'table-border': ('top', 'bottom'),
            'bgcolor': 'hdr',
            'font': 'default',
            'indent': 1,
            'wrap': True,
            }

    def _get_hdr_project_meta(self, col_count):
        return {
            'bold': True,
            'width': 45 if col_count > 24 else 55,
            'valign': 'middle',
            'upper': True,
            'table-border': ('top', 'bottom'),
            'border': 'hdr-inner',
            'bgcolor': 'hdr',
            'font': 'default',
            'indent': 1,
            }

    def _get_hdr_totalhrs_meta(self, col_count, last_col = False):
        return {
            'bold': True,
            'width': 9,
            'align': 'right',
            'valign': 'middle',
            'upper': True,
            'border': 'hdr-inner',
            'table-border': ('top', 'bottom', 'right') if last_col else ('top', 'bottom'),
            'bgcolor': 'hdr',
            'font': 'default',
            'indent': 1,
            'wrap': True,
            }

    def _get_day_header_cell_meta(self, loopdate, date_from, date_to, last_col = False):
        if loopdate.isoweekday() in (6,7):
            border = 'wknd-hdr-inner'
            bgcolor = 'hdr-wknd'
        else:
            border = 'hdr-inner'
            bgcolor = 'hdr'

        return {
            'bold': True,
            'align': 'center',
            'valign': 'middle',
            'width': 6.5,
            'border': border,
            'table-border': ('top', 'bottom', 'right') if last_col else ('top', 'bottom'),
            'bgcolor': bgcolor,
            'font': 'default',
            'month_col_span': self.get_month_col_count(loopdate, date_from, date_to), #calculating colspan for month header
            }

    def _get_cell_meta(self, col, even, col_count, new_section = False, last_col=False):
        meta = {
            'valign': 'middle',
            'font': 'default',
            'indent': 1,
        }

        try:
            weekend = col.isoweekday() in (6,7)
        except:
            weekend = False

        if weekend:
            if even:
                meta['bgcolor'] = 'wknd-even'
                meta['border'] = 'wknd-even'
            else:
                meta['bgcolor'] = 'wknd-odd'
                meta['border'] = 'wknd-odd'
        else:
            if even:
                meta['bgcolor'] = 'even'
                meta['border'] = 'even'
            else:
                meta['bgcolor'] = 'odd'
                meta['border'] = 'odd'

        if new_section:
            meta['section-divider'] = True

        if col == 'employee':
            meta['height'] = 22
            meta['table-border'] = 'left'

        if last_col:
            meta['table-border'] = ('right',)

        return meta

    def _get_day_cell_meta(self, line, line_id, meta):
        meta['dtype'] = 'decimal'
        return meta

    def _get_total_cell_meta(self, line_id, meta, **kwargs):
        meta['dtype'] = 'decimal'
        return meta

    def _set_total_line_meta(self, total_line):
        for col_name, col in total_line.items():
            col['meta']['bold'] = True
            col['meta']['section-divider'] = True
            try:
                col['meta']['table-border'] += ('bottom',)
            except:
                col['meta']['table-border'] = 'bottom'

            if col_name not in ('employee', 'project'):
                col['meta']['dtype'] = 'decimal'
            elif col_name == 'employee':
                col['meta']['table-border'] = ('left', 'bottom')
