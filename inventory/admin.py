from django.contrib import admin
from parler.admin import TranslatableAdmin
from parler.admin import TranslatableTabularInline

from co_manager.admin import admin_site
from .models import ItemGroup, Item
from .forms import ItemGroupAdminForm, ItemAdminForm

class ItemInLine(TranslatableTabularInline):
    form = ItemAdminForm
    fields = ('name', 'description', 'unit_of_measure', 'price', 'active')
    model = Item

class ItemGroupAdmin(TranslatableAdmin):
    form = ItemGroupAdminForm
    inlines = [
        ItemInLine,
    ]

class ItemAdmin(admin.ModelAdmin):
    list_display    = ('name', 'description', 'unit_of_measure', 'item_group', 'active')
    list_filter     = ('item_group', 'active',)
    search_fields   = ('name', 'description', 'unit_of_measure__description', 'item_group__name') 

admin_site.register(ItemGroup, ItemGroupAdmin)
admin_site.register(Item, ItemAdmin)