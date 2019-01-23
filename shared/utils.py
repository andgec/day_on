from io import BytesIO
from datetime import datetime, time
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import get_template
#from xhtml2pdf import pisa

def start_of_day(date_time: datetime):
    return datetime.combine(date_time.date(), time.min)

def end_of_day(date_time: datetime):
    return datetime.combine(date_time.date(), time.max)

def start_of_today():
    return start_of_day(timezone.now())

def end_of_today():
    return end_of_day(timezone.now())

'''
def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
'''