import logging
from io import BytesIO
from datetime import datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType
from django.core.checks.security.base import check_sts_include_subdomains


def uniq4list(seq):
    '''
    Uniquefies and converts a sequence to a list
    '''
    keys = {}
    for item in seq:
        keys[item] = 1
    return list(keys)

def str2bool(value):
    return value.lower() in ('true', 'yes', 't', 'y', '1')

def date2str(value):
    return value.strftime("%Y-%m-%d")

def start_of_day(date_time: datetime):
    return datetime.combine(date_time.date(), time.min)

def end_of_day(date_time: datetime):
    return datetime.combine(date_time.date(), time.max)

def start_of_today():
    return start_of_day(timezone.now())

def end_of_today():
    return end_of_day(timezone.now())

def start_of_month(date_time: datetime):
    return datetime(date_time.year, date_time.month, 1) 
    
def end_of_month(date_time: datetime):
    return date_time + relativedelta(day=31)

def start_of_current_month():
    return start_of_month(timezone.now())

def end_of_current_month():
    return end_of_month(timezone.now())

def get_contenttypes():
    content_types = ContentType.objects.all()
    return {(c.app_label, c.model): c.id for c in content_types}

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def write_log_message(user, text, view=None):
    db_logger = logging.getLogger('db')
    message = ''
    if user:
        message += 'USER: [' + str(user.id) + '] ' + user.first_name + ' ' + user.last_name + ' | \n '
    if view:
        message += 'VIEW: ['+ view + '] | \n '
    message += 'DATA: ' + text
    db_logger.info(message)

def field_exists(model, fieldname, include_hidden = True):
    for field in model._meta.get_fields(include_hidden):
        if field.name == fieldname:
            return True
    return False
