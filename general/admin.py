from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .models import Company, UnitOfMeasure

class CompanyAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs=super().get_queryset(request)
        if request.user.is_superuser:
            return qs.exclude(id=1)
        return qs.exclude(id=1)
    
    def has_add_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        (None, {
            'fields': ('name', 'number')
        }),
        (_('Address'), {
            'fields': ('address', 'city', 'post_code', 'country')
        }),
        (_('Contact information'), {
            'fields': ('email', 'phone_no', 'mobile_no', 'fax_no')
        }),
        (_('Other'), {
            'fields': ('web_site',)
        }),
    )

admin.site.register(Company, CompanyAdmin)
admin.site.register(UnitOfMeasure)