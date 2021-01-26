'''
    Project URLS
'''

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.urls import include

from rest_framework_jwt.views import obtain_jwt_token

from conf import settings

from djauth      import urls as djauth_urls
from prjdash     import urls as prjdash_urls
from reports     import urls as reports_urls
from receivables import urls as receivb_urls
from receivables.views import WorkTimeJournalView_V2


from .admin import admin_site

urlpatterns = i18n_patterns(
    url(r'^$', WorkTimeJournalView_V2.as_view(), name='index'),
    url(r'^accounts/', include(djauth_urls.urlpatterns)),
    url(r'^v1/', include(receivb_urls.urlpatterns_v1)),
    url(r'^v2/', include(receivb_urls.urlpatterns_v2)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^admin/', admin_site.urls, name='admin'),
    url(r'^v1/pdash/', include(prjdash_urls.urlpatterns)),
    url(r'^reports/', include(reports_urls.urlpatterns)),
    url(r'^api/auth/token', obtain_jwt_token),
    prefix_default_language=False
)

#https://stackoverflow.com/questions/6779265/how-can-i-not-use-djangos-admin-login-view
admin.autodiscover()
#admin.site.login = login_required(admin.site.login)
admin.site.login = login_required(login_url='/accounts/login/')

if settings.LOCAL_ENV and settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
