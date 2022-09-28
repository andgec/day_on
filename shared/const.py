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
    (JANUARY,   _('January')),
    (FEBRUARY,  _('February')),
    (MARCH,     _('March')),
    (APRIL,     _('April')),
    (MAY,       _('May')),
    (JUNE,      _('June')),
    (JULY,      _('July')),
    (AUGUST,    _('August')),
    (SEPTEMBER, _('September')),
    (OCTOBER,   _('October')),
    (NOVEMBER,  _('November')),
    (DECEMBER,  _('December')),
)

# ---------------------
# Company configuration
# ---------------------

# Configuration variable types
BOOLEAN     = 0
INTEGER     = 1
DECIMAL     = 3
STRING      = 4
OPTION      = 5
MULTIPLE    = 6

VARIABLE_TYPE_CHOICES = (
    (BOOLEAN, 'Boolean'),
    (INTEGER, 'Integer'),
    (DECIMAL, 'Decimal'),
    (STRING, 'String'),
    (OPTION, 'Option'),
    (MULTIPLE, 'Multiple options'),
)

# View actions

VIEW = 0
EDIT = 1
DELETE = 2
