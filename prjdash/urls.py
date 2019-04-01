from django.conf.urls import url
from .views import ProjectDashboardView, ProjectDashboardAssignEmployeesView


urlpatterns = [
    url('(?P<pk>[0-9]+)/assign-employees$', ProjectDashboardAssignEmployeesView.as_view(), name='pdash-assign-employees'),
    url('(?P<pk>[0-9]+)/(?P<mode>edit)$', ProjectDashboardView.as_view(), name='pdash'),
    url('(?P<pk>[0-9]+)$', ProjectDashboardView.as_view(), name='pdash'),
    url('', ProjectDashboardView.as_view(), name='pdash'),
]