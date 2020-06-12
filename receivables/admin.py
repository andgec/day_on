from django.contrib import admin
from django import forms
from django.contrib.admin import widgets
from django.contrib.admin.filters import SimpleListFilter
from django.db import models
from django.forms import Textarea
from django.contrib.contenttypes.admin import GenericStackedInline
from django.utils.translation import ugettext_lazy as _
from .models import Customer, ProjectCategory, Project, SalesOrderHeader
from .forms import SalesOrderAdminForm, CustomerAdminForm, ProjectAdminForm
from general.models import Contact
from django.forms.widgets import CheckboxSelectMultiple
from co_manager.admin import admin_site
from general.admin import CoModelAdmin


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


class CustomerAdmin(CoModelAdmin):
    form = CustomerAdminForm
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


class ProjectCategoryAdmin(CoModelAdmin):
    list_display = ('name', 'description',)
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description',)
        }),
    )


class ProjectCategoryListFilter(SimpleListFilter):
    title = _('Project category')
    parameter_name = 'project_category__id__exact'
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        q_project_categories = ProjectCategory.objects.filter(company = request.user.company).order_by('name')
        project_categories = list(q_project_categories.values_list('id', 'name'))
        return project_categories

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is None:
            return queryset
        return queryset.filter(category_id = self.value())


class ProjectAdmin(CoModelAdmin):
    form = ProjectAdminForm

    list_display = ('name', 'description', 'category', 'customer', 'active',)
    list_filter = ('active', ProjectCategoryListFilter)
    search_fields   = ('name', 'description', 'category__name', 'customer__name',)

    fieldsets = (
        (None, {
            'fields': ('customer', 'name', 'category', 'description', 'comment', 'active', 'visible', 'employees',)
        }),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        qs = db_field.related_model.objects.filter(
            company = request.user.company).prefetch_related(
            'user').order_by(
            'user__first_name', 'user__last_name')
        kwargs['queryset'] = qs
        return super().formfield_for_manytomany(db_field, request, **kwargs)


admin_site.register(Customer, CustomerAdmin)
admin_site.register(ProjectCategory, ProjectCategoryAdmin)
admin_site.register(Project, ProjectAdmin)
#admin_site.register(SalesOrderHeader, SalesOrderAdmin)
