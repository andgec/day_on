from django.db import models
from django.db.models.deletion import PROTECT
from general.models import UnitOfMeasure
from django.utils.translation import ugettext_lazy as _

class ItemGroup(models.Model):
    name            = models.CharField(max_length=60)
    description     = models.CharField(max_length=250, blank=True, default='')
    
    class Meta:
        verbose_name = _('Item group')
        verbose_name_plural = _('Item groups')
    
    def __str__(self):
        return self.name


class Item(models.Model):
    name            = models.CharField(max_length =100)
    description     = models.CharField(max_length=250, blank=True, default='')
    item_group      = models.ForeignKey(ItemGroup, on_delete=PROTECT)
    unit_of_measure = models.ForeignKey(UnitOfMeasure, on_delete=PROTECT)
    active          = models.BooleanField(default=True)
    price           = models.DecimalField(blank=True, max_digits=14, decimal_places=4)

    class Meta:
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
    
    def __str__(self):
        return self.name
