from django.utils import timezone
from django import forms
from django_select2.forms import Select2Widget
from .models import Project, SalesOrderHeader, WorkTimeJournal, Customer
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2Widget
from django.forms.widgets import SelectDateWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
from shared.widgets import SelectTimeWidget
from inventory.models import ItemGroup
from general.forms import CoModelForm


class CustomerAdminForm(CoModelForm):
    class Meta:
        model = Customer
        fields = '__all__'


class ProjectAdminForm(CoModelForm):
    # sorting employees in filter_horizontal by first_name and last_name (moved to ProjectModelAdmin).
    #employees = forms.ModelMultipleChoiceField(Employee.objects.all().order_by('user__first_name', 'user__last_name'), widget=FilteredSelectMultiple(_('Employees'), False))
    #employees.label = _('Employees')
    class Meta:
        model = Project

        widgets = {
            'employees': FilteredSelectMultiple(_("Employees"), False),
            }

        fields = '__all__'


class SalesOrderAdminForm(forms.ModelForm): # Unused
    description = forms.CharField(widget = forms.Textarea, max_length=120)
    class Meta:
        model = SalesOrderHeader
        fields = ('__all__')
        '''
        widgets = {
            'customer': ModelSelect2Widget(
                    search_fields=['name__icontains'],
                    dependent_fields={'project': 'projects'},
                ),
            'project': ModelSelect2Widget(
                    search_fields=['name__icontains'],
                    dependent_fields={'customer': 'customer'},
                    max_results=500,
                ),
        }
        '''
    '''    
    customer = forms.ModelChoiceField(
        queryset = Customer.objects.all(),
        label = _('Customer'),
        widget = ModelSelect2Widget(
            search_fields=['name__icontains'],
            #dependent_fields={'project': 'projects'},
            queryset = Customer.objects.all(), 
        )
    )
    '''
    project = forms.ModelChoiceField(
        queryset = Project.objects.all(),
        label = _('Project'),
        widget = ModelSelect2Widget(
            search_fields=['name__icontains'],
            dependent_fields={'customer': 'customer'},
            max_results=500,
            queryset = Project.objects.all(),
            model = Project
        )
    )


class WorkTimeJournalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(WorkTimeJournalForm, self).__init__(*args, **kwargs)
        self.work_date = kwargs.get('work_date', timezone.now())
        self.fields['work_date'].initial = self.work_date
        self.fields['item'].choices = self.items_as_choices()

    def items_as_choices(self):
        item_group_list = []
        for itemgroup in ItemGroup.objects.filter(company = self.company or -1).prefetch_related('translations'
                                                                              ).prefetch_related('items'
                                                                              ).prefetch_related('items__translations'):
            new_itemgroup = []
            item_list = []
            for item in itemgroup.items.all():
                item_list.append([item.id, item.name])

            new_itemgroup = [itemgroup.name, item_list]
            item_group_list.append(new_itemgroup)
        return item_group_list

    class Meta:
        model = WorkTimeJournal
        readonly_fields = ['empty',]
        fields = ['item',
                  'employee',
                  'work_date',
                  'work_time_from',
                  'work_time_to',
                  'distance',
                  'toll_ring',
                  'ferry',
                  'diet',
                  'parking',
                  ]

        widgets = {
            'item': Select2Widget,
            'employee': Select2Widget,
            'work_date': SelectDateWidget(years = range(2010, 2030)),
            'work_time_from': SelectTimeWidget(minute_step = 5, seconds_visible = False),
            'work_time_to': SelectTimeWidget(minute_step = 5, seconds_visible = False),
            'distance': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'toll_ring': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'ferry': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'diet': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'parking': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
        }


class WorkTimeJournalForm_V2(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super(WorkTimeJournalForm_V2, self).__init__(*args, **kwargs)
        self.work_date = kwargs.get('work_date', timezone.now())
        self.fields['work_date'].initial = self.work_date
        self.fields['item'].choices = self.items_as_choices()
        self.fields['item'].error_messages['invalid_choice'] = '' # Clear built-in field validation error message

    def items_as_choices(self):
        item_group_list = []
        # Adding an empty value to the top of the list:
        item_group_list.append([0, '----------------------'])
        for itemgroup in ItemGroup.objects.filter(company = self.company or -1).prefetch_related('translations'
                                                                              ).prefetch_related('items'
                                                                              ).prefetch_related('items__translations'):
            new_itemgroup = []
            item_list = []
            for item in itemgroup.items.all():
                item_list.append([item.id, item.name])
            new_itemgroup = [itemgroup.name, item_list]
            item_group_list.append(new_itemgroup)
        return item_group_list

    class Meta:
        model = WorkTimeJournal
        readonly_fields = ['empty',]
        fields = ['object_id',
                  'item',
                  'employee',
                  'work_date',
                  'work_time_from',
                  'work_time_to',
                  'distance',
                  'toll_ring',
                  'ferry',
                  'diet',
                  'parking',
                  ]

        widgets = {
            'object_id': forms.NumberInput(attrs={'hidden': True}),
            'item': Select2Widget,
            'work_date': SelectDateWidget(years = range(2010, 2030)),
            'work_time_from': SelectTimeWidget(minute_step = 5, seconds_visible = False),
            'work_time_to': SelectTimeWidget(minute_step = 5, seconds_visible = False),
            'distance': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'toll_ring': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'ferry': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'diet': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'parking': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
        }
