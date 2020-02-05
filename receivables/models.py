from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.admin.models import LogEntry
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields import CharField, PositiveSmallIntegerField,\
    BooleanField, TextField
from django.db.models.deletion import PROTECT
from conf.settings import MAX_DIGITS_PRICE, MAX_DIGITS_QTY, DECIMAL_PLACES_PRICE, DECIMAL_PLACES_QTY,\
    MAX_DIGITS_CURRENCY, DECIMAL_PLACES_CURRENCY
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.fields.related import ManyToManyField

from salary.models import Employee
from shared.models import AddressMixin
from inventory.models import Item
from general.models import UnitOfMeasure, CoModel


COMPANY = 100
PERSON  = 200

CUSTOMER_TYPE_CHOICES = (
        (COMPANY, _('Company')),
        (PERSON, _('Person')),
    )

class Customer(AddressMixin, CoModel):
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
    web_site = models.CharField(max_length=250,
                                blank=True,
                                default='',
                                verbose_name=_('Web site')
                                )
    active = BooleanField(default=True,
                          verbose_name=_('Active')
                          )
    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        return self.name


class ProjectCategory(CoModel):
    name = CharField(max_length = 10, verbose_name = _('Name'))
    description = TextField(blank = True, default= '', verbose_name = _('Description'))

    class Meta:
        verbose_name = _('Project category')
        verbose_name_plural = _('Project categories')

    def __str__(self):
        return self.name


class Project(CoModel):
    name = CharField(max_length=100,
                     verbose_name=_('Name')
                     )
    description = TextField(blank=True,
                            default='',
                            verbose_name=_('Description')
                            )
    comment = TextField(blank=True,
                        default='',
                        verbose_name=_('Comment'),
                        )
    customer = models.ForeignKey(Customer,
                                 on_delete=PROTECT,
                                 related_name='projects',
                                 verbose_name=_('Customer')
                                 )

    category = models.ForeignKey(ProjectCategory,
                                 on_delete=PROTECT,
                                 blank=True,
                                 null = True,
                                 verbose_name = _('Category'),
                                 )

    active = BooleanField(default=True,
                          verbose_name=_('Active')
                          )
    visible = BooleanField(default=True,
                           verbose_name=_('Visible')
                           )
    employees = ManyToManyField(Employee,
                                through = 'RelatedEmployee',
                                related_name = 'projects',
                                verbose_name = _('Employees'),
                                )

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        #app_label = 'reports' Just make sure to adapt the FK and M2M fields accordingly.

    def __str__(self):
        return self.name


class SalesOrderHeader(CoModel):
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
                                           verbose_name=_('Description')
                                           )
    employees = ManyToManyField(Employee,
                                through = 'RelatedEmployee',
                                related_name = 'sales_orders',
                                verbose_name = _('Employees'),
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
    
    created_date_time.short_description = _('Created')
    
    def created_date_time_str(self):
        return self.created_date_time().strftime("%Y-%m-%d %H:%M")
        
    created_date_time_str.short_description = _('Created')
                                        
    def __str__(self):
        return self.created_date_time_str() + ' | ' + self.customer.name + ' - ' + self.project.name

    class Meta:
        verbose_name = _('Sales order')
        verbose_name_plural = _('Sales orders')
        ordering = ['-id']


class SalesOrderLine(CoModel):
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
        
    class Meta:
        verbose_name = _('Sales order line')
        verbose_name_plural = _('Sales order lines')


class RelatedEmployee(models.Model):
    project = models.ForeignKey(Project, on_delete=PROTECT, blank=True, null=True)
    sales_order_header = models.ForeignKey(SalesOrderHeader, on_delete=PROTECT, blank=True, null=True)
    employee = models.ForeignKey(Employee, on_delete=PROTECT)
    assigned = models.DateTimeField(auto_now=True)
    '''
    def save(self, *args, **kwargs):
        if self.sales_order_header:
            self.project = self.sales_order_header.project
        super(RelatedEmployee, self).save(*args, **kwargs)
    '''
    def __str__(self):
        return self.employee.full_name()

    class Meta:
        unique_together = (
            ('employee', 'sales_order_header'),
            ('employee', 'project'),
        )
        verbose_name = _('Related employee')
        verbose_name_plural = _('Related employees')
        managed = False # Disable migrations
        auto_created = True


class WorkTimeJournal(CoModel):
    content_type = models.ForeignKey(ContentType, 
                                     on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type',
                                       'object_id')
    employee = models.ForeignKey(Employee,
                                 on_delete = models.PROTECT,
                                 related_name = 'journal_lines',
                                 verbose_name = _('Employee'))
    item = models.ForeignKey(Item,
                             on_delete = PROTECT,
                             related_name = 'journal_lines',
                             verbose_name = _('Item')
                             )
    work_date = models.DateField(verbose_name = _('Date'))
    work_time_from = models.TimeField(verbose_name = _('From'))
    work_time_to = models.TimeField(verbose_name = _('To'))
    work_time = models.DecimalField(max_digits = 4,
                                    decimal_places = 2, 
                                    verbose_name = _('Work time')
                                    )
    overtime_50 = models.DecimalField(max_digits = 4,
                                     decimal_places = 2,
                                     blank = True,
                                     null = True,
                                     verbose_name = _('Overtime 50%')
                                     )
    overtime_100 = models.DecimalField(max_digits = 4,
                                       decimal_places = 2,
                                       blank = True,
                                       null = True,
                                       verbose_name = _('Overtime 100%')
                                       )
    distance = models.PositiveSmallIntegerField(blank = True,
                                                null = True,
                                                verbose_name = _('Distance')
                                                )
    toll_ring = models.DecimalField(max_digits = 7,
                                    decimal_places = 2,
                                    null = True,
                                    blank = True,
                                    verbose_name = _('Toll ring')
                                    )
    ferry = models.DecimalField(max_digits = 7,
                                decimal_places = 2,
                                null = True,
                                blank = True,
                                verbose_name = _('Ferry')
                                )
    diet = models.DecimalField(max_digits = 7, 
                                decimal_places = 2,
                                null = True,
                                blank = True, 
                                verbose_name = _('Diet')
                                )
    created_date_time = models.DateTimeField(
                             auto_now = True,
                             verbose_name = _('Created date/time')
                             )

    def clean(self):
        if self.calc_work_hours() == 0:
            raise ValidationError({'work_time_from': _('Working time cannot be zero.')})
        if datetime.combine(self.work_date,  self.work_time_to) < datetime.combine(self.work_date, self.work_time_from):
            raise ValidationError({'work_time_from': _('Start time cannot be later than the end time.')})
        overlap = self.time_overlap(self.id, self.employee_id, self.work_date, self.work_time_from, self.work_time_to)
        if overlap is not None:
            raise ValidationError({'work_time_from': _('Selected time is already used for the task [%(time_from)s-%(time_to)s %(job)s].') % \
                                    {'time_from': overlap.work_time_from.strftime('%H:%M'),
                                     'time_to': overlap.work_time_to.strftime('%H:%M'),
                                     'job': overlap.item,
                                    }
                                  },
                                )

    def time_overlap(self, rec_id, employee_id, date, time_from, time_to):
        dt_from_more = datetime.combine(date, time_from) + timedelta(microseconds=1)
        dt_to_less = datetime.combine(date, time_to) - timedelta(microseconds=1)
        overlaps = WorkTimeJournal.objects.filter(Q(employee_id = employee_id) & (
                                                  Q(work_date=date,
                                                    work_time_from__gt=dt_from_more.time(),
                                                    work_time_from__lt=dt_to_less.time()) |
                                                  Q(work_date=date,
                                                    work_time_from__lt=dt_from_more.time(),
                                                    work_time_to__gt=dt_from_more.time()
                                                    )
                                                  )
                                                  ).exclude(id=rec_id)
        if overlaps.count() == 0:
            return None
        else:
            return overlaps[0]

    def calc_work_hours(self):
        timediff = datetime.combine(self.work_date,  self.work_time_to) -\
                   datetime.combine(self.work_date, self.work_time_from)
        timediff_hours = timediff.total_seconds() / 3600
        return round(timediff_hours, 2)
                    
    def save(self, *args, **kwargs):
        self.work_time = self.calc_work_hours()
        super(WorkTimeJournal, self).save(*args, **kwargs)

    class Meta:
        verbose_name = ('Work time journal')
        verbose_name_plural = _('Work time journal')

