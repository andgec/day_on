from django.contrib import admin
from parler.admin import TranslatableAdmin
from parler.admin import TranslatableTabularInline

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

admin.site.register(ItemGroup, ItemGroupAdmin)
admin.site.register(Item, ItemAdmin)