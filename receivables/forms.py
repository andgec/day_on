from django.utils import timezone
from django import forms
from .models import Project, SalesOrderHeader, WorkTimeJournal
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2Widget
from django.forms.widgets import SelectDateWidget
#from nntplib import ArticleInfo

class SalesOrderAdminForm(forms.ModelForm):
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
        super(WorkTimeJournalForm, self).__init__(*args, **kwargs)
        self.fields['work_date'].initial = timezone.now()
    class Meta:
        model = WorkTimeJournal
        fields = ['item',
                  'work_date',
                  'work_time_from',
                  'work_time_to',
                  'distance',
                  'toll_ring',
                  'ferry',
                  'diet'
                  ]
        widgets = {
            'work_date': SelectDateWidget(years = range(2010, 2030)),
            'employee': forms.Select(attrs={'disabled': True}),
            'work_time_from': forms.TimeInput(),
            'work_time_to': forms.TimeInput()
        }
        

    