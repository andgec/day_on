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
    request = None
    project = None

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        project_id = kwargs.pop('project_id', None)
        self.project = Project.objects.get(pk=project_id)
        super(PDashAssignEmployees, self).__init__(*args, **kwargs)
        self._init_fields()

    def _init_fields(self):
        employees = Employee.objects.filter(user__is_active=True).order_by('user__first_name', 'user__last_name').select_related('user')
        assigned_employees = self.project.employees.all();
        assigned_empl_ids = [assigned_employee.user_id for assigned_employee in assigned_employees]
        print(assigned_empl_ids)
        for employee in employees:
            self.fields['empl_%s' % employee.user_id] = forms.BooleanField(label=employee.full_name(),
                                                                           required=False,
                                                                           initial=employee.user_id in assigned_empl_ids
                                                                           )
    
    def get_employee_fields(self):
        for field_name in self.fields:
            yield self[field_name]

    def save(self, commit=False):
        print('RUN form.save() %s', self.cleaned_data)

        