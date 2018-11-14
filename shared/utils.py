from datetime import datetime, time
from django.utils import timezone

def start_of_day(date_time: datetime):
    return datetime.combine(date_time.date(), time.min)

def end_of_day(date_time: datetime):
    return datetime.combine(date_time.date(), time.max)

def start_of_today():
    return start_of_day(timezone.now())

def end_of_today():
    return end_of_day(timezone.now())