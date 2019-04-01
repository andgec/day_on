from django import forms
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.utils.translation import ugettext_lazy as _
#from django.forms.widgets import HiddenInput
from receivables.models import Project
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.utils import construct_change_message
from salary.models import Employee 

class PDashProjectForm(forms.ModelForm):
    name = forms.CharField(label = _('Project name'), widget=forms.TextInput(attrs={'size':'60'}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 1, 'cols': 32}))
    mode = ADDITION
    request = None
    #customer_id = forms.IntegerField(required=True, widget=HiddenInput())

    class Meta:
        model = Project
        fields = ('customer', 'name', 'comment', 'description')
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PDashProjectForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.mode = CHANGE
    
    def save(self, commit=True):
        #data = self.cleaned_data
        obj = super(PDashProjectForm, self).save(commit=False)
        
        if commit:
            obj.save()
            LogEntry.objects.log_action(
                user_id         = self.request.user.pk,
                content_type_id = ContentType.objects.get_for_model(obj).pk,
                object_id       = obj.pk,
                object_repr     = str(obj),
                action_flag     = self.mode,
                change_message  = construct_change_message(self, formsets=None, add=(self.mode==ADDITION)),
                )
        return obj

class PDashAssignEmployees(forms.Form):
    fields = {}

    def __init__(self, *args, **kwargs):
        super(PDashAssignEmployees, self).__init__(*args, **kwargs)
        self._init_fields()        

    def _init_fields(self):
        employees = Employee.objects.filter(user__is_active=True).order_by('user__first_name', 'user__last_name').select_related('user')
        for employee in employees:
            self.fields['empl_%s' % employee.user_id] = forms.BooleanField(label=employee.full_name())

    def save(self):
        pass        
        