from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy as _
from djauth.forms import CoAdminAuthenticationForm


class CoAdminSite(AdminSite):
    login_form = CoAdminAuthenticationForm

    def get_urls(self):
        from django.conf.urls import url
        urls = super(CoAdminSite, self).get_urls()
        urls += [
            #url(r'^timelist_html/$', TimelistHTMLView.as_view()),
            #url(r'^timelist_html/(?P<project_id>[0-9]+)/$', TimelistHTMLView.as_view()),
            #PDF timelist URLs
            #url(r'^timelist_pdf/$', TimelistPDFView.as_view()),
            #url(r'^timelist_pdf/(?P<project_ids>[0-9]+)/(?P<date_from>\d{4}-\d{2}-\d{2})$', TimelistPDFView.as_view()),
            #url(r'^timelist_pdf/(?P<project_ids>[0-9]+)/(?P<date_to>\d{4}-\d{2}-\d{2})$', TimelistPDFView.as_view()),
            #url(r'^timelist_pdf/(?P<project_ids>[0-9]+)/(?P<date_from>\d{4}-\d{2}-\d{2})/(?P<date_to>\d{4}-\d{2}-\d{2})$', TimelistPDFView.as_view()),          
        ]
        return urls


def setup_admin_site():
    admin_site = CoAdminSite()
    return admin_site

admin_site = setup_admin_site()
