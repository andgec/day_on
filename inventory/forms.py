from django import forms
from parler.forms import TranslatableModelForm, TranslatableBaseInlineFormSet
from .models import ItemGroup, Item

class ItemGroupAdminForm(TranslatableModelForm):
    class Meta:
        model = ItemGroup
        widgets = {
            'description': forms.Textarea(attrs={'size': 250}),
        }
        fields = '__all__'

class ItemAdminForm(TranslatableModelForm):
    class Meta:
        model = Item
        widgets = {
            'description': forms.Textarea(attrs={'rows':1, 'cols':100}),
        }
        fields = '__all__'
