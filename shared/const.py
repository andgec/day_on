from django.utils.translation import ugettext_lazy as _

# Common constants

JANUARY     = 1
FEBRUARY    = 2
MARCH       = 3
APRIL       = 4
MAY         = 5
JUNE        = 6
JULY        = 7
AUGUST      = 8
SEPTEMBER   = 9
OCTOBER     = 10
NOVEMBER    = 11
DECEMBER    = 12

MONTH_CHOICES = (
    (JANUARY,   _('Sausis')),
    (FEBRUARY,  _('Vasaris')),
    (MARCH,     _('Kovas')),
    (APRIL,     _('Balandis')),
    (MAY,       _('Gegužė')),
    (JUNE,      _('Birželis')),
    (JULY,      _('Liepa')),
    (AUGUST,    _('Rugpjūtis')),
    (SEPTEMBER, _('Rugsėjis')),
    (OCTOBER,   _('Spalis')),
    (NOVEMBER,  _('Lapkritis')),
    (DECEMBER,  _('Gruodis')),
)
