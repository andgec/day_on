from django.contrib import admin
from django import forms
from django.contrib.admin import widgets
from django.db import models
from django.forms import Textarea
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import ugettext_lazy as _
from .models import Customer, ProjectCategory, Project, SalesOrderHeader
from .forms import SalesOrderAdminForm
from general.models import Contact
from django.forms.widgets import CheckboxSelectMultiple
from co_manager.admin import admin_site
from salary.models import Employee
from django.contrib.admin.widgets import FilteredSelectMultiple


class AssignedSalesOrderEmployeeAdminInline(admin.TabularInline):
    model = SalesOrderHeader.employees.through
    fields = ('employee',)
    extra = 0

class SalesOrderAdmin(admin.ModelAdmin):
    form = SalesOrderAdminForm
    readonly_fields=('created_date_time_str',)
    list_display=('id', 'created_date_time', 'customer', 'project')
    #list_filter     = ('customer', 'project')
    search_fields   = ('id', 'customer__name', 'project__name')
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'project', 'description', 'created_date_time_str')
        }),
        (_('Amounts'), {
            'fields': ('estimated_amount', 'discount_amount', 'discount_percent')
        }),
    )
    
    inlines = [
        AssignedSalesOrderEmployeeAdminInline,
    ]

class SalesOrderInLine(admin.TabularInline):
    model = SalesOrderHeader
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows':2, 'cols':60})},
        #models.CharField: {'widget': Textarea(attrs={'size':120})},
    }
    readonly_fields = ('created_date_time_str',)
    fields = ('created_date_time_str', 'description',)
    def has_add_permission(self, request):
        return False
    def has_edit_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False


class ContactInLine(GenericStackedInline):
    model = Contact
    extra = 0
    #ordering = ('first_name', 'last_name', 'address', 'city')
    #fields = ('first_name', 'last_name', 'address', 'city')
    
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name')
        }),
        (_('Address information'), {
            'fields': ('address', 'post_code', 'city', 'country')
        }),
        (_('Contact information'), {
            'fields': ('mobile_no', 'phone_no', 'email')
        }),
    )


class CustomerAdmin(admin.ModelAdmin):
    readonly_fields = ('full_address',)
    list_display    = ('name', 'number', 'full_address', 'type', 'active')
    list_filter     = ('active', 'type')
    search_fields   = ('name', 'number', 'address', 'address2', 'post_code', 'city', 'web_site') 

    fieldsets = (
        (None, {
            'fields': ('type', 'name', 'number', 'active')
        }),
        (_('Address information'), {
            'fields': ('address', 'post_code', 'city', 'country')
        }),
        (_('Other information'), {
            'fields': ('web_site',)
        }),
    )
    inlines = [
        ContactInLine,
    ]

class AssignedProjectEmployeeAdminInline(admin.TabularInline):
    model = Project.employees.through
    fields = ('employee',)
    extra = 0


class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description',)
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description',)
        }),
    )

# Form for sorting employees in filter_horizontal by first_name and last_name
class ProjectAdminForm(forms.ModelForm):
    employees = forms.ModelMultipleChoiceField(Employee.objects.all().order_by('user__first_name', 'user__last_name'), widget=FilteredSelectMultiple(_('Employees'), False))
    employees.label = _('Employees')
    class Meta:
        model = Project
        '''
        widgets = {
            'employees': FilteredSelectMultiple(_("Employees"), False),
            }
        '''
        fields = '__all__'


class ProjectAdmin(admin.ModelAdmin):
    form = ProjectAdminForm

    list_display = ('name', 'description', 'category', 'customer', 'active',)
    list_filter = ('active', 'category')
    search_fields   = ('name', 'description', 'category', 'customer__name',)

    fieldsets = (
        (None, {
            'fields': ('customer', 'name', 'category', 'description', 'comment', 'active', 'visible', 'employees',)
        }),
    )


admin_site.register(Customer, CustomerAdmin)
admin_site.register(ProjectCategory, ProjectCategoryAdmin)
admin_site.register(Project, ProjectAdmin)
#admin_site.register(SalesOrderHeader, SalesOrderAdmin)
