from django.db import models
from django.contrib.admin.models import LogEntry
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import CharField, PositiveSmallIntegerField,\
    BooleanField, DateTimeField, TextField
from general.models import Address, Contact
from django.db.models.deletion import PROTECT
from djauth.models import User
from inventory.models import Item
from general.models import UnitOfMeasure
from conf.settings import MAX_DIGITS_PRICE, MAX_DIGITS_QTY, DECIMAL_PLACES_PRICE, DECIMAL_PLACES_QTY,\
    MAX_DIGITS_CURRENCY, DECIMAL_PLACES_CURRENCY
from shared.models import AddressMixin
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from salary.models import Employee
from django.core.validators import MaxLengthValidator

COMPANY = 100
PERSON  = 200

CUSTOMER_TYPE_CHOICES = (
        (COMPANY, _('Company')),
        (PERSON, _('Person')),
    )

class Customer(AddressMixin, models.Model):
    number = CharField(max_length=32,
                       unique=True,
                       verbose_name=_('Number')
                       )
    name = CharField(max_length=128,
                     verbose_name=_('Name')
                     )
    type = PositiveSmallIntegerField(choices=CUSTOMER_TYPE_CHOICES,
                                     default=COMPANY,
                                     verbose_name=_('Type')
                                     )
    '''
    address = models.ForeignKey(Address,
                                blank=True,
                                null=True,
                                on_delete=PROTECT,
                                related_name='customer',
                                verbose_name=_('Address'))
    '''                                
    web_site = models.CharField(max_length=250,
                                blank=True,
                                default='',
                                verbose_name=_('Web site')
                                )
    '''
    shipping_address = models.ForeignKey(Address,
                                         blank=True,
                                         null=True,
                                         on_delete=PROTECT,
                                         related_name='customer_ship',
                                         verbose_name=_('Shipping address')
                                         )
    billing_address = models.ForeignKey(Address,
                                        blank=True,
                                        null=True,
                                        on_delete=PROTECT,
                                        related_name='customer_bill',
                                        verbose_name=_('Billing address')
                                        )
    '''                                        
    active = BooleanField(default=True,
                          verbose_name=_('Active')
                          )
    
    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    
    def __str__(self):
        return self.number + ' - ' + self.name


class Project(models.Model):
    name = CharField(max_length=60,
                     verbose_name=_('Name')
                     )
    description = TextField(blank=True,
                            default='',
                            verbose_name=_('Description')
                            )
    customer = models.ForeignKey(Customer,
                                 on_delete=PROTECT,
                                 related_name='projects',
                                 verbose_name=_('Customer')
                                 )
    active = BooleanField(default=True,
                          verbose_name=_('Active')
                          )
    '''
    created_date_time   = models.DateTimeField(auto_now=True,
                                               verbose_name=_('Created date/time')
                                               )
    created_by          = models.ForeignKey(User,
                                            blank = True,
                                            on_delete=PROTECT,
                                            related_name='projects',
                                            verbose_name=_('Created by')
                                            )
    '''
    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
    
    def __str__(self):
        return self.name


class SalesOrderHeader(models.Model):
    customer            = models.ForeignKey(Customer,
                                            on_delete=PROTECT,
                                            related_name='sales_orders',
                                            verbose_name=_('Customer')
                                            )
    project             = models.ForeignKey(Project,
                                            blank=True,
                                            null=True,
                                            on_delete=PROTECT,
                                            related_name='sales_orders',
                                            verbose_name=_('Project')
                                            )
    description         = models.CharField(max_length = 120,
                                           blank=True,
                                           default = '',
                                           )
    estimated_amount    = models.DecimalField(max_digits=MAX_DIGITS_CURRENCY,
                                              decimal_places=DECIMAL_PLACES_CURRENCY,
                                              blank=True,
                                              null=True,
                                              verbose_name=_('Estimated amount')
                                              )
    discount_amount     = models.DecimalField(max_digits=MAX_DIGITS_CURRENCY,
                                              decimal_places=DECIMAL_PLACES_CURRENCY,
                                              blank=True,
                                              null=True,
                                              verbose_name=_('Discount amount')
                                              )
    discount_percent    = models.DecimalField(max_digits=3,
                                              decimal_places=0,
                                              blank=True,
                                              null=True,
                                              verbose_name=_('Discount percent')
                                              )

    def created_date_time(self):
        'Returns date and time when the sales order was created'
        log_entry = LogEntry.objects.get(content_type__model='salesorderheader', action_flag=1, object_id=self.id)
        return log_entry.action_time
    
    created_date_time.short_description = _('Created date / time')
    
    def created_date_time_str(self):
        return self.created_date_time().strftime("%Y-%m-%d %H:%M")
        
    created_date_time_str.short_description = _('Created date / time')
    
        
        

    '''    
    created_date_time   = models.DateTimeField(auto_now=True,
                                               verbose_name=_('Created date/time')
                                               )
    created_by          = models.ForeignKey(User, 
                                            blank=True, 
                                            on_delete=PROTECT,
                                            related_name='sales_orders',
                                            verbose_name=_('Created by')
                                            )
    last_modified_date_time = models.DateTimeField(auto_now=True,
                                                   verbose_name=_('Last modified date/time')
                                                   )
    last_modified_by    = models.ForeignKey(User,
                                            blank=True,
                                            on_delete=PROTECT,
                                            related_name='sales_orders_modified_by',
                                            verbose_name=_('Last modified by'))
    str(self.created_date_time).strftime("%Y-%m-%d %H:%M")
    '''        
                                        
    def __str__(self):
        return self.created_date_time_str() + ' | ' + self.customer.name + ' - ' + self.project.name

    class Meta:
        verbose_name = _('Sales order')
        verbose_name_plural = _('Sales orders')
        ordering = ['-id']


class SalesOrderLine(models.Model):
    sales_order_header  = models.ForeignKey(SalesOrderHeader, 
                                            on_delete=PROTECT,
                                            related_name='lines',
                                            verbose_name=_('Order')
                                            )
    item                = models.ForeignKey(Item, 
                                            on_delete=PROTECT,
                                            related_name='sales_order_lines',
                                            verbose_name=_('Item')
                                            )
    quantity            = models.DecimalField(max_digits=MAX_DIGITS_QTY, 
                                              decimal_places=DECIMAL_PLACES_QTY,
                                              verbose_name=_('Quantity')
                                              )
    unit_of_measure     = models.ForeignKey(UnitOfMeasure, 
                                            on_delete=PROTECT,
                                            related_name='sales_order_lines',
                                            verbose_name=_('Unit of measure')
                                            )
    price               = models.DecimalField(max_digits=MAX_DIGITS_PRICE,
                                              decimal_places=DECIMAL_PLACES_PRICE,
                                              blank=True,
                                              null=True,
                                              verbose_name=_('Price')
                                              )
    amount              = models.DecimalField(max_digits=MAX_DIGITS_CURRENCY,
                                              decimal_places=DECIMAL_PLACES_CURRENCY,
                                              blank=True,
                                              null=True,
                                              verbose_name=('Amount')
                                              )
    discount_amount     = models.DecimalField(max_digits=MAX_DIGITS_CURRENCY,
                                              decimal_places=DECIMAL_PLACES_CURRENCY,
                                              blank=True,
                                              null=True,
                                              verbose_name=('Discount amount')
                                              )
    discount_percent    = models.DecimalField(max_digits=MAX_DIGITS_CURRENCY,
                                              decimal_places=DECIMAL_PLACES_CURRENCY,
                                              blank=True,
                                              null=True,
                                              verbose_name=('Discount percent')
                                              )
    line_amount         = models.DecimalField(max_digits=MAX_DIGITS_CURRENCY,
                                              decimal_places=DECIMAL_PLACES_CURRENCY,
                                              blank=True,
                                              null=True,
                                              verbose_name=('Line amount')
                                              )
        
    '''
    created_date_time   = models.DateTimeField(auto_now=True,
                                               verbose_name=_('Created date/time')
                                               )
    created_by          = models.ForeignKey(User, #Todo: remove created by and created date/time fields as there is history system
                                            blank=True,
                                            null=True,
                                            on_delete=PROTECT,
                                            related_name='sales_order_lines',
                                            verbose_name=_('Created by')
                                            )
    '''    
        
    class Meta:
        verbose_name = _('Sales order line')
        verbose_name_plural = _('Sales order lines')


class WorkTimeJournal(models.Model):
    employee_id = models.ForeignKey(Employee, on_delete=PROTECT)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_date_time = models.DateTimeField(auto_now=True,
                                             verbose_name = _('Created date/time')
                                             )
    
    class Meta:
        verbose_name = ('Work time journal')
        verbose_name_plural = _('Work time journal')
    
