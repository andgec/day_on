from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SalaryConfig(AppConfig):
    name = 'reports'
    verbose_name = _('Reports')