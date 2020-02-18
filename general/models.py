import os
from django.db import models
from parler.models import TranslatableModel
from shared.models import AddressMixin, ContactMixin
from django.db.models.fields.related import ForeignKey
from django.utils.translation import ugettext_lazy as _
from django.utils.html import mark_safe
from django.db.models.deletion import CASCADE, PROTECT
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from shared.utils import get_image_path
from conf.settings import MEDIA_URL
from shared.utils import image_as_base64


class Company(AddressMixin, ContactMixin, models.Model):
    name            = models.CharField(max_length=60, unique=True, verbose_name=_('Name'))
    number          = models.CharField(max_length=30, unique=True, verbose_name=_('Number'))
    web_site        = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Website'))
    images_subdir   = 'company-logos' ## used in function get_image_path for the field "logo"
    logo            = models.ImageField(upload_to=get_image_path,
                                        blank=True,
                                        null=True,
                                        verbose_name = _('change logo'))

    ## Display logo image
    def logo_tag(self):
        if self.logo:
            return mark_safe('<img src="%s" width="300") />' % os.path.join(MEDIA_URL, str(self.logo)))
        else:
            return _('not selected').capitalize()

    logo_tag.short_description = _('logo')

    def logo_base64(self):
        image_format = (os.path.splitext(self.logo.path))[1]
        return image_as_base64(self.logo.path, image_format)

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
    name        = models.CharField(max_length=10, verbose_name=_('Name'))
    description = models.CharField(max_length=60, verbose_name=_('Description'))
    active      = models.BooleanField(default=True, verbose_name=_('Active'))
    class Meta:
        verbose_name = _('Unit of measure')
        verbose_name_plural = _('Units of measure')
    def __str__(self):
        return self.name + ' (' + self.description + ')'
    
