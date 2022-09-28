from django.conf.urls import url
from .views import EmployeeView

urlpatterns = [
    url('$', EmployeeView.as_view(), name='employees'),
]