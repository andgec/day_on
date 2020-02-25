from django.conf.urls import url
from .views import CoLoginView


urlpatterns = [
    url('login/', CoLoginView.as_view(), name='login'),
]
