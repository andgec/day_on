from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline
from .models import Customer, Project, SalesOrderHeader
from .forms import SalesOrderAdminForm
from general.models import Contact
from django.utils.translation import ugettext_lazy as _

class SalesOrderAdmin(admin.ModelAdmin):
    form = SalesOrderAdminForm
    readonly_fields=('created_date_time_str',)
    list_display=('id', 'created_date_time', 'customer', 'project')
    fieldsets = (
        (None, {
            'fields': ('customer', 'project', 'description', 'created_date_time_str')
        }),
        (_('Amounts'), {
            'fields': ('estimated_amount', 'discount_amount', 'discount_percent')
        }),
    )


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

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Project)
admin.site.register(SalesOrderHeader, SalesOrderAdmin)

#admin.site.register(SalesOrderLine)