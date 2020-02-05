from django.db import models
from django.db.models.deletion import PROTECT
from django.core.exceptions import ValidationError
from parler.models import TranslatedField, TranslatedFields
from general.models import UnitOfMeasure, CoTranslatableModel
from django.utils.translation import ugettext_lazy as _

class ItemGroup(CoTranslatableModel):
    translations = TranslatedFields(
        name            = models.CharField(
                              max_length=60,
                              #unique=True,
                              verbose_name = _('Name')
                              ),
        description     = models.CharField(
                              max_length=250,
                              blank=True, 
                              default='',
                              verbose_name = _('Description')
                              )
        )
    name = TranslatedField(any_language=True)
    description = TranslatedField(any_language=True)
    '''
    def clean(self):
        print(self.company, self.name)
        qs_duplicates = ItemGroup.objects.filter(company = self.company, translations__name = self.name).exclude(id=self.id)
        if qs_duplicates.count() != 0:
            raise ValidationError({'name': _('Item group with given name already exists.')})
    '''
    class Meta:
        verbose_name = _('Item group')
        verbose_name_plural = _('Item groups')

    def __str__(self):
        return self.name


class Item(CoTranslatableModel):
    translations = TranslatedFields(
        name            = models.CharField(
                              max_length =100,
                              #unique=True,
                              verbose_name = _('Name')
                          ),
        description     = models.CharField(
                              max_length=250,
                              blank=True,
                              default='',
                              verbose_name = _('Description')
                          )
    )

    name = TranslatedField(any_language=True)
    description = TranslatedField(any_language=True)

    item_group      = models.ForeignKey(
                          ItemGroup,
                          on_delete=PROTECT,
                          verbose_name = _('Item group'),
                          related_name = 'items',
                          )
    unit_of_measure = models.ForeignKey(
                          UnitOfMeasure,
                          on_delete=PROTECT,
                          verbose_name = _('Unit of measure')
                          )
    active          = models.BooleanField(
                          default=True,
                          verbose_name = _('Active')
                          )
    price           = models.DecimalField(
                          default = 0,
                          max_digits=14,
                          decimal_places=2,
                          verbose_name = _('Price')
                          )

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
    
    def __str__(self):
        return self.name
