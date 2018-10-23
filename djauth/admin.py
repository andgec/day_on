from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from receivables.models import Employee
from django.contrib.admin.options import StackedInline
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


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    readonly_fields = ('last_login', 'date_joined')
   
    fieldsets=(
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'groups',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display=('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_employee')
    
    def save_model(self, request, obj, form, change):
        obj.company = request.user.company
        print('Saving user. Company: ' + str(request.user.company))        
        super().save_model(request, obj, form, change)
        
        
    inlines = [
        EmployeeInLine,
    ]

    
    pass
