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
    assigned_empl_ids = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.project = kwargs.pop('project', None)
        #self.project = Project.objects.get(pk=project_id)
        super(PDashAssignEmployees, self).__init__(*args, **kwargs)
        self._init_fields()

    def _init_fields(self):
        employees = Employee.objects.filter(user__is_active=True).order_by('user__first_name', 'user__last_name').select_related('user')
        assigned_employees = self.project.employees.all();
        self.assigned_empl_ids = [assigned_employee.user_id for assigned_employee in assigned_employees]
        for employee in employees:
            self.fields['empl_%s' % employee.user_id] = forms.BooleanField(label=employee.full_name(),
                                                                           required=False,
                                                                           initial=employee.user_id in self.assigned_empl_ids
                                                                           )
    
    def get_employee_fields(self):
        for field_name in self.fields:
            yield self[field_name]
            
    def get_add_value_list(self):
        empl_id_list = []
        for key, value in self.cleaned_data.items():
            if value:
                empl_id_list.append(int(key.replace('empl_', '')))
        return empl_id_list
    
    def get_remove_value_list(self):
        old_list = self.assigned_empl_ids
        new_list = self.get_add_value_list()
        return [id for id in old_list if id not in new_list]
            
    def save(self, commit=False):
        self.project.employees.add(*self.get_add_value_list())
        self.project.employees.remove(*self.get_remove_value_list())

        