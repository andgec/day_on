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

def make_active(modeladmin, request, queryset):
    queryset.update(is_active = True)
make_active.short_description = _('Activate selected users')

def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active = False)
make_inactive.short_description = _('Deactivate selected users')

class UserAdmin(DjangoUserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(company = request.user.company)
        return qs

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            self.fieldsets=(
                (None, {'fields': ('username', 'password', 'company')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name')}),
                (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups',)}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
            )
        else:
            self.fieldsets=(
                (None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name')}),
                (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups',)}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
            )

        return super().get_fieldsets(request, obj)

    def get_list_display(self, request):
        if request.user.is_superuser:
            self.list_display = ('username', 'company', 'first_name', 'last_name', 'is_staff', 'is_employee', 'is_active')
        else:
            self.list_display = ('username', 'first_name', 'last_name', 'is_staff', 'is_employee', 'is_active')
        return super().get_list_display(request)

    def get_list_filter(self, request):
        if request.user.is_superuser:
            self.list_filter = ('company', 'is_staff', IsEmployeeFilter, 'is_active', 'groups')
        else:
            self.list_filter = ('is_staff', IsEmployeeFilter, 'is_active', 'groups')
        return super().get_list_filter(request)

    readonly_fields = ('last_login', 'date_joined')

    ordering = ('company', 'first_name', 'last_name')

    actions = [make_active, make_inactive]

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

    inlines = [
        EmployeeInLine,
    ]

admin_site.register(User, UserAdmin)
