from django.conf.urls import url
from .views import ProjectDashboardView, ProjectDashboardAssignEmployeesView, ProjectDashboardPostedTimeReview
from reports.views import TimelistPDFView

urlpatterns = [
    url('(?P<location>desktop|archive)/(?P<pk>[0-9]+)/assign-employees$', ProjectDashboardAssignEmployeesView.as_view(), name='pdash-assign-employees'),
    url('(?P<location>desktop|archive)/(?P<project_id>[0-9]+)/time-review$', ProjectDashboardPostedTimeReview.as_view(), name='pdash-time-review'),
    url('(?P<location>desktop|archive)/(?P<project_id>[0-9]+)/time-review/(?P<pk>[0-9]+)$', ProjectDashboardPostedTimeReview.as_view(), name='pdash-time-review'),
    url('(?P<location>desktop|archive)/(?P<project_id>[0-9]+)/time-review/(?P<pk>[0-9]+)/(?P<mode>edit|delete)$', ProjectDashboardPostedTimeReview.as_view(), name='pdash-time-review'),
    url('(?P<pk>[0-9]+)/timelist_pdf$', TimelistPDFView.as_view(), name='timelist-pdf'),
    # url('(?P<pk>[0-9]+)/(?P<mode>edit)$', ProjectDashboardView.as_view(), name='pdash'),
    url('(?P<location>desktop|archive)/(?P<pk>[0-9]+)/(?P<mode>edit)$', ProjectDashboardView.as_view(), name='pdash'),
    url('(?P<location>desktop|archive)/(?P<pk>[0-9]+)$', ProjectDashboardView.as_view(), name='pdash'),
    url('(?P<location>desktop|archive)$', ProjectDashboardView.as_view(), name='pdash'),
    # url('(?P<pk>[0-9]+)$', ProjectDashboardView.as_view(), name='pdash'),
    url('', ProjectDashboardView.as_view(), name='pdash'),
]