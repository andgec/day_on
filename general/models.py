from django.db import models
from shared.models import AddressMixin, ContactMixin
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _
from django.db.models.deletion import CASCADE
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
#from djauth.models import User

class Company(AddressMixin, ContactMixin, models.Model):
    name        = models.CharField(max_length=60, unique=True)
    number      = models.CharField(max_length=30, unique=True)
    web_site    = models.CharField(max_length=250, blank=True, null=True)
    
    class Meta:
        abstract = False
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')
    def __str__(self):
        return self.name

class Contact(ContactMixin, AddressMixin, models.Model):
    company     = ForeignKey(Company, default=1, on_delete=CASCADE)
    first_name  = models.CharField(max_length=60)
    last_name   = models.CharField(max_length=60, blank=True, default='')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    def __str__(self):
        return self.first_name + ' - ' + self.last_name

class Address(ContactMixin, AddressMixin, models.Model):
    
    class Meta:
        abstract = False
    def __str__(self):
        return self.address

class UnitOfMeasure(models.Model):
    name        = models.CharField(max_length=10) #Use ISO codes
    description = models.CharField(max_length=60) #ToDo: add translation
    active      = models.BooleanField(default=False)
    class Meta:
        verbose_name_plural = _('Units of measure')
    def __str__(self):
        return self.name
    

    
