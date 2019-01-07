from django.utils import timezone
from django import forms
from .models import Project, SalesOrderHeader, WorkTimeJournal
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2Widget
from django.forms.widgets import SelectDateWidget
from shared.widgets import SelectTimeWidget
from inventory.models import ItemGroup, Item
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
    '''    
    accepted
    To validate a single field on it's own you can use a clean_FIELDNAME() method in your form, so for email:
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email
    then for co-dependant fields that rely on each other, you can overwrite the forms clean() method which is run after all the fields (like email above) have been validated individually:
    
    def clean(self):
        form_data = self.cleaned_data
        if form_data['password'] != form_data['password_repeat']:
            self._errors["password"] = ["Password do not match"] # Will raise a error message
            del form_data['password']
        return form_data
    '''     
    def __init__(self, *args, **kwargs):
        super(WorkTimeJournalForm, self).__init__(*args, **kwargs)
        self.work_date = kwargs.get('work_date', timezone.now())
        self.fields['work_date'].initial = self.work_date
        self.fields['item'].choices = self.items_as_choices()
        
    def items_as_choices(self):
        item_group_list = []
        for itemgroup in ItemGroup.objects.all():
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
            'work_time_from': SelectTimeWidget(minute_step = 5, seconds_visible = False),
            'work_time_to': SelectTimeWidget(minute_step = 5, seconds_visible = False),
            'distance': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'toll_ring': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'ferry': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
            'diet': forms.NumberInput(attrs={'class': 'timereg_num_field'}),
        }
        

    