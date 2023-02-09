from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from general.models import CalendarHeader, CalendarLine, HOLIDAY
from .models import Employee

class CalendarLine(forms.ModelForm):
    ''' Class for general Calendar Entry '''
    ''' Meant to be derived by specific calendar entries, like HolidayLine, AbsenceLine, etc. '''

    ''' TODO: Patestuoti su kitomis kompanijomis '''

    company = None
    id = None
    calendar_type = None
    owner_type_id = None
    owner_id = None

    def __init__(self, data, instance=None, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        self.id = kwargs.pop('id', None)
        self.calendar_type = kwargs.pop('calendar_type', None)
        self.owner_type_id = kwargs.pop('owner_type_id', None)
        self.owner_id = kwargs.pop('owner_id', None)
        super(CalendarLine, self).__init__(data, instance=instance)

    def _get_calendar_header(self):
        '''
        Retrieving relevand Calendar Header
        '''
        # Search for relevant calendar header
        cal_header = CalendarHeader.objects.filter(
            company=self.company,
            type=self.calendar_type,
            owner_type = self.owner_type_id,
            owner_id = self.owner_id)

        # Create calendar header if not exists
        if cal_header:
            cal_header = cal_header[0]
        else:
            cal_header = CalendarHeader(
                company = self.company,
                type_id = HOLIDAY,
                owner_type = self.owner_type_id,
                owner_id = self.owner_id,
                name = 'HOLIDAY_' + str(self.owner_type_id.id) + '_' + str(self.owner_id)
            )
            cal_header.save()
        return cal_header

    def save(self, commit=True):
        '''
        Saving calendar line
        '''
        obj = super().save(commit=False)
        if commit:
            #create line afterwards
            obj.calendar = self._get_calendar_header()
            obj.save()
        return obj

    class Meta:
        model = CalendarLine
        fields = ['description',
                  'dtfr',
                  'dtto',
                  ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 1, 'placeholder': _("holiday").capitalize()}),
            'dtfr': forms.SelectDateWidget(years = range(2020, 2035)),
            'dtto': forms.SelectDateWidget(years = range(2020, 2035)),
        }

class HolidayLine(CalendarLine):
    '''
        Form for Holiday calendar entry
    '''
    def __init__(self, data, instance=None, *args, **kwargs):
        ''' Initializing Holiday Calendar - specific data '''
        kwargs['calendar_type'] = HOLIDAY
        owner_type = kwargs.pop('owner_type')
        # Avoid accessing database to get owner type if it is transferred from the caller
        if owner_type is None:
            kwargs['owner_type_id'] = ContentType.objects.get_for_model(Employee) # if value is not transferred then fallback to read from a database
        else:
            kwargs['owner_type_id'] = owner_type
        kwargs['owner_id'] = kwargs.pop('employee')
        super().__init__(data, instance=instance, *args, **kwargs)
