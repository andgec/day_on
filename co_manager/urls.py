"""co_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
#from django.urls import path
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.urls import include
from .admin import setup_admin_site
from conf import settings
from . import views
from receivables.wiews import WorkTimeJournalView

setup_admin_site(admin.site)

urlpatterns = i18n_patterns(
    url(r'^$', views.index, name='index'),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^receivables/tjournal/(?P<project_id>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})$', WorkTimeJournalView.as_view(), name='tjournal'),
    url(r'^receivables/tjournal/(?P<project_id>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})/(?P<modify_id>[0-9]+)$', WorkTimeJournalView.as_view(), name='tjournal'),
    prefix_default_language=False
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
