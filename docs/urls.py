from django.conf.urls import url
from .views import change_password

#https://stackoverflow.com/questions/6779265/how-can-i-not-use-djangos-admin-login-view

urlpatterns = [
    url(r'^password/$', change_password, name='change_password'),
]
