from django.db import models
from django.db.models.deletion import PROTECT
from parler.models import TranslatableModel, TranslatedFields
from general.models import UnitOfMeasure
from django.utils.translation import ugettext_lazy as _

class ItemGroup(TranslatableModel):
    translations = TranslatedFields(
        name            = models.CharField(
                              max_length=60,
                              unique=True,
                              verbose_name = _('Name')
                              ),
        description     = models.CharField(
                              max_length=250,
                              blank=True, 
                              default='',
                              verbose_name = _('Description')
                              )
        )
    
    class Meta:
        verbose_name = _('Item group')
        verbose_name_plural = _('Item groups')
    
    def __str__(self):
        return self.name


class Item(TranslatableModel):
    translations = TranslatedFields(
        name            = models.CharField(
                              max_length =100,
                              unique=True,
                              verbose_name = _('Name')
                          ),
        description     = models.CharField(
                              max_length=250,
                              blank=True,
                              default='',
                              verbose_name = _('Description')
                          )
    )
    item_group      = models.ForeignKey(
                          ItemGroup,
                          on_delete=PROTECT,
                          verbose_name = _('Item group')
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
