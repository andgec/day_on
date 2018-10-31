from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Employee

class EmployeeAdmin(admin.ModelAdmin):
    list_display=('full_name', 'mobile_no', 'email', 'is_active')    
    readonly_fields = ('full_name', 'user', 'email', 'is_active')
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
    def has_add_permission(self, request):
        return False


admin.site.register(Employee, EmployeeAdmin)