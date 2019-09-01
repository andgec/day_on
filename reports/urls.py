from django.conf.urls import url
from .views import TimeSummaryXLSXView

urlpatterns = [
    url('time-summary', TimeSummaryXLSXView.as_view(), name='report-time-summary'),
]