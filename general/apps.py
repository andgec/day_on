from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GeneralConfig(AppConfig):
    name = 'general'
    verbose_name = _('General')