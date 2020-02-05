from django.db import models
from parler.models import TranslatableModel
from shared.models import AddressMixin, ContactMixin
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _
from django.db.models.deletion import CASCADE, PROTECT
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
#from djauth.models import User

class Company(AddressMixin, ContactMixin, models.Model):
    name        = models.CharField(max_length=60, unique=True, verbose_name=_('Name'))
    number      = models.CharField(max_length=30, unique=True, verbose_name=_('Number'))
    web_site    = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Website'))

    class Meta:
        abstract = False
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
    def __str__(self):
        return self.name


#Base translatable class for models in Co project
class CoTranslatableModel(TranslatableModel):
    company = models.ForeignKey(Company, default=1, on_delete = PROTECT)
    class Meta:
        abstract = True


#Base class for models in Co project
class CoModel(models.Model):
    company = models.ForeignKey(Company, default=1, on_delete = PROTECT)
    class Meta:
        abstract = True


class Contact(ContactMixin, AddressMixin, models.Model):
    company     = ForeignKey(Company, default=1, on_delete=CASCADE)
    first_name  = models.CharField(max_length=60, verbose_name=_('First name'))
    last_name   = models.CharField(max_length=60, blank=True, default='', verbose_name=_('Last name'))
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class Address(ContactMixin, AddressMixin, models.Model):
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        abstract = False
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        
    def __str__(self):
        return self.address


class UnitOfMeasure(models.Model):
    company     = models.ForeignKey(Company, default=1, on_delete=CASCADE)
    name        = models.CharField(max_length=10, verbose_name='Name') #Use ISO codes
    description = models.CharField(max_length=60, verbose_name='Description') #ToDo: add translation
    active      = models.BooleanField(default=False)
    class Meta:
        verbose_name = _('Unit of measure')
        verbose_name_plural = _('Units of measure')
    def __str__(self):
        return self.name + ' (' + self.description + ')'
    
