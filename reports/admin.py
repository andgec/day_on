from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render

from django.http import HttpResponse

from co_manager.admin import admin_site


class TimelistPDFFakeModel(object):
    class _meta:
        app_label = _('Reports') 
        model_name = _('Print timelist')
        verbose_name_plural = _('Print timelist')
        object_name = 'ObjectName'
        app_config = app_label
        
        swapped = False
        abstract = False


class TimelistAdminForm(admin.ModelAdmin):
    def has_add_permission(self, *args, **kwargs):
        return False

    def has_change_permission(self, *args, **kwargs):
        return True

    def has_delete_permission(self, *args, **kwargs):
        return False

    def changelist_view(self, request):
        context = {'title': 'Timelist Admin Form'}
        '''
        if request.method == 'POST':
            form = CustomForm(request.POST)
            if form.is_valid():
                # Do your magic with the completed form data.

                # Let the user know that form was submitted.
                messages.success(request, 'Congrats, form submitted!')
                return HttpResponseRedirect('')
            else:
                messages.error(
                    request, 'Please correct the error below'
                )

        else:
            form = CustomForm()

        context['form'] = form
        
        return render(request, 'admin/change_form.html', context)
        '''
        return HttpResponse("Hello!")
    
    
#admin_site.register([TimelistPDFFakeModel], TimelistAdminForm)
