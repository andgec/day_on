from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.contrib.contenttypes.admin import GenericStackedInline
from .models import Customer, Project, SalesOrderHeader
from .forms import SalesOrderAdminForm
from general.models import Contact
from django.utils.translation import ugettext_lazy as _

class SalesOrderAdmin(admin.ModelAdmin):
    form = SalesOrderAdminForm
    readonly_fields=('created_date_time_str',)
    list_display=('id', 'created_date_time', 'customer', 'project')
    #list_filter     = ('customer', 'project')
    search_fields   = ('id', 'customer__name', 'project__name')
    
    fieldsets = (
        (None, {
            'fields': ('customer', 'project', 'description', 'created_date_time_str', 'employees')
        }),
        (_('Amounts'), {
            'fields': ('estimated_amount', 'discount_amount', 'discount_percent')
        }),
    )
    
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
    
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'customer', 'active',)
    list_filter = ('active',)
    search_fields   = ('name', 'description', 'customer__name',)
    
    inlines = [
        SalesOrderInLine,
    ]

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(SalesOrderHeader, SalesOrderAdmin)

#admin.site.register(SalesOrderLine)