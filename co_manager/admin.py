from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy as _
from reports.views import TimelistPDFView, TimelistHTMLView
from django.contrib.auth.admin import GroupAdmin
from django.apps import apps


class CoAdminSite(AdminSite):

    def get_urls(self):
        from django.conf.urls import url
        urls = super(CoAdminSite, self).get_urls()
        urls += [
            url(r'^timelist_pdf/$', TimelistPDFView.as_view()),
            url(r'^timelist_html/$', TimelistHTMLView.as_view()),
        ]
        return urls

def get_site_header():
#    if DEBUG:
#       return _('Marketwell administration') + ' (' + RUNTIME_ENV + ')'
#    else:
    return _('Company administration')


def setup_admin_site():
    admin_site = CoAdminSite()
    
    # Text to put at the end of each page's <title>.
    admin_site.site_title = _('Company site admin')

    # Text to put in each page's <h1> (and above login form).
    admin_site.site_header = get_site_header()

    # Text to put at the top of the admin index page.
    admin_site.index_title = _('Site administration')

    return admin_site

admin_site = setup_admin_site()

Group = apps.get_model('auth.Group')
Group._meta.app_label = 'djauth'
admin_site.register(Group, GroupAdmin)