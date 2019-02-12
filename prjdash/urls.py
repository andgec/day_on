from django.conf.urls import url
from .views import ProjectDashboardView


urlpatterns = [
    url('', ProjectDashboardView.as_view(), name='pdash')
]