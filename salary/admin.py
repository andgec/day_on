from django.contrib import admin
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from shared.snippets import MultiFieldSortableModelAdmin
from .models import Employee
from co_manager.admin import admin_site
from django.apps import apps


class IsActiveFilter(admin.SimpleListFilter):
    title = _('Active')
    parameter_name = 'is_active'

    def lookups(self, request, models_admin):
        return(
            (True, _('Yes')),
            (False, _('No')),
        )
    
    def queryset(self, request, queryset):
        value = self.value()

        if value is not None:
            return queryset.filter(user__is_active=value)
        return queryset


class EmployeeAdmin(MultiFieldSortableModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(company = request.user.company)
    
    list_select_related = ('user',)
    list_display = ('full_name', 'mobile_no', 'email', 'is_active',)    
    readonly_fields = ('full_name', 'user', 'email', 'is_active')
    search_fields = ('user__first_name',
                     'user__last_name',
                     'user__email',
                     'mobile_no',
                     'phone_no',
                     'address',
                     'post_code',
                     'city',
                     'country')
    list_filter     = (IsActiveFilter,)
    fieldsets = (
        (None, {
            'fields': ('full_name', 'user', 'is_active')
        }),
        (_('Contact information'), {
            'fields': ('mobile_no', 'phone_no', 'email')
        }),
        (_('Address information'), {
            'fields': ('address', 'post_code', 'city', 'country')
        }),
    )

    def is_active(self, obj):
        return obj.is_active()
    
    is_active.boolean = True
    is_active.admin_order_field = 'user__is_active'
    is_active.short_description = _('Active')


    def full_name(self, obj):
        return obj.full_name()

    full_name.admin_order_field = ['user__first_name', 'user__last_name']
    full_name.short_description = _('Full name')


    def email(self, obj):
        return obj.email()
    email.admin_order_field = 'user__email'
    email.short_description = _('Email')

    def has_add_permission(self, request):
        return False

Employee = apps.get_model('salary.Employee')
Employee._meta.app_name = 'djauth'
admin_site.register(Employee, EmployeeAdmin)
