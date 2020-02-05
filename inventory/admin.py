from general.admin import CoTranslatableTabularInline
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.filters import SimpleListFilter
from co_manager.admin import admin_site
from general.admin import CoTranslatableAdmin
from .models import ItemGroup, Item
from .forms import ItemGroupAdminForm, ItemAdminForm


class ItemInLine(CoTranslatableTabularInline):
    form = ItemAdminForm
    fields = ('name', 'description', 'unit_of_measure', 'price', 'active')
    model = Item


class ItemGroupAdmin(CoTranslatableAdmin):
    form = ItemGroupAdminForm
    inlines = [
        ItemInLine,
    ]


class ItemGroupListFilter(SimpleListFilter):
    title = _('Item group')
    parameter_name = 'item_group__id__exact'
    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        # Get translated items
        q_item_groups = ItemGroup.objects.filter(company = request.user.company).translated().prefetch_related('translations')
        # Get not translated items
        q_item_groups2 = ItemGroup.objects.filter(company = request.user.company).exclude(id__in = [t.id for t in q_item_groups]).active_translations().prefetch_related('translations')
        # Join items in both languages:
        item_groups = list(q_item_groups.values_list('id', 'translations__name')) + list(q_item_groups2.values_list('id', 'translations__name'))
        # Sort items by name:
        item_groups.sort(key=lambda item_group: item_group[1].lower())
        return item_groups

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() is None:
            return queryset
        return queryset.filter(item_group_id = self.value())


class ItemAdmin(CoTranslatableAdmin):
    list_display    = ('name', 'description', 'unit_of_measure', 'item_group', 'active')
    fields = ('item_group', 'name', 'description', 'unit_of_measure', 'price', 'active')
    #list_filter     = ('item_group', 'active',)
    list_filter     = (ItemGroupListFilter, 'active',)
    search_fields   = ('name', 'description', 'unit_of_measure__description', 'item_group__name')
    form            = ItemAdminForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('item_group__translations')


admin_site.register(ItemGroup, ItemGroupAdmin)
admin_site.register(Item, ItemAdmin)