from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from general.models import CalendarHeader, CalendarLine, HOLIDAY, ILLNESS, ILLSELF, ABSENCE
from .models import Employee

class CalendarLineForm(forms.ModelForm):
    ''' Form Class for generic Calendar Entry '''
    ''' Meant to be derived by specific calendar entries, like HolidayLine, AbsenceLine, etc. '''

    ''' TODO: Patestuoti su kitomis kompanijomis '''
    ''' TODO: Perkelti į general.forms '''

    company = None
    id = None
    cal_type = None
    owner_type_id = None
    owner_id = None
    descr_placeholder = ''

    def __init__(self, data, instance=None, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        self.id = kwargs.pop('id', None)
        self.owner_type_id = kwargs.pop('owner_type', None)
        self.owner_id = kwargs.pop('owner', None)
        super(CalendarLineForm, self).__init__(data, instance=instance)
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 1, 'placeholder': _(self.descr_placeholder).capitalize})

    def _get_calendar_header(self):
        '''
        Retrieving relevand Calendar Header
        '''
        # Search for relevant calendar header
        cal_header = CalendarHeader.objects.filter(
            company=self.company,
            type=self.cal_type,
            owner_type = self.owner_type_id,
            owner_id = self.owner_id)

        # Create calendar header if not exists
        if cal_header:
            cal_header = cal_header[0]
        else:
            cal_header = CalendarHeader(
                company = self.company,
                type_id = self.cal_type,
                owner_type = self.owner_type_id,
                owner_id = self.owner_id,
                name = self.cal_type_verbose + '_' + str(self.owner_type_id.id) + '_' + str(self.owner_id)
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
        abstract = True
        model = CalendarLine
        fields = ['description',
                  'dtfr',
                  'dtto',
                  ]

        widgets = {
            'dtfr': forms.SelectDateWidget(years = range(2020, 2035)),
            'dtto': forms.SelectDateWidget(years = range(2020, 2035)),
        }


class HolidayLineForm(CalendarLineForm):
    '''
        Form for Holiday calendar entry
    '''
    cal_type = HOLIDAY
    cal_type_verbose = 'HOLIDAY'
    descr_placeholder = "holiday"

class IllnessLineForm(CalendarLineForm):
    '''
        Form for Doctor-declared illness calendar entry
    '''
    cal_type = ILLNESS
    cal_type_verbose = 'ILLNESS'
    descr_placeholder = "illness"

class IllselfLineForm(CalendarLineForm):
    '''
        Form for Self-declared illness calendar entry
    '''
    cal_type = ILLSELF
    cal_type_verbose = 'ILLSELF'
    descr_placeholder = "illness"

class AbsenceLineForm(CalendarLineForm):
    '''
        Form for Absence calendar entry
    '''
    cal_type = ABSENCE
    cal_type_verbose = 'ABSENCE'
    descr_placeholder = "absence"
