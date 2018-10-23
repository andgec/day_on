from django.db import models
from django.db.models.fields.related import OneToOneField
from django.db.models.deletion import CASCADE
from django.utils.translation import ugettext_lazy as _

from djauth.models import User
from shared.models import AddressMixin

class Employee(AddressMixin, models.Model):
    user        = OneToOneField(User, primary_key=True, related_name='employee', on_delete=CASCADE)
    phone_no    = models.CharField(max_length=20, blank=True, default='')
    mobile_no   = models.CharField(max_length=20, blank=True, default='')
    
    def full_name(self):
        return self.user.get_full_name()
    full_name.short_description = _('Full name')
    
    def email(self):
        return self.user.email
    email.short_description = _('Email')
    
    def is_active(self):
        return self.user.is_active
    is_active.boolean = True
    is_active.short_description = _('Active')
    
    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
    
    def __str__(self):
        return self.user.get_full_name()
