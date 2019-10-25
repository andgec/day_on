from django.utils.functional import curry
from parler.admin import TranslatableAdmin
from parler.admin import TranslatableTabularInline

from co_manager.admin import admin_site
from .models import ItemGroup, Item
from .forms import ItemGroupAdminForm, ItemAdminForm

class ItemInLine(TranslatableTabularInline):
    form = ItemAdminForm
    fields = ('name', 'description', 'unit_of_measure', 'price', 'active')
    model = Item

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if request.method == "GET":
            for i in range(self.extra):
                initial.append({'unit_of_measure': 1}) # %MULTICOMPANY% This will not work for multi-company setup. Use setup table to set default unit of measure.
            formset = super(ItemInLine, self).get_formset(request, obj, **kwargs)
            formset.__init__ = curry(formset.__init__, initial=initial)
            return formset


class ItemGroupAdmin(TranslatableAdmin):
    form = ItemGroupAdminForm
    inlines = [
        ItemInLine,
    ]


class ItemAdmin(TranslatableAdmin):
    list_display    = ('name', 'description', 'unit_of_measure', 'item_group', 'active')
    fields = ('item_group', 'name', 'description', 'unit_of_measure', 'price', 'active')
    list_filter     = ('item_group', 'active',)
    search_fields   = ('name', 'description', 'unit_of_measure__description', 'item_group__name')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ItemAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['unit_of_measure'].initial = 1 # %MULTICOMPANY% This will not work for multi-company setup. Use setup table to set default unit of measure.
        return form


admin_site.register(ItemGroup, ItemGroupAdmin)
admin_site.register(Item, ItemAdmin)