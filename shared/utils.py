import os
import base64
import logging
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify


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

def none2zero(value):
    return 0 if value is None else value

def zero2none(value):
    return None if value is 0 else value

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


def imagefield_as_base64(image_field):
    if not image_field:
        return ''

    path_parts = str(image_field).split('.')
    file_format = path_parts[len(path_parts) - 1]
    encoded_string = base64.b64encode(image_field.read())

    return 'data:image/%(format)s;base64,%(encoded_string)s' % {'format': file_format, 'encoded_string': encoded_string.decode('utf-8')}


def get_image_path(instance, filename):
    ## split the file along the dots
    file_split = filename.split('.')

    ## find the file type
    file_type = file_split[-1]

    ## slugify the filename and put it together with the file_type
    ## slugfiy removes dots, hence why we do it this way
    filename = slugify(''.join(file_split[:-1])) + '.' + file_type

    ## return a path to the new file
    return os.path.join('pictures', instance.images_subdir, filename)

def qstring_add_param(qstring, param, value, default_value = None):
    '''
        Painless building of HTML query string.
        Adds one parameter with value to the HTML query string [qstring].
        Parameters with empty values are not added to the string.
        Skipping parameters with default value.
        Pass "&" for qstring if you want start with "&" instead of "?"
        For example, return string could be [?customer=321&status=active].
    '''
    if param is not None and str(param) != '' and value is not None and str(value) != '' and str(value) != str(default_value):
        if qstring is None or str(qstring) == '':
            qstring = '?'
        else:
            if qstring == '&':
                qstring = ''
            qstring = qstring + '&'
        return qstring + param + '=' + str(value)
    else:
        if qstring == '&':
            qstring = ''
        return qstring if qstring is not None else '' # return original qstring or initialize to empty string if qstring was None.

def add_unique_substr(rstr, substr, separator):
    '''
        Adding substring to a string if it does not exists within a string.
    '''
    if rstr is None or rstr == '':
        rstr = ''

    if substr not in rstr:
        if len(rstr) > 0:
            rstr = rstr + separator + substr
        else:
            rstr = substr
    return rstr

def add_css_class(class_list, new_class):
    '''
        Adds css class to a class_list variable of type string. 
        Only class names that does not exist in the class_list string (unique) are added
    '''
    return add_unique_substr(class_list, new_class, ' ')
