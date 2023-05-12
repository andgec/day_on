from django.conf.urls import url
from .views import EmployeeView, HolidayView, IllnessView, IllselfView, AbsenceView

urlpatterns = [
    url('$', EmployeeView.as_view(), name='employees'),
    url('holidays$', HolidayView.as_view(), name='empl_holidays'),
    url('holidays/(?P<employee>[0-9]+)$', HolidayView.as_view(), name='empl_holidays'),
    url('holidays/(?P<employee>[0-9]+)/(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})$', HolidayView.as_view(), name='empl_holidays'),
    url('illness$', IllnessView.as_view(), name='empl_illness'),
    url('illness/(?P<employee>[0-9]+)$', IllnessView.as_view(), name='empl_illness'),
    url('illness/(?P<employee>[0-9]+)/(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})$', IllnessView.as_view(), name='empl_illness'),
    url('illself$', IllselfView.as_view(), name='empl_illself'),
    url('illself/(?P<employee>[0-9]+)$', IllselfView.as_view(), name='empl_illself'),
    url('illself/(?P<employee>[0-9]+)/(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})$', IllselfView.as_view(), name='empl_illness'),
    url('absence$', AbsenceView.as_view(), name='empl_absence'),
    url('absence/(?P<employee>[0-9]+)$', AbsenceView.as_view(), name='empl_absence'),
    url('absence/(?P<employee>[0-9]+)/(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})$', AbsenceView.as_view(), name='empl_absence'),

]
