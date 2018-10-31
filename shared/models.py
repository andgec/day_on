from django.db import models
from django_countries.fields import CountryField
from django.utils.translation import ugettext_lazy as _


class AddressMixin(models.Model):
    '''
    A mixin class that adds address information fields and methods
    '''
    address     = models.CharField(max_length=100,
                                   blank=True,
                                   null=True,
                                   verbose_name=_('Street address'),
                                   )
    address2    = models.CharField(max_length=100,
                                   blank=True,
                                   null=True,
                                   verbose_name=_('Street address 2'),
                                   )
    city        = models.CharField(max_length=60,
                                   blank=True,
                                   null=True,
                                   verbose_name=_('City'),
                                   )
    post_code   = models.CharField(max_length=16,
                                   blank=True,
                                   default='',
                                   verbose_name=_('Post code'),
                                   )
    country     = CountryField(blank_label=_('(select country)'),
                               blank=True,
                               verbose_name=_('Country')
                               )

    def full_address(self):
        return (self.address + ', ' if self.address is not None else '') +\
               (self.post_code + ' ' if self.post_code is not None else '') +\
               (self.city + ' ' if self.city is not None else '')

    full_address.short_description = _('Full address')
    
    class Meta:
        abstract = True


class ContactMixin(models.Model):
    '''
    A mixin class that adds contact information fields and methods
    '''
    email           = models.EmailField(max_length=120,
                                        blank=True,
                                        default='',
                                        verbose_name=_('Email')
                                        )
    phone_no        = models.CharField(max_length=20,
                                       blank=True,
                                       default='',
                                       verbose_name=_('Phone No.')
                                       )
    mobile_no       = models.CharField(max_length=20,
                                       blank=True,
                                       default='',
                                       verbose_name=_('Mobile No.')
                                       )
    fax_no          = models.CharField(max_length=20,
                                       blank=True,
                                       default='',
                                       verbose_name=_('Fax No.')
                                       )
    class Meta:
        abstract = True
        
