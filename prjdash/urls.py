from django.conf.urls import url
from .views import ProjectDashboardView


urlpatterns = [
    url('(?P<pk>[0-9]+)$', ProjectDashboardView.as_view(), name='pdash'),
    url('', ProjectDashboardView.as_view(), name='pdash'),    
]