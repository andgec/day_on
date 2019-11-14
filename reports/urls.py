from django.conf.urls import url
from .views import TimeSummaryHTMLView, TimeSummaryPostedLineDetailView

urlpatterns = [
    url('time-summary/details$', TimeSummaryPostedLineDetailView.as_view(), name='report-time-summary-details'),
    url('time-summary/details/(?P<employee>[0-9]+)/(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})$',
        TimeSummaryPostedLineDetailView.as_view(),
        name='report-time-summary-details'
        ),
    url('time-summary$', TimeSummaryHTMLView.as_view(), name='report-time-summary'),
]