from django.utils.translation import ugettext_lazy as _

def get_site_header():
#    if DEBUG:
#       return _('Marketwell administration') + ' (' + RUNTIME_ENV + ')'
#    else:
    return _('Company administration')

def setup_admin_site(admin_site):
    # Text to put at the end of each page's <title>.
    admin_site.site_title = _('Company site admin')

    # Text to put in each page's <h1> (and above login form).
    admin_site.site_header = get_site_header()

    # Text to put at the top of the admin index page.
    admin_site.index_title = _('Site administration')
