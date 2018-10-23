from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DJAuthConfig(AppConfig):
    name = 'djauth'
    verbose_name = _('Authenticaion and authorization')