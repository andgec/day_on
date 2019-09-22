from django.conf.urls import url
from .views import WorkTimeJournalView, work_time_journal_proj_list_view, WorkTimeJournalView_V2

urlpatterns_v1 = [
    url('tjournal$', work_time_journal_proj_list_view, name='tjournal'),
    url('tjournal/(?P<project_id>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})$', WorkTimeJournalView.as_view(), name='tjournal'),
    url('tjournal/(?P<project_id>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})/(?P<jrline_id>[0-9]+)$', WorkTimeJournalView.as_view(), name='tjournal'),
    url('tjournal/(?P<project_id>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})/(?P<jrline_id>[0-9]+)/(?P<action>edit|delete+)$', WorkTimeJournalView.as_view(), name='tjournal'),
]

urlpatterns_v2 = [
    url('tjournal$', WorkTimeJournalView_V2.as_view(), name='tjr-v2'),
    url('tjournal/(?P<date>\d{4}-\d{2}-\d{2})$', WorkTimeJournalView_V2.as_view(), name='tjr-v2'),
    url('tjournal/(?P<date>\d{4}-\d{2}-\d{2})/(?P<jrline_id>[0-9]+)$', WorkTimeJournalView_V2.as_view(), name='tjr-v2'),
    url('tjournal/(?P<date>\d{4}-\d{2}-\d{2})/(?P<jrline_id>[0-9]+)/(?P<action>edit|delete+)$', WorkTimeJournalView_V2.as_view(), name='tjr-v2'),
]