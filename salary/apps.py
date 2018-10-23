from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SalaryConfig(AppConfig):
    name = 'salary'
    verbose_name = _('Salary')