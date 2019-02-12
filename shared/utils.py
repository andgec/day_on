from io import BytesIO
from datetime import datetime, time
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType
#from xhtml2pdf import pisa

def start_of_day(date_time: datetime):
    return datetime.combine(date_time.date(), time.min)

def end_of_day(date_time: datetime):
    return datetime.combine(date_time.date(), time.max)

def start_of_today():
    return start_of_day(timezone.now())

def end_of_today():
    return end_of_day(timezone.now())

def read_contenttypes():
    content_types = ContentType.objects.all()
    return {(c.app_label, c.model): c.id for c in content_types}

content_type_id_by_name = read_contenttypes()

