from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from receivables.models import Employee
from django.contrib.admin.options import StackedInline
from co_manager.admin import admin_site

from .models import User


class EmployeeInLine(StackedInline):
    model = Employee
    extra = 0

    fieldsets = (
        (None, {
            'fields': ('mobile_no', 'phone_no')
        }),
        (_('Address information'), {
            'fields': ('address', 'post_code', 'city', 'country')
        }),
    )
    verbose_name = 'Employee'
    verbose_name_plural = 'Employee'


class IsEmployeeFilter(admin.SimpleListFilter):
    title = _('Employee')
    parameter_name = 'is_employee'

    def lookups(self, request, models_admin):
        return(
            (True, _('Yes')),
            (False, _('No')),
        )
    
    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            value = value != 'True' #converting to boolean and reversing the value for query
            return queryset.filter(employee__isnull=value)
        return queryset


class UserAdmin(DjangoUserAdmin):

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        return qs

    readonly_fields = ('last_login', 'date_joined')
    list_filter = ('is_staff', IsEmployeeFilter, 'is_active', 'groups')    

    fieldsets=(
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display=('username', 'first_name', 'last_name', 'is_staff', 'is_employee', 'is_active')

    def save_model(self, request, obj, form, change):
        obj.company = request.user.company
        super().save_model(request, obj, form, change)

    inlines = [
        EmployeeInLine,
    ]

admin_site.register(User, UserAdmin)
