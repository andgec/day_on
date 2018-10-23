from django import forms
from .models import Customer, Project, SalesOrderHeader
from django.utils.translation import ugettext_lazy as _
from django_select2.forms import ModelSelect2Widget

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
    