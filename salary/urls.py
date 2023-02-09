from django.conf.urls import url
from .views import EmployeeView, HolidayView

urlpatterns = [
    url('$', EmployeeView.as_view(), name='employees'),
    url('holidays$', HolidayView.as_view(), name='empl_holidays'),
    url('holidays/(?P<employee>[0-9]+)$', HolidayView.as_view(), name='empl_holidays'),
    url('holidays/(?P<employee>[0-9]+)/(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})$', HolidayView.as_view(), name='empl_holidays'),
]