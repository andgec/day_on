from django import forms
from general.forms import UniqNameTranslatableModelForm
from .models import ItemGroup, Item
from general.models import UnitOfMeasure


class ItemGroupAdminForm(UniqNameTranslatableModelForm):
    class Meta:
        model = ItemGroup
        widgets = {
            'description': forms.Textarea(attrs={'size': 250}),
        }
        fields = '__all__'


class ItemAdminForm(UniqNameTranslatableModelForm):
    def __init__(self, *args, **kwargs):
        def get_uom(company):
            uoms = UnitOfMeasure.objects.filter(company = company).order_by('id')
            return uoms[0].id if uoms else None
        super().__init__(*args, **kwargs)
        if self.request:
            self.fields['unit_of_measure'].initial = get_uom(self.request.user.company)

    class Meta:
        model = Item
        widgets = {
            'description': forms.Textarea(attrs={'rows':1, 'cols':100}),
        }
        fields = '__all__'
